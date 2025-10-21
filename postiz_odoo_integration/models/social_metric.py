# -*- coding: utf-8 -*-
"""Analytics metrics similar to the insights provided by Postiz."""

from datetime import datetime
from typing import Optional

from odoo import _, api, fields, models


class PostizSocialMetric(models.Model):
    _name = "postiz.social.metric"
    _description = "Social media metric"
    _order = "capture_date desc"

    name = fields.Char(required=True, default="Metric")
    post_id = fields.Many2one("postiz.social.post", ondelete="cascade")
    channel_id = fields.Many2one("postiz.social.post.channel", ondelete="cascade")
    account_id = fields.Many2one("postiz.social.account", required=True, ondelete="cascade")
    capture_date = fields.Datetime(default=fields.Datetime.now)
    impressions = fields.Integer(default=0)
    clicks = fields.Integer(default=0)
    likes = fields.Integer(default=0)
    comments = fields.Integer(default=0)
    shares = fields.Integer(default=0)
    saves = fields.Integer(default=0)
    profile_visits = fields.Integer(default=0)
    follower_delta = fields.Integer(default=0)
    sentiment_score = fields.Float(default=0.0)
    payload = fields.Json(help="Raw payload returned by the social network")

    _sql_constraints = [
        (
            "postiz_metric_unique",
            "unique(account_id, channel_id, capture_date)",
            "A metric already exists for this snapshot.",
        )
    ]

    @api.model
    def create_or_update_from_payload(self, account, payload, post=None, channel=None):
        capture_date = self._parse_date(payload.get("captured_at")) or fields.Datetime.now()
        defaults = {
            "name": payload.get("name") or _("Metric"),
            "post_id": post and post.id,
            "channel_id": channel and channel.id,
            "account_id": account.id,
            "capture_date": capture_date,
            "impressions": int(payload.get("impressions", 0) or 0),
            "clicks": int(payload.get("clicks", 0) or 0),
            "likes": int(payload.get("likes", 0) or 0),
            "comments": int(payload.get("comments", 0) or 0),
            "shares": int(payload.get("shares", 0) or 0),
            "saves": int(payload.get("saves", 0) or 0),
            "profile_visits": int(payload.get("profile_visits", 0) or 0),
            "follower_delta": int(payload.get("follower_delta", 0) or 0),
            "sentiment_score": float(payload.get("sentiment_score", 0.0) or 0.0),
            "payload": payload,
        }
        existing = self.search([
            ("account_id", "=", account.id),
            ("channel_id", "=", channel and channel.id),
            ("capture_date", "=", defaults["capture_date"]),
        ], limit=1)
        if existing:
            existing.write(defaults)
            return existing
        return self.create(defaults)

    def get_totals(self):  # pragma: no cover - reporting helper
        totals = {
            "impressions": 0,
            "clicks": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "saves": 0,
        }
        for metric in self:
            for key in totals:
                totals[key] += getattr(metric, key)
        return totals

    def _parse_date(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None
