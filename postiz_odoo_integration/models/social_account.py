# -*- coding: utf-8 -*-
"""Representation of connected social media accounts."""

from datetime import datetime, timedelta
from uuid import uuid4

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .postiz_api_mixin import PostizAPIError


class PostizSocialAccount(models.Model):
    _name = "postiz.social.account"
    _description = "Social media account"
    _inherit = ["mail.thread", "mail.activity.mixin", "postiz.api.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    platform_id = fields.Many2one(
        "postiz.social.platform",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    workspace_id = fields.Many2one(
        "postiz.social.workspace",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("connected", "Connected"),
            ("expired", "Expired"),
            ("error", "Error"),
        ],
        default="draft",
        tracking=True,
    )
    token = fields.Char(groups="postiz_odoo_integration.group_postiz_manager")
    refresh_token = fields.Char(groups="postiz_odoo_integration.group_postiz_manager")
    token_expiration = fields.Datetime()
    page_identifier = fields.Char(help="Page, profile or channel identifier")
    page_name = fields.Char()
    api_base_url = fields.Char()
    webhook_token = fields.Char(copy=False, default=lambda self: uuid4().hex)
    last_sync = fields.Datetime()
    sync_status = fields.Selection([
        ("idle", "Idle"),
        ("running", "Running"),
        ("failed", "Failed"),
    ], default="idle", tracking=True)
    error_message = fields.Text()
    metadata = fields.Json()
    campaign_tag_ids = fields.Many2many("utm.tag", string="UTM Tags")
    external_metrics_count = fields.Integer(compute="_compute_external_metrics_count")

    _sql_constraints = [
        (
            "postiz_social_account_unique",
            "unique(platform_id, page_identifier)",
            "This social account is already connected.",
        ),
    ]

    @api.depends("metadata")
    def _compute_external_metrics_count(self):
        metric_obj = self.env["postiz.social.metric"]
        for account in self:
            account.external_metrics_count = metric_obj.search_count([
                ("account_id", "=", account.id)
            ])

    def _prepare_connection_payload(self):
        self.ensure_one()
        return {
            "platform": self.platform_id.technical_name,
            "page_identifier": self.page_identifier,
            "refresh_token": self.refresh_token,
        }

    def action_connect(self):
        for account in self:
            if not account.api_base_url:
                account.api_base_url = account.platform_id.base_url
            payload = account._prepare_connection_payload()
            response = account._postiz_request(
                "POST",
                f"{account.api_base_url}/connect",
                json_payload=payload,
                headers=account.platform_id.get_default_headers(),
            )
            token = response.get("access_token")
            if not token:
                raise UserError(_("The platform did not return an access token."))
            account.write({
                "token": token,
                "refresh_token": response.get("refresh_token") or account.refresh_token,
                "token_expiration": account._parse_expiration(response.get("expires_in")),
                "state": "connected",
                "error_message": False,
            })

    def action_refresh_token(self):
        for account in self:
            if not account.refresh_token:
                raise UserError(_("No refresh token has been stored for this account."))
            response = account._postiz_request(
                "POST",
                f"{account.api_base_url or account.platform_id.base_url}/refresh",
                json_payload={"refresh_token": account.refresh_token},
            )
            account.write({
                "token": response.get("access_token"),
                "token_expiration": account._parse_expiration(response.get("expires_in")),
                "state": "connected",
            })

    def action_disconnect(self):
        for account in self:
            account.write({
                "token": False,
                "refresh_token": False,
                "token_expiration": False,
                "state": "draft",
            })

    def _parse_expiration(self, expires_in):
        if not expires_in:
            return False
        try:
            expires_int = int(expires_in)
        except (TypeError, ValueError):
            return False
        return fields.Datetime.to_string(datetime.utcnow() + timedelta(seconds=expires_int))

    def _ensure_token_valid(self):
        for account in self:
            if not account.token:
                raise UserError(_("The account %s is not connected.") % account.name)
            if account.token_expiration and account.token_expiration < fields.Datetime.now():
                account.action_refresh_token()

    def fetch_post_status(self, external_id: str):
        self.ensure_one()
        try:
            response = self._postiz_request(
                "GET",
                f"{self.api_base_url or self.platform_id.base_url}/posts/{external_id}",
                token=self.token,
            )
        except PostizAPIError as exc:
            self.write({
                "state": "error",
                "error_message": str(exc),
            })
            raise
        return response

    def action_fetch_metrics(self):
        metric_obj = self.env["postiz.social.metric"]
        for account in self:
            account._ensure_token_valid()
            response = account._postiz_request(
                "GET",
                f"{account.api_base_url or account.platform_id.base_url}/analytics",
                token=account.token,
            )
            metrics = response.get("data", [])
            for item in metrics:
                metric_obj.create_or_update_from_payload(account, item)
            account.write({
                "last_sync": fields.Datetime.now(),
                "sync_status": "idle",
                "error_message": False,
            })

    def action_schedule_sync(self):
        self.write({"sync_status": "running"})
        for account in self:
            account.action_fetch_metrics()

    def name_get(self):  # pragma: no cover - UI helper
        result = []
        for record in self:
            name = record.name
            if record.page_identifier:
                name = "%s (%s)" % (name, record.page_identifier)
            result.append((record.id, name))
        return result

    @api.model
    def cron_sync_accounts(self):
        accounts = self.search([("state", "=", "connected")])
        for account in accounts:
            try:
                account.action_schedule_sync()
            except PostizAPIError as exc:
                account.write({
                    "sync_status": "failed",
                    "error_message": str(exc),
                })
