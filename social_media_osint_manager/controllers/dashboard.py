from odoo import http
from odoo.http import request


class SocialMediaDashboardController(http.Controller):
    @http.route("/social_media/osint_dashboard", type="json", auth="user")
    def osint_dashboard(self, account_id=None):
        domain = []
        if account_id:
            domain.append(("account_id", "=", int(account_id)))
        snapshots = request.env["social.media.osint"].sudo().search(domain, limit=50)
        return {"snapshots": [snap.to_dashboard_payload() for snap in snapshots]}

    @http.route("/social_media/post_performance", type="json", auth="user")
    def post_performance(self, account_id=None):
        domain = []
        if account_id:
            domain.append(("account_id", "=", int(account_id)))
        posts = request.env["social.media.post"].sudo().search(domain, limit=100)
        dataset = [
            {
                "id": post.id,
                "title": post.name,
                "account": post.account_id.display_name,
                "likes": post.likes_count,
                "comments": post.comments_count,
                "shares": post.shares_count,
                "sentiment": post.sentiment_score,
                "engagement": post.engagement_score,
                "published": post.published_date,
            }
            for post in posts
        ]
        return {"posts": dataset}
