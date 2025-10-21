# -*- coding: utf-8 -*-
"""Wizard used to bulk publish or schedule posts."""

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PostizBulkPublishWizard(models.TransientModel):
    _name = "postiz.bulk.publish.wizard"
    _description = "Bulk publish wizard"

    post_ids = fields.Many2many("postiz.social.post", string="Posts")
    action_type = fields.Selection(
        [
            ("schedule", "Schedule"),
            ("publish", "Publish now"),
        ],
        required=True,
        default="schedule",
    )
    scheduled_at = fields.Datetime(default=fields.Datetime.now)
    notify_members = fields.Boolean(default=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids")
        if active_ids and "post_ids" in fields_list:
            res["post_ids"] = [(6, 0, active_ids)]
        return res

    def action_apply(self):
        if not self.post_ids:
            raise UserError(_("Please select at least one post."))
        if self.action_type == "schedule":
            for post in self.post_ids:
                post.write({"scheduled_at": self.scheduled_at})
                post.action_schedule()
                if self.notify_members:
                    post.message_subscribe(partner_ids=post.workspace_id.member_ids.mapped("partner_id").ids)
                    post.message_post(body=_("Post rescheduled via bulk wizard."))
        else:
            self.post_ids.action_publish()
        return {"type": "ir.actions.act_window_close"}
