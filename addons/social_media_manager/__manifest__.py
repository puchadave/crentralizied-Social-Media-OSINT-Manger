# Copyright 2024
{
    "name": "Social Media Manager",
    "summary": "Plan, publish, and analyze social media campaigns from Odoo.",
    "version": "16.0.1.0.0",
    "author": "OpenAI Assistant",
    "website": "https://www.example.com",
    "category": "Marketing",
    "depends": [
        "mail",
        "social",
        "marketing_automation",
        "board",
        "web_dashboard",
    ],
    "data": [
        "security/social_media_security.xml",
        "security/ir.model.access.csv",
        "data/social_media_cron.xml",
        "views/social_media_menus.xml",
        "views/social_media_account_views.xml",
        "views/social_media_post_views.xml",
        "views/social_media_metric_views.xml",
        "views/social_media_dashboard_views.xml",
        "views/social_media_wizard_views.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "social_media_manager/static/src/js/social_media_manager_tour.js",
        ],
    },
    "application": True,
    "license": "LGPL-3",
}
