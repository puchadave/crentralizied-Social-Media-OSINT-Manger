import logging
from datetime import datetime

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BaseSocialService:
    """Generic integration layer for external social media APIs."""

    platform = "generic"

    def __init__(self, env):
        self.env = env

    # pylint: disable=unused-argument
    def refresh_token(self, account):
        return None

    def publish_post(self, account, payload):
        raise NotImplementedError

    def fetch_metrics(self, account):
        return []

    def _mock_success(self, message):
        _logger.info("[Social API] %s", message)
        return {"summary": message}


class FacebookService(BaseSocialService):
    platform = "facebook"

    def refresh_token(self, account):
        if not account.refresh_token:
            return None
        return (
            f"fb-{account.refresh_token}-new",
            account.refresh_token,
            3600,
        )

    def publish_post(self, account, payload):
        _logger.info("Publishing to Facebook: account=%s payload=%s", account.id, payload)
        return self._mock_success("Facebook post scheduled")

    def fetch_metrics(self, account):
        return [
            {
                "date": datetime.utcnow(),
                "followers": account.follower_count + 10,
                "engagement": account.engagement_rate + 0.5,
                "impressions": 1234,
                "clicks": 150,
            }
        ]


class InstagramService(FacebookService):
    platform = "instagram"

    def publish_post(self, account, payload):
        _logger.info("Publishing to Instagram: account=%s payload=%s", account.id, payload)
        return self._mock_success("Instagram content published")


class TwitterService(BaseSocialService):
    platform = "twitter"

    def refresh_token(self, account):
        if account.refresh_token:
            return (f"tw-{account.refresh_token}-token", account.refresh_token, 7200)
        return None

    def publish_post(self, account, payload):
        _logger.info("Tweeting for account=%s payload=%s", account.id, payload)
        return self._mock_success("Tweet sent")

    def fetch_metrics(self, account):
        return [
            {
                "date": datetime.utcnow(),
                "followers": account.follower_count + 5,
                "engagement": account.engagement_rate + 0.2,
                "impressions": 800,
                "clicks": 75,
            }
        ]


class LinkedInService(BaseSocialService):
    platform = "linkedin"

    def refresh_token(self, account):
        if account.refresh_token:
            return (f"li-{account.refresh_token}-token", account.refresh_token, 3600)
        return None

    def publish_post(self, account, payload):
        _logger.info("Sharing LinkedIn post for account=%s payload=%s", account.id, payload)
        return self._mock_success("LinkedIn update published")


class YouTubeService(BaseSocialService):
    platform = "youtube"

    def refresh_token(self, account):
        if account.refresh_token:
            return (f"yt-{account.refresh_token}-token", account.refresh_token, 3600)
        return None

    def publish_post(self, account, payload):
        _logger.info("Uploading video to YouTube for account=%s payload=%s", account.id, payload)
        return self._mock_success("YouTube upload completed")

    def fetch_metrics(self, account):
        return [
            {
                "date": datetime.utcnow(),
                "followers": account.follower_count + 20,
                "engagement": account.engagement_rate + 1.0,
                "impressions": 2000,
                "clicks": 300,
            }
        ]


class TikTokService(BaseSocialService):
    platform = "tiktok"

    def publish_post(self, account, payload):
        _logger.info("Publishing TikTok video for account=%s payload=%s", account.id, payload)
        return self._mock_success("TikTok video published")


class SocialApiClient(models.AbstractModel):
    _name = "social.api.client"
    _description = "Social Media API Client"

    _service_handlers = {
        "facebook": FacebookService,
        "instagram": InstagramService,
        "twitter": TwitterService,
        "linkedin": LinkedInService,
        "youtube": YouTubeService,
        "tiktok": TikTokService,
    }

    def get_service(self, platform):
        handler = self._service_handlers.get(platform)
        if not handler:
            return BaseSocialService(self.env)
        return handler(self.env)

    def refresh_token(self, account):
        service = self.get_service(account.platform)
        try:
            return service.refresh_token(account)
        except Exception as exc:  # pylint: disable=broad-except
            _logger.exception("Token refresh failed for account %s: %s", account.id, exc)
            raise

    def publish_post(self, account, payload):
        service = self.get_service(account.platform)
        account._ensure_valid_token()
        try:
            return service.publish_post(account, payload)
        except Exception as exc:  # pylint: disable=broad-except
            _logger.exception("Publish failed for account %s: %s", account.id, exc)
            raise UserError(_("Publishing failed: %s") % exc)  # type: ignore[name-defined]

    def fetch_metrics(self, account):
        service = self.get_service(account.platform)
        account._ensure_valid_token()
        try:
            return service.fetch_metrics(account)
        except Exception as exc:  # pylint: disable=broad-except
            _logger.exception("Metric synchronization failed for account %s: %s", account.id, exc)
            return []
