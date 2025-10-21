from unittest.mock import patch

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestContentGeneration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.prompt = cls.env['social.media.prompt'].create(
            {
                'name': 'Default Prompt',
                'prompt_text': 'Write a compelling social media post for ${brand}.',
            }
        )
        cls.account = cls.env['social.media.account'].create(
            {
                'name': 'Demo Facebook',
                'platform': 'facebook',
                'access_token': 'token',
                'refresh_token': 'refresh',
            }
        )
        cls.post = cls.env['social.media.post'].create(
            {
                'name': 'Launch Announcement',
                'account_id': cls.account.id,
                'post_type': 'text',
            }
        )

    def test_generate_and_apply_content(self):
        wizard = self.env['social.media.content.wizard'].with_context(
            default_account_id=self.account.id,
            default_post_id=self.post.id,
            default_prompt_template_id=self.prompt.id,
        ).create(
            {
                'account_id': self.account.id,
                'post_id': self.post.id,
                'prompt_template_id': self.prompt.id,
            }
        )
        with patch(
            'odoo.addons.social_media_manager.services.openai_client.OpenAIClient.generate_content',
            return_value='Awesome body',
        ), patch(
            'odoo.addons.social_media_manager.services.openai_client.OpenAIClient.generate_hashtags',
            return_value=['#demo', '#odoo'],
        ):
            wizard.action_generate()
        self.assertEqual(wizard.generated_caption, 'Awesome body')
        self.assertIn('#demo', wizard.generated_hashtags)

        wizard.action_apply_to_post()
        self.assertIn('Awesome body', self.post.body_html)
