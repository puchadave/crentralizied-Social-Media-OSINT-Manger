import logging
from typing import Dict, Optional

from odoo import api, models, _

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None


_logger = logging.getLogger(__name__)


class OpenAIContentHelper:
    """Lightweight helper encapsulating OpenAI interactions."""

    def __init__(self, env):
        self.env = env

    @property
    def config_parameter(self):
        return self.env["ir.config_parameter"].sudo()

    def _get_client(self):
        api_key = self.config_parameter.get_param("social_media_osint_manager.openai_api_key")
        if not api_key:
            _logger.warning("No OpenAI API key configured - AI generation will be simulated.")
            return None
        if OpenAI is None:
            _logger.warning("openai python dependency missing - falling back to mocked responses.")
            return None
        return OpenAI(api_key=api_key)

    def generate_post_content(
        self,
        prompt: str,
        tone: str = "informative",
        hashtags: Optional[str] = None,
        target_audience: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, str]:
        model = model or "gpt-4o-mini"
        system_prompt = _(
            "You are an expert marketing copywriter who creates engaging social media content. "
            "Return JSON with keys title, body_html, summary, hashtags."
        )
        user_prompt = prompt
        if tone and tone != "custom":
            user_prompt += _("\nThe tone of voice must be %(tone)s.", tone=tone)
        if target_audience:
            user_prompt += _("\nTailor the message for: %(audience)s.", audience=target_audience)
        if hashtags:
            user_prompt += _("\nIncorporate these hashtags when appropriate: %(hashtags)s.", hashtags=hashtags)

        payload = {
            "title": None,
            "body_html": None,
            "summary": None,
            "hashtags": hashtags,
        }

        client = self._get_client()
        if client:
            try:
                response = client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                )
                if response.choices:
                    content = response.choices[0].message.content
                    payload.update(self._safe_json_load(content))
            except Exception as exc:  # pragma: no cover - network failure fallback
                _logger.exception("OpenAI content generation failed: %s", exc)

        if not payload.get("body_html"):
            fallback_body = _(
                "<p><strong>AI Draft:</strong> %(prompt)s</p>",
                prompt=prompt,
            )
            payload.update(
                {
                    "title": payload.get("title") or _("AI Generated Post"),
                    "body_html": fallback_body,
                    "summary": payload.get("summary") or prompt[:180],
                    "hashtags": hashtags,
                }
            )
        return payload

    # Helpers -----------------------------------------------------------------
    def _safe_json_load(self, content: str) -> Dict[str, str]:
        import json

        try:
            return json.loads(content) if content else {}
        except Exception:  # pragma: no cover - best effort fallback
            _logger.warning("OpenAI returned non JSON content: %s", content)
            return {"body_html": content}


class SocialMediaAISettings(models.TransientModel):
    _name = "social.media.ai.settings"
    _description = "Settings helper to configure OpenAI"
    _inherit = "res.config.settings"

    openai_api_key = models.Char(string="OpenAI API Key")

    def set_values(self):
        res = super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "social_media_osint_manager.openai_api_key", self.openai_api_key
        )
        return res

    @api.model
    def get_values(self):
        values = super().get_values()
        values.update(
            openai_api_key=self.env["ir.config_parameter"].sudo().get_param(
                "social_media_osint_manager.openai_api_key"
            )
        )
        return values
