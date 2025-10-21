from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestSocialMediaManagerTour(HttpCase):
    def test_social_media_manager_tour(self):
        self.start_tour('/web', 'social_media_manager_tour', login='admin')
