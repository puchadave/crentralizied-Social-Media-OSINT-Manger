from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SocialMediaContentWizard(models.TransientModel):
    _name = "social.media.content.wizard"
    _description = "AI Assisted Social Media Content Wizard"

    account_id = fields.Many2one("social.media.account", required=True)
    post_id = fields.Many2one("social.media.post")
    prompt_template_id = fields.Many2one("social.media.prompt", required=True)
    additional_context = fields.Text()
    generated_caption = fields.Text(readonly=True)
    generated_body = fields.Html(readonly=True)
    generated_hashtags = fields.Char(readonly=True)

    @api.model
    def default_get(self, field_list):
        defaults = super().default_get(field_list)
        post_id = defaults.get('post_id') or self.env.context.get('default_post_id')
        if post_id:
            post = self.env['social.media.post'].browse(post_id)
            defaults.setdefault('post_id', post.id)
            if post.account_id:
                defaults.setdefault('account_id', post.account_id.id)
            prompt = post.prompt_template_id or post.account_id.prompt_template_id
            if prompt:
                defaults.setdefault('prompt_template_id', prompt.id)
        elif self.env.context.get('default_account_id'):
            defaults.setdefault('account_id', self.env.context['default_account_id'])
        return defaults

    def action_generate(self):
        self.ensure_one()
        prompt = self.prompt_template_id
        if not prompt:
            raise UserError(_("Select a prompt template before generating content."))
        context = self.additional_context
        service = self.env["social.openai.client"]
        body = service.generate_content(prompt, context=context)
        hashtags = service.generate_hashtags(body)
        caption = body.split("\n\n", maxsplit=1)[0] if body else ""
        self.write(
            {
                "generated_caption": caption,
                "generated_body": body,
                "generated_hashtags": ", ".join(hashtags),
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_apply_to_post(self):
        self.ensure_one()
        if not self.post_id:
            raise UserError(_("This wizard must be launched from a social media post."))
        hashtags = self.generated_hashtags or ""
        self.post_id.write(
            {
                "caption": self.generated_caption or self.post_id.caption,
                "body_html": self.generated_body or self.post_id.body_html,
                "prompt_template_id": self.prompt_template_id.id,
            }
        )
        if hashtags:
            self.post_id.message_post(body=_("Suggested hashtags: %s") % hashtags)
        return {"type": "ir.actions.act_window_close"}
