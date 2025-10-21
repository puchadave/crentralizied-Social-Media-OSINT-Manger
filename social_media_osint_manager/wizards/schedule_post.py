from datetime import timedelta

from odoo import fields, models, _


class SocialMediaScheduleWizard(models.TransientModel):
    _name = "social.media.schedule.wizard"
    _description = "Schedule multiple social media posts"

    post_ids = fields.Many2many("social.media.post", string="Posts", required=True)
    scheduled_date = fields.Datetime(required=True, default=fields.Datetime.now)
    apply_offset = fields.Boolean(default=False)
    offset_hours = fields.Float(default=2.0)

    def action_apply_schedule(self):
        self.ensure_one()
        base_date = self.scheduled_date
        for index, post in enumerate(self.post_ids.sorted("id")):
            publish_date = base_date
            if self.apply_offset:
                publish_date = base_date + timedelta(hours=index * self.offset_hours)
            post.write(
                {
                    "scheduled_date": publish_date,
                    "state": "scheduled",
                }
            )
            post.message_post(
                body=_("Scheduled via wizard for %(date)s", date=publish_date),
            )
        return {"type": "ir.actions.act_window_close"}
