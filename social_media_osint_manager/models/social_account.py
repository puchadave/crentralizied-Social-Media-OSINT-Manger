from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SocialMediaAccount(models.Model):
    _name = "social.media.account"
    _description = "Social Media Account"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    platform = fields.Selection(
        selection=[
            ("twitter", "X / Twitter"),
            ("facebook", "Facebook"),
            ("instagram", "Instagram"),
            ("linkedin", "LinkedIn"),
            ("youtube", "YouTube"),
            ("tiktok", "TikTok"),
            ("mastodon", "Mastodon"),
            ("threads", "Threads"),
            ("reddit", "Reddit"),
            ("other", "Other"),
        ],
        string="Platform",
        default="twitter",
        required=True,
        tracking=True,
    )
    account_identifier = fields.Char(
        string="Handle / ID",
        tracking=True,
        help="Handle, page name or API identifier used for external integrations.",
    )
    access_token = fields.Char(groups="base.group_system", string="Access Token")
    refresh_token = fields.Char(groups="base.group_system", string="Refresh Token")
    webhook_secret = fields.Char(groups="base.group_system", string="Webhook Secret")
    is_active = fields.Boolean(default=True, tracking=True)
    description = fields.Text()
    timezone = fields.Selection(
        selection=lambda self: self.env["res.partner"]._fields["tz"].selection,
        string="Time Zone",
        help="Default timezone that will be applied when scheduling content.",
    )
    default_post_time = fields.Float(
        string="Preferred Post Hour",
        help="Hour of day (0-23) that will be used when suggesting publishing windows.",
    )
    posts_ids = fields.One2many("social.media.post", "account_id", string="Posts")
    posts_count = fields.Integer(compute="_compute_posts_count", store=False)
    scheduled_posts_count = fields.Integer(
        compute="_compute_posts_count", store=False
    )
    follower_count = fields.Integer(string="Followers", tracking=True)
    following_count = fields.Integer(string="Following", tracking=True)
    engagement_rate = fields.Float(
        compute="_compute_engagement_rate",
        store=True,
        string="Engagement %",
        digits=(6, 2),
    )
    last_synced_at = fields.Datetime(string="Last Sync")
    incoming_webhook_url = fields.Char(string="Webhook URL", copy=False)
    team_ids = fields.Many2many(
        "res.users",
        string="Team",
        help="Users allowed to collaborate on this social account.",
    )
    color = fields.Integer()
    osint_snapshot_ids = fields.One2many(
        "social.media.osint",
        "account_id",
        string="OSINT Snapshots",
    )
    osint_last_snapshot = fields.Datetime(string="Last OSINT Snapshot")

    _sql_constraints = [
        ("account_platform_identifier_unique", "unique(platform, account_identifier)", "Each handle can only be linked once per platform."),
    ]

    @api.constrains("default_post_time")
    def _check_default_post_time(self):
        for account in self:
            if account.default_post_time and not (0.0 <= account.default_post_time < 24.0):
                raise ValidationError(
                    _("Preferred post hour must be a number between 0 and 23.99."),
                )

    def _compute_posts_count(self):
        grouped = self.env["social.media.post"].read_group(
            [("account_id", "in", self.ids)],
            ["account_id", "id:count", "state"],
            ["account_id", "state"],
        )
        mapping = {account_id: {"total": 0, "scheduled": 0} for account_id in self.ids}
        for data in grouped:
            account_id = data.get("account_id") and data["account_id"][0]
            if not account_id:
                continue
            mapping.setdefault(account_id, {"total": 0, "scheduled": 0})
            mapping[account_id]["total"] += data.get("id_count", 0)
            if data.get("state") in {"draft", "scheduled"}:
                mapping[account_id]["scheduled"] += data.get("id_count", 0)
        for account in self:
            account.posts_count = mapping.get(account.id, {}).get("total", 0)
            account.scheduled_posts_count = mapping.get(account.id, {}).get("scheduled", 0)

    def _compute_engagement_rate(self):
        for account in self:
            posts = account.posts_ids.filtered(lambda post: post.engagement_reach > 0)
            if not posts:
                account.engagement_rate = 0.0
                continue
            total_engagement = sum(posts.mapped("engagement_score"))
            total_reach = sum(posts.mapped("engagement_reach"))
            account.engagement_rate = (total_engagement / total_reach) * 100 if total_reach else 0.0

    def action_refresh_metrics(self):
        self.ensure_one()
        self.message_post(body=_("Manual sync triggered for the account."))
        self.last_synced_at = fields.Datetime.now()
        for post in self.posts_ids:
            post.action_refresh_metrics()
        return True

    def action_fetch_osint_data(self):
        """Entry point to fetch OSINT data for each social account.

        In a production system this method would call dedicated OSINT providers
        or internal services. Here it simply proxies the call to the analytics
        model in charge of storing snapshots.
        """

        for account in self:
            self.env["social.media.osint"].with_context(active_test=False).create_from_account(account)
        return True

    def _cron_refresh_accounts(self):
        active_accounts = self.search([("is_active", "=", True)])
        for account in active_accounts:
            account.action_refresh_metrics()
            account.action_fetch_osint_data()
        return True
