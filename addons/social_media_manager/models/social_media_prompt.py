from odoo import fields, models


class SocialMediaPrompt(models.Model):
    _name = "social.media.prompt"
    _description = "Social Media Prompt"
    _order = "name"

    name = fields.Char(required=True)
    prompt_text = fields.Text(required=True)
    default_hashtags = fields.Char()
    tone = fields.Selection(
        [
            ("friendly", "Friendly"),
            ("professional", "Professional"),
            ("playful", "Playful"),
            ("inspirational", "Inspirational"),
        ],
        default="friendly",
    )
    target_audience = fields.Char()
    channel = fields.Selection(
        selection=[
            ("facebook", "Facebook"),
            ("instagram", "Instagram"),
            ("twitter", "Twitter / X"),
            ("linkedin", "LinkedIn"),
            ("youtube", "YouTube"),
            ("tiktok", "TikTok"),
            ("generic", "Generic"),
        ],
        default="generic",
    )
    temperature = fields.Float(default=0.7)
    max_tokens = fields.Integer(default=250)

    def to_openai_payload(self, context=None):
        self.ensure_one()
        base_prompt = self.prompt_text
        if context:
            base_prompt = f"{base_prompt}\n\nContext:\n{context}"
        return {
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "system", "content": "You are a social media marketer."},
                {"role": "user", "content": base_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
