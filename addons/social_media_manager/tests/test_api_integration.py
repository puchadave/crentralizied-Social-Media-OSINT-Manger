from unittest.mock import patch

from odoo import fields
from odoo.tests import TransactionCase, tagged


class FakeFailureService:
    def __init__(self, env):
        self.env = env

    def refresh_token(self, account):
        return (account.access_token, account.refresh_token, 3600)

    def publish_post(self, account, payload):  # pylint: disable=unused-argument
        raise ValueError('API failure')

    def fetch_metrics(self, account):  # pylint: disable=unused-argument
        raise ValueError('Fetch failure')


@tagged('post_install', '-at_install')
class TestApiIntegration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account = cls.env['social.media.account'].create(
            {
                'name': 'Failure Account',
                'platform': 'facebook',
                'access_token': 'token',
                'refresh_token': 'refresh',
            }
        )
        cls.post = cls.env['social.media.post'].create(
            {
                'name': 'Failing Post',
                'account_id': cls.account.id,
                'post_type': 'text',
                'state': 'scheduled',
                'scheduled_date': fields.Datetime.now(),
            }
        )

    def test_publish_error_handling(self):
        with patch(
            'odoo.addons.social_media_manager.services.social_api_client.SocialApiClient.get_service',
            return_value=FakeFailureService(self.env),
        ):
            self.post._publish_post()
        self.assertEqual(self.post.state, 'failed')
        self.assertIn('API failure', self.post.error_message or '')

    def test_metric_sync_error_is_logged(self):
        with patch(
            'odoo.addons.social_media_manager.services.social_api_client.SocialApiClient.get_service',
            return_value=FakeFailureService(self.env),
        ):
            self.account._sync_metrics()
        self.assertFalse(self.account.metric_ids)
