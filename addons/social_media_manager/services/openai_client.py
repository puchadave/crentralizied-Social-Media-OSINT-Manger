import json
import logging

import requests

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenAIClient(models.AbstractModel):
    _name = "social.openai.client"
    _description = "OpenAI ChatGPT Client"

    _default_endpoint = "https://api.openai.com/v1/chat/completions"

    def _get_api_key(self):
        key = (
            self.env["ir.config_parameter"].sudo().get_param("social_media_manager.openai_api_key")
        )
        if not key:
            raise UserError(
                _(
                    "The OpenAI API key is not configured. Set the 'social_media_manager.openai_api_key' system parameter.",
                )
            )
        return key

    def _prepare_headers(self, api_key):
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _perform_request(self, payload, endpoint=None):
        endpoint = endpoint or self._default_endpoint
        api_key = self._get_api_key()
        headers = self._prepare_headers(api_key)
        try:
            response = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=30)
        except requests.RequestException as exc:  # pylint: disable=broad-except
            _logger.exception("OpenAI request failed: %s", exc)
            raise UserError(_("Unable to reach OpenAI services: %s") % exc) from exc
        if response.status_code >= 400:
            _logger.error("OpenAI error %s: %s", response.status_code, response.text)
            raise UserError(_("OpenAI API returned an error: %s") % response.text)
        return response.json()

    def generate_content(self, prompt, context=None):
        payload = prompt.to_openai_payload(context=context)
        response = self._perform_request(payload)
        choices = response.get("choices", [])
        if not choices:
            raise UserError(_("OpenAI response did not include any choices."))
        return choices[0].get("message", {}).get("content", "")

    def generate_hashtags(self, base_content, count=5):
        payload = {
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "system", "content": "Create concise social media hashtags."},
                {
                    "role": "user",
                    "content": _(
                        "Generate %s creative hashtags based on the following content: %s",
                    )
                    % (count, base_content),
                },
            ],
        }
        response = self._perform_request(payload)
        choices = response.get("choices", [])
        if not choices:
            return []
        content = choices[0].get("message", {}).get("content", "")
        return [tag.strip() for tag in content.replace("#", " #").split() if tag.startswith("#")]
