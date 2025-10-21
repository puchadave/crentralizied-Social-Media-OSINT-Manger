from odoo import fields, models


class SocialMediaAIContentWizard(models.TransientModel):
    _name = "social.media.ai.content.wizard"
    _description = "Wizard to request AI generated content"

    post_id = fields.Many2one("social.media.post", required=True)
    tone = fields.Selection(
        selection=lambda self: self.env["social.media.post"]._fields["ai_tone"].selection,
        default="informative",
    )
    prompt = fields.Text()
    hashtags = fields.Char()
    target_audience = fields.Char()
    temperature = fields.Float(default=0.7)

    def action_generate(self):
        self.ensure_one()
        values = {
            "ai_tone": self.tone,
            "ai_prompt": self.prompt,
            "hashtags": self.hashtags,
            "target_audience": self.target_audience,
            "ai_temperature": self.temperature,
        }
        self.post_id.write(values)
        self.post_id.action_generate_ai_content()
        return {
            "type": "ir.actions.act_window",
            "res_model": "social.media.post",
            "view_mode": "form",
            "res_id": self.post_id.id,
        }
