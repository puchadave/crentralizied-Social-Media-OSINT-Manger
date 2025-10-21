# -*- coding: utf-8 -*-
"""Scheduling and publishing of social media posts."""

from __future__ import annotations

from collections import Counter
from datetime import timedelta
from typing import Dict, List

from odoo import _, api, fields, models
from odoo.tools import html2plaintext
from odoo.exceptions import UserError

from .postiz_api_mixin import PostizAPIError


class PostizSocialPost(models.Model):
    _name = "postiz.social.post"
    _description = "Scheduled social post"
    _inherit = ["mail.thread", "mail.activity.mixin", "postiz.api.mixin"]
    _order = "scheduled_at desc, create_date desc"

    name = fields.Char(required=True, tracking=True, default=lambda self: self._default_name())
    workspace_id = fields.Many2one(
        "postiz.social.workspace",
        required=True,
        tracking=True,
        ondelete="cascade",
    )
    account_ids = fields.Many2many(
        "postiz.social.account",
        string="Accounts",
        relation="postiz_post_account_rel",
        column1="post_id",
        column2="account_id",
    )
    channel_ids = fields.One2many("postiz.social.post.channel", "post_id", string="Channels", copy=False)
    campaign_id = fields.Many2one("utm.campaign", string="Campaign", tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("scheduled", "Scheduled"),
            ("queued", "Queued"),
            ("publishing", "Publishing"),
            ("published", "Published"),
            ("failed", "Failed"),
            ("canceled", "Canceled"),
        ],
        default="draft",
        tracking=True,
    )
    approval_state = fields.Selection(
        [
            ("pending", "Pending approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="approved",
        tracking=True,
    )
    scheduled_at = fields.Datetime(tracking=True)
    published_at = fields.Datetime()
    deadline = fields.Datetime()
    body_text = fields.Html(required=True, tracking=True)
    link_url = fields.Char(string="Link")
    notes = fields.Text()
    allow_comments = fields.Boolean(default=True)
    preview_image_id = fields.Many2one("ir.attachment", string="Preview image")
    media_ids = fields.One2many("postiz.social.post.media", "post_id", string="Media")
    external_payload = fields.Json()
    analytics_metric_ids = fields.One2many("postiz.social.metric", "post_id", string="Metrics", copy=False)
    has_failed_channels = fields.Boolean(compute="_compute_has_failed_channels", store=True)
    next_action_at = fields.Datetime(compute="_compute_next_action_at", store=True)
    can_publish = fields.Boolean(compute="_compute_can_publish")

    def _default_name(self):  # pragma: no cover - uses sequence
        return self.env["ir.sequence"].next_by_code("postiz.social.post") or _("New Post")

    @api.depends("channel_ids.state", "scheduled_at")
    def _compute_next_action_at(self):
        for post in self:
            if post.state in ("draft", "canceled", "failed"):
                post.next_action_at = False
            elif post.scheduled_at:
                post.next_action_at = post.scheduled_at
            else:
                post.next_action_at = fields.Datetime.now()

    @api.depends("channel_ids.state")
    def _compute_has_failed_channels(self):
        for post in self:
            post.has_failed_channels = any(channel.state == "failed" for channel in post.channel_ids)

    @api.depends("approval_state", "scheduled_at", "account_ids")
    def _compute_can_publish(self):
        now = fields.Datetime.now()
        for post in self:
            post.can_publish = bool(
                post.account_ids
                and post.approval_state == "approved"
                and (not post.scheduled_at or post.scheduled_at <= now)
            )

    @api.constrains("scheduled_at", "deadline")
    def _check_schedule(self):
        for post in self:
            if post.deadline and post.scheduled_at and post.deadline < post.scheduled_at:
                raise UserError(_("The deadline cannot be before the schedule date."))

    @api.onchange("account_ids")
    def _onchange_account_ids(self):  # pragma: no cover - UI helper
        if self._origin:
            self._origin._sync_channels()
        else:
            self._sync_channels()

    def write(self, vals):
        res = super().write(vals)
        if "account_ids" in vals:
            self._sync_channels()
        if {"state", "channel_ids"} & set(vals.keys()):
            self._update_state_from_channels()
        return res

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._sync_channels()
        record._update_state_from_channels()
        return record

    def _sync_channels(self):
        for post in self:
            commands = []
            existing = {channel.account_id.id: channel for channel in post.channel_ids}
            for account in post.account_ids:
                if account.id not in existing:
                    commands.append((0, 0, {"account_id": account.id, "state": "draft"}))
            for channel in post.channel_ids:
                if channel.account_id not in post.account_ids:
                    commands.append((2, channel.id))
            if commands:
                post.write({"channel_ids": commands})

    def action_schedule(self):
        for post in self:
            if not post.scheduled_at:
                post.scheduled_at = fields.Datetime.now() + timedelta(minutes=10)
            if post.state == "draft":
                post.state = "scheduled"
            post.channel_ids.write({"state": "scheduled"})
            post.message_post(body=_("Post scheduled for %s") % post.scheduled_at)

    def action_publish(self):
        for post in self:
            if not post.can_publish:
                raise UserError(_("The post is not ready to be published."))
            post.state = "publishing"
            failures = []
            for channel in post.channel_ids:
                account = channel.account_id
                payload = post._prepare_post_payload(channel)
                try:
                    channel.write({"state": "publishing", "error_message": False})
                    account._ensure_token_valid()
                    response = account._postiz_request(
                        "POST",
                        f"{account.api_base_url or account.platform_id.base_url}/posts",
                        token=account.token,
                        json_payload=payload,
                    )
                except PostizAPIError as exc:
                    failures.append((channel, str(exc)))
                    continue
                channel.write({
                    "state": "published",
                    "external_id": response.get("id"),
                    "published_at": response.get("published_at") or fields.Datetime.now(),
                    "error_message": False,
                    "response_payload": response,
                })
            for channel, message in failures:
                channel.write({
                    "state": "failed",
                    "error_message": message,
                })
            post._update_state_from_channels()
            if failures:
                post.message_post(body=_("Some channels failed to publish."))
            else:
                post.message_post(body=_("Post published successfully."))

    def action_cancel(self):
        self.write({"state": "canceled"})
        for post in self:
            post.channel_ids.write({"state": "canceled"})

    def action_retry_failed(self):
        for post in self:
            failed_channels = post.channel_ids.filtered(lambda c: c.state == "failed")
            failed_channels.write({"state": "queued", "error_message": False})
            post.state = "queued"
        self.action_publish()

    def _prepare_post_payload(self, channel: "PostizSocialPostChannel") -> Dict:
        self.ensure_one()
        message = html2plaintext(self.body_text or "").strip()
        payload = {
            "message": message,
            "link": self.link_url,
            "allow_comments": self.allow_comments,
            "scheduled_at": self.scheduled_at and self._serialize_datetime(self.scheduled_at),
            "campaign": self.campaign_id and self.campaign_id.name,
            "workspace": self.workspace_id.name,
        }
        media_payload: List[Dict] = []
        for media in self.media_ids:
            media_payload.append({
                "name": media.name,
                "mimetype": media.mimetype,
                "url": media.url,
            })
        if media_payload:
            payload["media"] = media_payload
        return payload

    def _update_state_from_channels(self):
        for post in self:
            if not post.channel_ids:
                post.state = "draft"
                continue
            state_counter = Counter(post.channel_ids.mapped("state"))
            if state_counter.get("published") == len(post.channel_ids):
                post.state = "published"
                post.published_at = max(post.channel_ids.mapped("published_at"))
            elif state_counter.get("failed"):
                post.state = "failed"
            elif state_counter.get("publishing"):
                post.state = "publishing"
            elif state_counter.get("queued"):
                post.state = "queued"
            elif state_counter.get("scheduled") or post.scheduled_at:
                post.state = "scheduled"
            else:
                post.state = "draft"

    def action_fetch_latest_metrics(self):
        for post in self:
            for channel in post.channel_ids.filtered("external_id"):
                channel.action_fetch_metrics()

    @api.model
    def cron_publish_due_posts(self):
        domain = [
            ("state", "in", ["scheduled", "queued"]),
            ("approval_state", "=", "approved"),
            ("scheduled_at", "!=", False),
            ("scheduled_at", "<=", fields.Datetime.now()),
        ]
        posts = self.search(domain)
        if posts:
            posts.action_publish()


class PostizSocialPostMedia(models.Model):
    _name = "postiz.social.post.media"
    _description = "Post media"

    post_id = fields.Many2one("postiz.social.post", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    mimetype = fields.Char()
    attachment_id = fields.Many2one("ir.attachment", ondelete="set null")
    url = fields.Char(help="Optional URL when the media lives outside of Odoo")
    embed_html = fields.Html()


class PostizSocialPostChannel(models.Model):
    _name = "postiz.social.post.channel"
    _description = "Post publishing state per account"
    _inherit = "mail.thread"
    _order = "post_id, account_id"

    post_id = fields.Many2one("postiz.social.post", required=True, ondelete="cascade")
    account_id = fields.Many2one("postiz.social.account", required=True, ondelete="cascade")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("queued", "Queued"),
            ("publishing", "Publishing"),
            ("scheduled", "Scheduled"),
            ("published", "Published"),
            ("failed", "Failed"),
            ("canceled", "Canceled"),
        ],
        default="draft",
        tracking=True,
    )
    external_id = fields.Char()
    published_at = fields.Datetime()
    error_message = fields.Text()
    response_payload = fields.Json()
    metric_ids = fields.One2many("postiz.social.metric", "channel_id", string="Metrics")

    def action_fetch_metrics(self):
        metric_obj = self.env["postiz.social.metric"]
        for channel in self.filtered("external_id"):
            account = channel.account_id
            try:
                account._ensure_token_valid()
                response = account._postiz_request(
                    "GET",
                    f"{account.api_base_url or account.platform_id.base_url}/posts/{channel.external_id}/metrics",
                    token=account.token,
                )
            except (PostizAPIError, UserError) as exc:
                channel.write({"error_message": str(exc)})
                continue
            metrics = response.get("metrics") or []
            for payload in metrics:
                metric_obj.create_or_update_from_payload(account, payload, post=channel.post_id, channel=channel)

    def name_get(self):  # pragma: no cover - UI helper
        return [
            (channel.id, "%s - %s" % (channel.post_id.name, channel.account_id.name))
            for channel in self
        ]
