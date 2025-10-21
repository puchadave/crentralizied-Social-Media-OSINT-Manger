from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDashboardMetrics(TransactionCase):
    def setUp(self):
        super().setUp()
        self.account = self.env['social.media.account'].create(
            {
                'name': 'Metrics Account',
                'platform': 'twitter',
            }
        )

    def test_dashboard_aggregation(self):
        metric_model = self.env['social.media.metric']
        now = fields.Datetime.now()
        metric_model.create(
            [
                {
                    'account_id': self.account.id,
                    'metric_date': now,
                    'follower_count': 100,
                    'engagement_rate': 1.2,
                    'impressions': 1000,
                    'clicks': 120,
                },
                {
                    'account_id': self.account.id,
                    'metric_date': now - timedelta(days=1),
                    'follower_count': 110,
                    'engagement_rate': 1.4,
                    'impressions': 800,
                    'clicks': 90,
                },
            ]
        )
        data = metric_model.get_dashboard_data()
        self.assertGreater(data['totals']['followers'], 0)
        self.assertIn(self.account.id, data['by_account'])
