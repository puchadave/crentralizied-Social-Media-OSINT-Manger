import json

from odoo import fields, models, _
from odoo.exceptions import UserError


class SocialMediaNewsletter(models.Model):
    _name = "social.media.newsletter"
    _description = "AI generated newsletter from social content"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    account_ids = fields.Many2many("social.media.account", string="Accounts")
    post_ids = fields.Many2many("social.media.post", string="Posts")
    ai_prompt = fields.Text(
        help="Prompt that guides the AI assistant when preparing the newsletter summary."
    )
    ai_response = fields.Text(readonly=True)
    mailing_id = fields.Many2one("mailing.mailing", string="Mass Mailing", copy=False)
    newsletter_body = fields.Html(string="Newsletter Body")
    summary = fields.Text()
    scheduled_date = fields.Datetime()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("ready", "Ready"),
            ("sent", "Sent"),
        ],
        default="draft",
    )

    def action_generate_from_posts(self):
        from .ai_service import OpenAIContentHelper

        helper = OpenAIContentHelper(self.env)
        for newsletter in self:
            prompt = newsletter.ai_prompt or newsletter._build_prompt()
            payload = helper.generate_post_content(
                prompt=prompt,
                tone="informative",
                hashtags=None,
                target_audience=None,
            )
            newsletter.write(
                {
                    "newsletter_body": payload.get("body_html"),
                    "summary": payload.get("summary"),
                    "ai_response": json.dumps(payload, indent=2),
                    "state": "ready",
                }
            )
        return True

    def _build_prompt(self):
        self.ensure_one()
        topics = []
        for post in self.post_ids:
            topics.append(
                _(
                    "- %(title)s (engagement: %(engagement)s, sentiment: %(sentiment)s)",
                    title=post.name or post.caption or post.account_id.name,
                    engagement=f"{post.engagement_score:.2f}",
                    sentiment=f"{post.sentiment_score:+.2f}",
                )
            )
        prompt = _(
            "Create a newsletter that summarises the latest highlights for our social media community."
        )
        if topics:
            prompt += "\n" + _("Include the following talking points:\n%(topics)s", topics="\n".join(topics))
        return prompt

    def action_prepare_mailing(self):
        Mailing = self.env["mailing.mailing"].sudo()
        for newsletter in self:
            if not newsletter.newsletter_body:
                raise UserError(_("Generate the newsletter content before creating a mailing."))
            values = {
                "name": newsletter.name,
                "subject": newsletter.name,
                "body_html": newsletter.newsletter_body,
                "mailing_type": "mail",
            }
            if newsletter.mailing_id:
                newsletter.mailing_id.write(values)
            else:
                newsletter.mailing_id = Mailing.create(values)
            newsletter.state = "ready"
        return True

    def action_send(self):
        for newsletter in self:
            if not newsletter.mailing_id:
                newsletter.action_prepare_mailing()
            newsletter.mailing_id.action_send_mail()
            newsletter.state = "sent"
        return True
