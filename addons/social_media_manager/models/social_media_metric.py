from odoo import api, fields, models


class SocialMediaMetric(models.Model):
    _name = "social.media.metric"
    _description = "Social Media Metric"
    _order = "metric_date desc"

    account_id = fields.Many2one(
        "social.media.account",
        required=True,
        ondelete="cascade",
    )
    metric_date = fields.Datetime(required=True, default=fields.Datetime.now)
    campaign_id = fields.Many2one("marketing.campaign")
    post_id = fields.Many2one("social.media.post")
    follower_count = fields.Integer()
    engagement_rate = fields.Float(digits=(16, 4))
    impressions = fields.Integer()
    clicks = fields.Integer()
    shares = fields.Integer()
    comments = fields.Integer()
    conversions = fields.Integer()
    spend = fields.Float()
    cpc = fields.Monetary(
        string="Cost per Click",
        currency_field="currency_id",
        compute="_compute_cpc",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    @api.depends("clicks", "spend")
    def _compute_cpc(self):
        for metric in self:
            metric.cpc = metric.clicks and (metric.spend or 0.0) / metric.clicks or 0.0

    def get_dashboard_data(self, date_from=None, date_to=None, account_ids=None):
        domain = []
        if date_from:
            domain.append(("metric_date", ">=", date_from))
        if date_to:
            domain.append(("metric_date", "<=", date_to))
        if account_ids:
            domain.append(("account_id", "in", account_ids))
        metrics = self.search(domain)
        totals = {
            "followers": sum(metrics.mapped("follower_count")),
            "engagement": sum(metrics.mapped("engagement_rate")) / (len(metrics) or 1),
            "impressions": sum(metrics.mapped("impressions")),
            "clicks": sum(metrics.mapped("clicks")),
            "conversions": sum(metrics.mapped("conversions")),
            "spend": sum(metrics.mapped("spend")),
        }
        return {
            "totals": totals,
            "by_account": {
                metric.account_id.id: {
                    "name": metric.account_id.name,
                    "platform": metric.account_id.platform,
                    "followers": metric.follower_count,
                    "engagement": metric.engagement_rate,
                    "impressions": metric.impressions,
                    "clicks": metric.clicks,
                }
                for metric in metrics
            },
        }
