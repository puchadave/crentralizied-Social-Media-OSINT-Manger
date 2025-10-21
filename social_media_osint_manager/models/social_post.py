from datetime import timedelta
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError


POST_STATES = [
    ("draft", "Draft"),
    ("scheduled", "Scheduled"),
    ("published", "Published"),
    ("failed", "Failed"),
]


class SocialMediaPost(models.Model):
    _name = "social.media.post"
    _description = "Social Media Post"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_date desc, id desc"

    name = fields.Char(string="Title", tracking=True)
    account_id = fields.Many2one(
        "social.media.account",
        required=True,
        tracking=True,
        ondelete="cascade",
    )
    state = fields.Selection(selection=POST_STATES, default="draft", tracking=True)
    message = fields.Html(string="Message", required=True)
    caption = fields.Char(string="Caption")
    hashtags = fields.Char(
        help="Comma separated hashtags that will be appended to generated content."
    )
    media_ids = fields.Many2many("ir.attachment", string="Media")
    ai_prompt = fields.Text(
        string="AI Prompt",
        help="Prompt sent to the AI content generator for automated copy writing.",
    )
    ai_response = fields.Text(string="AI Response", copy=False, readonly=True)
    ai_model = fields.Char(string="AI Model", default="gpt-4o-mini", readonly=True)
    ai_temperature = fields.Float(string="Creativity", default=0.7)
    ai_tone = fields.Selection(
        selection=[
            ("informative", "Informative"),
            ("playful", "Playful"),
            ("formal", "Formal"),
            ("urgent", "Urgent"),
            ("custom", "Custom"),
        ],
        default="informative",
    )
    scheduled_date = fields.Datetime(tracking=True)
    published_date = fields.Datetime(readonly=True)
    error_message = fields.Char(readonly=True)
    newsletter_mailing_id = fields.Many2one("mailing.mailing", string="Newsletter")

    likes_count = fields.Integer(string="Likes")
    comments_count = fields.Integer(string="Comments")
    shares_count = fields.Integer(string="Shares / Reposts")
    clicks_count = fields.Integer(string="Clicks")
    sentiment_score = fields.Float(string="Sentiment", digits=(6, 2))
    engagement_reach = fields.Integer(string="Reach")
    engagement_score = fields.Float(
        string="Engagement Score", digits=(6, 2), compute="_compute_engagement_score", store=True
    )
    osint_snapshot_ids = fields.One2many(
        "social.media.osint",
        "post_id",
        string="OSINT Snapshots",
    )
    osint_last_snapshot = fields.Datetime(string="Last OSINT Snapshot")
    tags = fields.Many2many("mail.activity.type", string="Tags")
    campaign_id = fields.Many2one("utm.campaign", string="Campaign")
    link_preview = fields.Char(string="Link Preview")

    auto_publish = fields.Boolean(default=True)
    allow_comments = fields.Boolean(default=True)
    target_audience = fields.Char(help="Audience descriptors used for AI personalization.")

    metadata_json = fields.Text(string="Raw Metadata", copy=False)

    _sql_constraints = [
        ("scheduled_date_positive", "CHECK(1=1)", "Scheduled date must be valid."),
    ]

    @api.depends("likes_count", "comments_count", "shares_count", "clicks_count")
    def _compute_engagement_score(self):
        for post in self:
            reach = post.engagement_reach or 1
            weighted_sum = (
                post.likes_count * 1
                + post.comments_count * 2
                + post.shares_count * 3
                + post.clicks_count * 0.5
            )
            post.engagement_score = weighted_sum / reach if reach else 0.0

    def action_generate_ai_content(self):
        from .ai_service import OpenAIContentHelper

        for post in self:
            prompt = post.ai_prompt or post._build_prompt_from_context()
            helper = OpenAIContentHelper(self.env)
            ai_payload = helper.generate_post_content(
                prompt=prompt,
                tone=post.ai_tone,
                hashtags=post.hashtags,
                target_audience=post.target_audience,
            )
            post.write(
                {
                    "message": ai_payload.get("body_html"),
                    "ai_response": json.dumps(ai_payload, indent=2),
                    "name": ai_payload.get("title") or post.name,
                }
            )
        return True

    def _build_prompt_from_context(self):
        self.ensure_one()
        prompt_parts = [
            _("Create a social media post for the %(platform)s account %(account)s.",
              platform=self.account_id.platform.title(), account=self.account_id.name)
        ]
        if self.campaign_id:
            prompt_parts.append(
                _("The post should support the campaign: %(campaign)s.", campaign=self.campaign_id.name)
            )
        if self.hashtags:
            prompt_parts.append(_("Incorporate the hashtags: %(hashtags)s.", hashtags=self.hashtags))
        if self.target_audience:
            prompt_parts.append(_("Target audience insights: %(audience)s.", audience=self.target_audience))
        return "\n".join(prompt_parts)

    def action_schedule(self):
        for post in self:
            if post.state == "published":
                raise UserError(_("Published content cannot be rescheduled."))
            if not post.scheduled_date:
                post.scheduled_date = fields.Datetime.now() + timedelta(hours=2)
            post.state = "scheduled"
            post.message_post(body=_("Post scheduled for publication on %(date)s", date=post.scheduled_date))
        return True

    def action_publish(self):
        for post in self:
            if post.state not in ("draft", "scheduled"):
                raise UserError(_("Only draft or scheduled posts can be published."))
            post.state = "published"
            post.published_date = fields.Datetime.now()
            post.message_post(body=_("Post marked as published."))
        return True

    def action_refresh_metrics(self):
        for post in self:
            analytics = post.osint_snapshot_ids[:1]
            if analytics:
                post.likes_count = analytics.likes_count
                post.comments_count = analytics.comments_count
                post.shares_count = analytics.shares_count
                post.sentiment_score = analytics.sentiment_score
                post.engagement_reach = analytics.reach
            else:
                post.likes_count = post.likes_count or 0
                post.comments_count = post.comments_count or 0
                post.shares_count = post.shares_count or 0
            post.metadata_json = json.dumps(
                {
                    "likes": post.likes_count,
                    "comments": post.comments_count,
                    "shares": post.shares_count,
                    "sentiment": post.sentiment_score,
                    "updated_at": fields.Datetime.now().isoformat(),
                },
                indent=2,
            )
        return True

    def action_open_osint_dashboard(self):
        self.ensure_one()
        action = self.env.ref("social_media_osint_manager.action_social_media_osint_analysis").read()[0]
        action["domain"] = ["|", ("post_id", "=", self.id), ("account_id", "=", self.account_id.id)]
        return action
