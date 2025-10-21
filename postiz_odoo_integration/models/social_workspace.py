# -*- coding: utf-8 -*-
"""Workspaces replicate the collaborative concept present in Postiz."""

import pytz

from odoo import _, api, fields, models


class PostizSocialWorkspace(models.Model):
    _name = "postiz.social.workspace"
    _description = "Social media workspace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(tracking=True)
    manager_id = fields.Many2one("res.users", tracking=True)
    member_ids = fields.Many2many("res.users", string="Members", tracking=True)
    color = fields.Integer(default=0)
    active = fields.Boolean(default=True)
    default_timezone = fields.Selection(
        selection="_get_timezones",
        default="UTC",
        required=True,
        tracking=True,
        help="Timezone used to compute automatic publishing slots.",
    )
    post_count = fields.Integer(compute="_compute_post_count")
    account_count = fields.Integer(compute="_compute_account_count")
    approval_required = fields.Boolean(
        string="Require approval",
        tracking=True,
        help="If enabled posts must be approved by a manager before publication.",
    )

    def _get_timezones(self):  # pragma: no cover - uses pytz dataset
        return [(tz, tz) for tz in pytz.common_timezones]

    @api.depends("member_ids")
    def _compute_account_count(self):
        account_obj = self.env["postiz.social.account"]
        for workspace in self:
            workspace.account_count = account_obj.search_count([
                ("workspace_id", "=", workspace.id)
            ])

    @api.depends("member_ids")
    def _compute_post_count(self):
        post_obj = self.env["postiz.social.post"]
        for workspace in self:
            workspace.post_count = post_obj.search_count([
                ("workspace_id", "=", workspace.id)
            ])

    def action_view_accounts(self):  # pragma: no cover - UI action
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Social Accounts"),
            "res_model": "postiz.social.account",
            "view_mode": "tree,form",
            "domain": [("workspace_id", "=", self.id)],
        }

    def action_view_posts(self):  # pragma: no cover - UI action
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Social Posts"),
            "res_model": "postiz.social.post",
            "view_mode": "kanban,tree,form,calendar",
            "domain": [("workspace_id", "=", self.id)],
        }

    def action_invite_members(self):
        self.ensure_one()
        template = self.env.ref("mail.mail_notification_light")
        for member in self.member_ids:
            if member == self.env.user:
                continue
            template.send_mail(member.id, force_send=True)

    def toggle_active(self):
        for record in self:
            record.active = not record.active
