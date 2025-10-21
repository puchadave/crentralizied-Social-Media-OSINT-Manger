# -*- coding: utf-8 -*-
"""Webhook endpoints that mimic the callbacks provided by Postiz."""

import logging

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PostizWebhookController(http.Controller):
    """Receive events such as published posts or refreshed analytics."""

    @http.route("/postiz/webhook/<string:platform>", type="json", auth="public", methods=["POST"], csrf=False)
    def receive_event(self, platform, **payload):
        _logger.info("Received webhook from %s: %s", platform, payload)
        platform_rec = request.env["postiz.social.platform"].sudo().search([
            ("technical_name", "=", platform)
        ], limit=1)
        if not platform_rec:
            return {"status": "unknown_platform"}
        token = payload.get("token")
        if not token:
            return {"status": "missing_token"}
        account = request.env["postiz.social.account"].sudo().search([
            ("webhook_token", "=", token)
        ], limit=1)
        if not account:
            return {"status": "unknown_account"}
        event_type = payload.get("event")
        if event_type == "post_published":
            self._handle_post_published(account, payload)
        elif event_type == "metric_updated":
            self._handle_metric_updated(account, payload)
        else:
            _logger.warning("Unhandled webhook event: %s", event_type)
        return {"status": "ok"}

    def _handle_post_published(self, account, payload):
        channel = request.env["postiz.social.post.channel"].sudo().search([
            ("external_id", "=", payload.get("external_id")),
            ("account_id", "=", account.id),
        ], limit=1)
        if not channel:
            return
        channel.write({
            "state": "published",
            "published_at": payload.get("published_at") or fields.Datetime.now(),
            "response_payload": payload,
        })

    def _handle_metric_updated(self, account, payload):
        metric_payload = payload.get("metric") or {}
        post = False
        if metric_payload.get("post_id"):
            post = request.env["postiz.social.post"].sudo().browse(metric_payload["post_id"])
        channel = False
        if payload.get("channel_id"):
            channel = request.env["postiz.social.post.channel"].sudo().browse(payload["channel_id"])
        request.env["postiz.social.metric"].sudo().create_or_update_from_payload(
            account,
            metric_payload,
            post=post,
            channel=channel,
        )
