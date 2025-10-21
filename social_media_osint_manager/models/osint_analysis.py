import json
from collections import Counter, defaultdict
from statistics import mean

from odoo import api, fields, models


class SocialMediaOSINT(models.Model):
    _name = "social.media.osint"
    _description = "Social Media OSINT Snapshot"
    _order = "snapshot_at desc"

    name = fields.Char(default="OSINT Snapshot", required=True)
    account_id = fields.Many2one("social.media.account", required=True, ondelete="cascade")
    post_id = fields.Many2one("social.media.post", ondelete="set null")
    snapshot_at = fields.Datetime(default=fields.Datetime.now)
    likes_count = fields.Integer()
    comments_count = fields.Integer()
    shares_count = fields.Integer()
    reach = fields.Integer()
    sentiment_score = fields.Float(digits=(6, 2))
    mentions_count = fields.Integer()
    repost_graph_json = fields.Text()
    topic_breakdown_json = fields.Text()
    location_heatmap_json = fields.Text()
    metadata_json = fields.Text()

    def to_dashboard_payload(self):
        self.ensure_one()
        return {
            "id": self.id,
            "snapshot_at": self.snapshot_at,
            "account_id": self.account_id.id,
            "post_id": self.post_id.id if self.post_id else None,
            "likes": self.likes_count,
            "comments": self.comments_count,
            "shares": self.shares_count,
            "sentiment": self.sentiment_score,
            "reach": self.reach,
            "mentions": self.mentions_count,
            "topics": json.loads(self.topic_breakdown_json or "{}"),
        }

    # Data collection ---------------------------------------------------------
    @api.model
    def create_from_account(self, account):
        if not account:
            return self
        posts = account.posts_ids
        snapshot_time = fields.Datetime.now()
        if not posts:
            snapshot = self.create(
                {
                    "name": f"{account.name} Snapshot",
                    "account_id": account.id,
                    "snapshot_at": snapshot_time,
                }
            )
            account.write({"osint_last_snapshot": snapshot_time})
            return snapshot

        likes = sum(posts.mapped("likes_count"))
        comments = sum(posts.mapped("comments_count"))
        shares = sum(posts.mapped("shares_count"))
        reach = sum(posts.mapped("engagement_reach")) or len(posts)
        sentiment_values = [post.sentiment_score or 0 for post in posts if post.sentiment_score]
        avg_sentiment = mean(sentiment_values) if sentiment_values else 0.0

        hashtags = Counter()
        mention_counter = Counter()
        for post in posts:
            if post.hashtags:
                hashtags.update([tag.strip().lower() for tag in post.hashtags.split(",") if tag.strip()])
            body = post.message or ""
            mention_counter.update(self._extract_mentions(body))

        location_heatmap = self._build_location_heatmap(posts)
        repost_graph = self._build_repost_graph(posts)
        metadata = {
            "top_hashtags": hashtags.most_common(10),
            "top_mentions": mention_counter.most_common(10),
        }
        topic_breakdown = {tag: count for tag, count in hashtags.most_common(15)}

        snapshot = self.create(
            {
                "name": f"{account.name} Snapshot {snapshot_time}",
                "account_id": account.id,
                "snapshot_at": snapshot_time,
                "likes_count": likes,
                "comments_count": comments,
                "shares_count": shares,
                "reach": reach,
                "sentiment_score": avg_sentiment,
                "mentions_count": sum(mention_counter.values()),
                "topic_breakdown_json": json.dumps(topic_breakdown),
                "location_heatmap_json": json.dumps(location_heatmap),
                "repost_graph_json": json.dumps(repost_graph),
                "metadata_json": json.dumps(metadata),
            }
        )
        account.write({"osint_last_snapshot": snapshot_time})
        account.posts_ids.write({"osint_last_snapshot": snapshot_time})
        return snapshot

    @api.model
    def create_from_post(self, post):
        if not post:
            return self
        snapshot_time = fields.Datetime.now()
        snapshot = self.create(
            {
                "name": f"{post.name} Snapshot",
                "account_id": post.account_id.id,
                "post_id": post.id,
                "snapshot_at": snapshot_time,
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "shares_count": post.shares_count,
                "reach": post.engagement_reach,
                "sentiment_score": post.sentiment_score,
                "topic_breakdown_json": json.dumps(self._extract_topics(post)),
                "metadata_json": post.metadata_json,
            }
        )
        post.write({"osint_last_snapshot": snapshot_time})
        return snapshot

    # Analytics helpers -------------------------------------------------------
    def _build_location_heatmap(self, posts):
        heatmap = defaultdict(int)
        for post in posts:
            metadata = self._safe_json_load(post.metadata_json)
            for location in metadata.get("locations", []):
                heatmap[location] += 1
        return heatmap

    def _build_repost_graph(self, posts):
        graph = {"nodes": [], "links": []}
        node_index = {}
        for post in posts:
            post_node = self._add_node(graph, node_index, f"post-{post.id}", label=post.name or str(post.id))
            metadata = self._safe_json_load(post.metadata_json)
            for mention in metadata.get("mentions", []):
                mention_node = self._add_node(graph, node_index, mention, label=mention)
                graph["links"].append({"source": post_node, "target": mention_node, "value": 1})
        return graph

    def _add_node(self, graph, node_index, key, label):
        if key not in node_index:
            node_index[key] = len(graph["nodes"])
            graph["nodes"].append({"id": key, "label": label})
        return node_index[key]

    def _extract_mentions(self, message: str):
        import re

        return [match.lower() for match in re.findall(r"@([A-Za-z0-9_\.]+)", message or "")]

    def _extract_topics(self, post):
        hashtags = {}
        if post.hashtags:
            for tag in post.hashtags.split(","):
                cleaned = tag.strip().lower()
                if cleaned:
                    hashtags[cleaned] = hashtags.get(cleaned, 0) + 1
        return hashtags

    def _safe_json_load(self, value):
        try:
            return json.loads(value or "{}")
        except Exception:
            return {}

    # Dashboard views ---------------------------------------------------------
    def action_open_dashboard(self):
        action = self.env.ref("social_media_osint_manager.action_social_media_osint_analysis").read()[0]
        action["context"] = {"search_default_group_by_account_id": 1}
        return action

    def action_generate_dashboard_payload(self):
        payload = [snapshot.to_dashboard_payload() for snapshot in self.search([], limit=50)]
        return payload
