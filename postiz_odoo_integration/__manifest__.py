# -*- coding: utf-8 -*-
{
    "name": "Postiz Social Media Manager",
    "summary": "Plan, publish and analyze social media content with Postiz-like integrations.",
    "version": "16.0.1.0.0",
    "category": "Marketing/Social",
    "author": "OpenAI Assistant",
    "website": "https://example.com/postiz",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "utm",
        "web",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/postiz_sequence.xml",
        "data/postiz_social_platform_data.xml",
        "data/postiz_cron.xml",
        "wizard/postiz_bulk_publish_views.xml",
        "views/postiz_menus.xml",
        "views/postiz_social_workspace_views.xml",
        "views/postiz_social_account_views.xml",
        "views/postiz_social_post_views.xml",
        "views/postiz_social_platform_views.xml",
        "views/postiz_social_metric_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "postiz_odoo_integration/static/src/scss/postiz_dashboard.scss",
        ]
    },
    "external_dependencies": {
        "python": ["requests", "pytz"],
    },
    "application": True,
}
