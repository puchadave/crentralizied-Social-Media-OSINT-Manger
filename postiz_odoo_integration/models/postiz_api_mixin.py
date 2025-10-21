# -*- coding: utf-8 -*-
"""Utility helpers that encapsulate HTTP calls to social media APIs."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PostizAPIError(UserError):
    """Raised when an upstream social network returns an error."""


class PostizAPIMixin(models.AbstractModel):
    """Reusable mixin for talking to Postiz compatible APIs.

    The real Postiz platform uses OAuth protected HTTP APIs.  This mixin offers a
    thin wrapper around :mod:`requests` so that models can focus on preparing the
    payload.  It provides structured logging, error wrapping and automatic JSON
    encoding.
    """

    _name = "postiz.api.mixin"
    _description = "Postiz API mixin"

    def _postiz_request(
        self,
        method: str,
        url: str,
        *,
        token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Perform an HTTP request and return the decoded JSON payload.

        Parameters
        ----------
        method: str
            HTTP verb (``GET``, ``POST`` ...).
        url: str
            Full endpoint URL.
        token: str, optional
            OAuth bearer token.  When provided an ``Authorization`` header is
            injected.
        params, data, json_payload: dict, optional
            Optional query string, form or JSON payload.
        timeout: int
            Request timeout in seconds.
        headers: dict, optional
            Additional HTTP headers.
        """

        session_headers: Dict[str, str] = {"User-Agent": "Odoo-Postiz-Connector/1.0"}
        if headers:
            session_headers.update(headers)
        if token:
            session_headers.setdefault("Authorization", f"Bearer {token}")

        _logger.debug(
            "Calling Postiz API", extra={
                "url": url,
                "method": method,
                "params": params,
                "data": data,
                "json": json_payload,
            }
        )

        try:
            response = requests.request(
                method,
                url,
                params=params,
                data=data,
                json=json_payload,
                timeout=timeout,
                headers=session_headers,
            )
        except requests.RequestException as exc:
            _logger.exception("Network error while contacting Postiz API")
            raise PostizAPIError(_("Network error while contacting Postiz API: %s", exc))

        if response.status_code >= 400:
            self._handle_postiz_error(response)

        content_type = response.headers.get("Content-Type", "")
        if "json" not in content_type:
            _logger.debug("Non JSON response from Postiz: %s", response.text[:200])
            return {"raw": response.text}
        try:
            return response.json()
        except ValueError as exc:  # pragma: no cover - defensive programming
            _logger.exception("Failed to decode Postiz JSON response")
            raise PostizAPIError(_("Failed to decode JSON response: %s", exc))

    def _handle_postiz_error(self, response: requests.Response) -> None:
        """Normalize errors in a user friendly :class:`UserError`."""

        try:
            payload = response.json()
            message = payload.get("message") or payload.get("error")
        except ValueError:
            message = response.text

        _logger.error(
            "Postiz API error",
            extra={
                "status": response.status_code,
                "body": message,
                "headers": dict(response.headers),
            },
        )

        error_message = _(
            "The social network returned an error (%(status)s): %(message)s",
            status=response.status_code,
            message=message,
        )
        raise PostizAPIError(error_message)

    def _serialize_datetime(self, value: datetime) -> str:
        """Serialize datetimes the way Postiz expects them."""

        return value.astimezone().isoformat()

    def _safe_json_loads(self, payload: str) -> Dict[str, Any]:
        """Utility that transforms a raw payload into a dictionary."""

        try:
            return json.loads(payload or "{}")
        except ValueError:
            _logger.exception("Failed to parse JSON payload: %s", payload)
            return {}
