from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AppointmentSlot(models.Model):
    _name = "appointment.slot"
    _description = "Appointment Slot"
    _order = "start_datetime"

    name = fields.Char()
    service_id = fields.Many2one(
        "appointment.service",
        required=True,
        ondelete="cascade",
    )
    start_datetime = fields.Datetime(required=True)
    end_datetime = fields.Datetime(required=True)
    capacity = fields.Integer(default=1)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open"),
            ("closed", "Closed"),
        ],
        default="draft",
        required=True,
    )
    website_published = fields.Boolean(
        string="Publish on Website",
        help="When enabled the slot will be available for booking from the website.",
    )
    booking_ids = fields.One2many("appointment.booking", "slot_id", string="Bookings")
    booked_count = fields.Integer(
        compute="_compute_booking_statistics",
        store=True,
    )
    available_capacity = fields.Integer(
        compute="_compute_booking_statistics",
        store=True,
    )
    is_fully_booked = fields.Boolean(
        compute="_compute_booking_statistics",
        store=True,
    )

    @api.depends("booking_ids.state", "capacity")
    def _compute_booking_statistics(self):
        for slot in self:
            confirmed = slot.booking_ids.filtered(lambda b: b.state in ("confirmed", "pending"))
            slot.booked_count = len(confirmed)
            slot.available_capacity = max(slot.capacity - slot.booked_count, 0)
            slot.is_fully_booked = slot.available_capacity == 0

    @api.constrains("start_datetime", "end_datetime")
    def _check_chronology(self):
        for slot in self:
            if slot.start_datetime and slot.end_datetime and slot.start_datetime >= slot.end_datetime:
                raise ValidationError("The slot end time must be after the start time.")

    @api.constrains("capacity")
    def _check_capacity(self):
        for slot in self:
            if slot.capacity < 1:
                raise ValidationError("A slot must allow at least one attendee.")

    @api.model
    def create(self, vals):
        service_id = vals.get("service_id")
        start_dt = vals.get("start_datetime")
        if not vals.get("end_datetime") and service_id and start_dt:
            service = self.env["appointment.service"].browse(service_id)
            if service.exists():
                duration = service.duration or 1.0
                vals["end_datetime"] = fields.Datetime.to_datetime(start_dt) + timedelta(hours=duration)
        if not vals.get("name") and service_id and start_dt:
            service = self.env["appointment.service"].browse(service_id)
            if service.exists():
                start = fields.Datetime.to_datetime(start_dt)
                vals["name"] = f"{service.name} - {start.strftime('%Y-%m-%d %H:%M')}"
        slot = super().create(vals)
        slot.with_context(skip_slot_state_update=True)._update_state()
        return slot

    def write(self, vals):
        res = super().write(vals)
        tracked_fields = {"capacity", "booking_ids", "state", "end_datetime", "start_datetime"}
        if not self.env.context.get("skip_slot_state_update") and tracked_fields & set(vals.keys()):
            self.with_context(skip_slot_state_update=True)._update_state()
        return res

    def _update_state(self):
        for slot in self:
            if slot.state == "closed":
                continue
            new_state = "open"
            if slot.is_fully_booked or slot.end_datetime < fields.Datetime.now():
                new_state = "closed"
            slot.with_context(skip_slot_state_update=True).write({"state": new_state})

    def action_open(self):
        self.write({"state": "open"})

    def action_close(self):
        self.write({"state": "closed"})
