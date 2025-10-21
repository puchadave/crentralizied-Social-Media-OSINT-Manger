from odoo import fields, models


class SocialMediaNewsletterWizard(models.TransientModel):
    _name = "social.media.newsletter.wizard"
    _description = "Wizard to generate newsletters from social media posts"

    post_ids = fields.Many2many("social.media.post", string="Posts")
    account_ids = fields.Many2many("social.media.account", string="Accounts")
    newsletter_name = fields.Char(required=True, default="Weekly Social Digest")
    ai_prompt = fields.Text()

    def action_create_newsletter(self):
        self.ensure_one()
        Newsletter = self.env["social.media.newsletter"].sudo()
        newsletter = Newsletter.create(
            {
                "name": self.newsletter_name,
                "ai_prompt": self.ai_prompt,
                "post_ids": [(6, 0, self.post_ids.ids)],
                "account_ids": [(6, 0, self.account_ids.ids)],
            }
        )
        newsletter.action_generate_from_posts()
        return {
            "type": "ir.actions.act_window",
            "res_model": "social.media.newsletter",
            "view_mode": "form",
            "res_id": newsletter.id,
        }
