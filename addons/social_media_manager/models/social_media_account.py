from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SocialMediaAccount(models.Model):
    """Stores credentials and automation preferences for each social network."""

    _name = "social.media.account"
    _description = "Social Media Account"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    platform = fields.Selection(
        selection=[
            ("facebook", "Facebook"),
            ("instagram", "Instagram"),
            ("twitter", "Twitter / X"),
            ("linkedin", "LinkedIn"),
            ("youtube", "YouTube"),
            ("tiktok", "TikTok"),
        ],
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    active = fields.Boolean(default=True)
    access_token = fields.Char(groups="base.group_system")
    refresh_token = fields.Char(groups="base.group_system")
    token_expiration = fields.Datetime(groups="base.group_system")
    api_key = fields.Char(string="API Key", groups="base.group_system")
    api_secret = fields.Char(string="API Secret", groups="base.group_system")
    last_sync_date = fields.Datetime(readonly=True, tracking=True)
    follower_count = fields.Integer(tracking=True)
    engagement_rate = fields.Float(tracking=True, digits=(16, 4))
    remark = fields.Text()
    post_ids = fields.One2many("social.media.post", "account_id")
    metric_ids = fields.One2many("social.media.metric", "account_id")
    prompt_template_id = fields.Many2one(
        "social.media.prompt",
        string="Default Prompt",
        help="Default prompt configuration for AI assisted content generation.",
    )

    def _get_service(self):
        return self.env["social.api.client"].with_context(company_id=self.company_id.id)

    def action_refresh_token(self):
        for account in self:
            service = account._get_service()
            new_tokens = service.refresh_token(account)
            if not new_tokens:
                raise UserError(
                    _("The selected platform does not support token refresh or the refresh failed."),
                )
            access_token, refresh_token, expires_in = new_tokens
            account.write(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token or account.refresh_token,
                    "token_expiration": datetime.utcnow() + timedelta(seconds=expires_in or 3600),
                }
            )
        return True

    def action_sync_metrics(self):
        for account in self:
            account._sync_metrics()
        return True

    def _sync_metrics(self):
        service = self._get_service()
        try:
            metrics = service.fetch_metrics(self)
        except Exception as exc:  # pylint: disable=broad-except
            self.message_post(
                body=_("Metric synchronization failed: %s") % exc,
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
            return
        if not metrics:
            return
        metric_vals = []
        now = fields.Datetime.now()
        for metric in metrics:
            metric_vals.append(
                {
                    "account_id": self.id,
                    "metric_date": metric.get("date") or now,
                    "follower_count": metric.get("followers", 0),
                    "engagement_rate": metric.get("engagement", 0.0),
                    "impressions": metric.get("impressions", 0),
                    "clicks": metric.get("clicks", 0),
                    "campaign_id": metric.get("campaign_id"),
                }
            )
        self.env["social.media.metric"].create(metric_vals)
        last_metric = metrics and metrics[-1] or {}
        self.write(
            {
                "last_sync_date": now,
                "follower_count": last_metric.get("followers", self.follower_count),
                "engagement_rate": last_metric.get("engagement", self.engagement_rate),
            }
        )

    def _ensure_valid_token(self):
        exp = self.token_expiration
        if not exp or fields.Datetime.now() > exp - timedelta(minutes=5):
            self.action_refresh_token()
        return self.access_token

    @api.model
    def cron_sync_metrics(self):
        accounts = self.search([("active", "=", True)])
        for account in accounts:
            try:
                account._sync_metrics()
            except Exception as exc:  # pylint: disable=broad-except
                account.message_post(
                    body=_("Metric synchronization failed: %s") % exc,
                    message_type="comment",
                    subtype_xmlid="mail.mt_note",
                )
        return True
