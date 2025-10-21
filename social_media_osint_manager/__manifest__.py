{
    "name": "Social Media OSINT Manager",
    "summary": "Plan, generate and analyse social media content with AI assisted workflows and OSINT dashboards",
    "version": "16.0.1.0.0",
    "category": "Marketing/Social Media",
    "author": "OpenAI Assistant",
    "website": "https://example.com/social-media-osint",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "web",
        "board",
        "mass_mailing",
        "utm"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/osint_analysis_views.xml",
        "views/newsletter_views.xml",
        "views/social_post_views.xml",
        "views/social_account_views.xml",
        "views/ai_generator_views.xml",
        "views/dashboard_templates.xml",
        "views/menu_views.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "social_media_osint_manager/static/src/js/osint_dashboard.js",
            "social_media_osint_manager/static/src/css/osint_dashboard.css"
        ]
    },
    "external_dependencies": {
        "python": ["openai"]
    },
    "application": True,
    "installable": True
}
