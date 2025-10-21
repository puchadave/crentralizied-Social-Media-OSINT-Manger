# -*- coding: utf-8 -*-
"""Description of social platforms supported by the Postiz integration."""

from odoo import _, api, fields, models


class PostizSocialPlatform(models.Model):
    _name = "postiz.social.platform"
    _description = "Social media platform"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    technical_name = fields.Selection(
        selection=[
            ("facebook", "Facebook"),
            ("instagram", "Instagram"),
            ("linkedin", "LinkedIn"),
            ("pinterest", "Pinterest"),
            ("twitter", "X (Twitter)"),
            ("tiktok", "TikTok"),
            ("youtube", "YouTube"),
            ("telegram", "Telegram"),
            ("mastodon", "Mastodon"),
            ("custom", "Custom API"),
        ],
        required=True,
        default="facebook",
    )
    base_url = fields.Char(help="Root URL for the API endpoints.")
    documentation_url = fields.Char()
    auth_type = fields.Selection(
        [
            ("oauth2", "OAuth 2"),
            ("api_key", "API key"),
            ("basic", "HTTP basic"),
            ("webhook", "Webhook only"),
        ],
        default="oauth2",
    )
    scope = fields.Char(string="OAuth scope")
    notes = fields.Text()
    icon_html = fields.Char(help="SVG icon snippet for kanban views")
    is_active = fields.Boolean(default=True)
    webhook_route = fields.Char(compute="_compute_webhook_route", store=True)

    _sql_constraints = [
        ("postiz_social_platform_unique", "unique(technical_name)", "The platform already exists."),
    ]

    @api.depends("technical_name")
    def _compute_webhook_route(self):
        for platform in self:
            platform.webhook_route = "/postiz/webhook/%s" % platform.technical_name

    def get_default_headers(self):
        self.ensure_one()
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_display_name(self, show_sequence=False):  # pragma: no cover - UI helper
        name = super().get_display_name(show_sequence=show_sequence)
        if self.scope:
            return "%s (%s)" % (name, self.scope)
        return name

    def activate(self):
        for record in self:
            record.is_active = True

    def deactivate(self):
        for record in self:
            record.is_active = False

    def action_open_accounts(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Accounts"),
            "res_model": "postiz.social.account",
            "view_mode": "tree,form",
            "domain": [
                ("platform_id", "=", self.id),
            ],
        }
