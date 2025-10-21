from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SocialMediaPost(models.Model):
    _name = "social.media.post"
    _description = "Social Media Post"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_date, id"

    name = fields.Char(required=True, tracking=True)
    account_id = fields.Many2one(
        "social.media.account",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("scheduled", "Scheduled"),
            ("posted", "Posted"),
            ("failed", "Failed"),
        ],
        default="draft",
        tracking=True,
    )
    post_type = fields.Selection(
        [
            ("text", "Text"),
            ("image", "Image"),
            ("video", "Video"),
            ("story", "Story"),
            ("mixed", "Mixed Media"),
        ],
        default="text",
        required=True,
        tracking=True,
    )
    caption = fields.Text(tracking=True)
    body_html = fields.Html(string="Post Body", sanitize=False)
    hashtag_ids = fields.Many2many("social.media.prompt", string="Hashtag Templates")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Media Attachments",
        relation="social_media_post_attachment_rel",
        column1="post_id",
        column2="attachment_id",
    )
    scheduled_date = fields.Datetime(tracking=True)
    published_date = fields.Datetime(readonly=True)
    campaign_id = fields.Many2one("marketing.campaign")
    error_message = fields.Text(readonly=True)
    metrics_summary = fields.Text(readonly=True)
    prompt_template_id = fields.Many2one(
        "social.media.prompt",
        string="Prompt Template",
        help="Prompt configuration used for AI assisted content generation.",
    )

    def action_schedule(self):
        for post in self:
            if not post.scheduled_date:
                raise UserError(_("Please provide a scheduled date before scheduling the post."))
            post.write({"state": "scheduled"})
        return True

    def action_publish_now(self):
        for post in self:
            post._publish_post()
        return True

    def _publish_post(self):
        if self.state not in ("scheduled", "draft"):
            return
        service = self.account_id._get_service()
        payload = self._prepare_payload()
        try:
            result = service.publish_post(self.account_id, payload)
        except Exception as exc:  # pylint: disable=broad-except
            self.write(
                {
                    "state": "failed",
                    "error_message": str(exc),
                }
            )
            self.account_id.message_post(
                body=_("Post '%s' failed to publish: %s") % (self.name, exc),
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
            return
        self.write(
            {
                "state": "posted",
                "published_date": fields.Datetime.now(),
                "error_message": False,
                "metrics_summary": result.get("summary") if isinstance(result, dict) else False,
            }
        )
        self.account_id.message_post(
            body=_("Post '%s' successfully published.") % self.name,
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )

    def _prepare_payload(self):
        return {
            "name": self.name,
            "body": self.body_html or self.caption,
            "caption": self.caption,
            "hashtags": [prompt.default_hashtags for prompt in self.hashtag_ids if prompt.default_hashtags],
            "type": self.post_type,
            "attachments": [
                {
                    "id": attachment.id,
                    "mimetype": attachment.mimetype,
                    "url": attachment.generate_access_token()[0] if hasattr(attachment, "generate_access_token") else attachment.url,
                }
                for attachment in self.attachment_ids
            ],
            "scheduled": self.scheduled_date,
            "campaign_id": self.campaign_id.id,
        }

    @api.model
    def cron_publish_posts(self):
        now = fields.Datetime.now()
        posts = self.search(
            [
                ("state", "=", "scheduled"),
                ("scheduled_date", "!=", False),
                ("scheduled_date", "<=", now),
            ]
        )
        for post in posts:
            post._publish_post()
        return True
