from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AppointmentBooking(models.Model):
    _name = "appointment.booking"
    _description = "Appointment Booking"
    _order = "create_date desc"

    name = fields.Char(default=lambda self: self._get_next_reference(), readonly=True)
    slot_id = fields.Many2one(
        "appointment.slot",
        required=True,
        ondelete="restrict",
    )
    service_id = fields.Many2one(
        related="slot_id.service_id",
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one("res.partner", string="Customer")
    partner_name = fields.Char(string="Contact Name")
    partner_email = fields.Char(string="Email")
    partner_phone = fields.Char(string="Phone")
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        required=True,
    )
    notes = fields.Text()
    website_source = fields.Char(string="Website Source")

    _sql_constraints = [
        (
            "slot_partner_unique",
            "UNIQUE(slot_id, partner_email, partner_phone)",
            "This contact already booked the selected slot.",
        )
    ]

    @api.model
    def _get_next_reference(self):
        return self.env["ir.sequence"].next_by_code("appointment.booking") or "New"

    @api.model
    def create(self, vals):
        slot = self.env["appointment.slot"].browse(vals.get("slot_id"))
        if slot and (slot.available_capacity <= 0 or slot.state == "closed"):
            raise ValidationError("The selected slot is no longer available.")
        record = super().create(vals)
        if slot:
            slot.invalidate_cache(["booked_count", "available_capacity", "is_fully_booked"], slot.ids)
            slot.with_context(skip_slot_state_update=True)._update_state()
        return record

    def write(self, vals):
        slots_before = self.mapped("slot_id")
        res = super().write(vals)
        if {"state", "slot_id"} & set(vals.keys()):
            slots = slots_before | self.mapped("slot_id")
            slots.invalidate_cache(["booked_count", "available_capacity", "is_fully_booked"], slots.ids)
            slots.with_context(skip_slot_state_update=True)._update_state()
        return res

    def action_confirm(self):
        for booking in self:
            slot = booking.slot_id
            competing = slot.booking_ids.filtered(
                lambda b: b.id != booking.id and b.state in ("pending", "confirmed")
            )
            if len(competing) >= slot.capacity:
                raise ValidationError("No more places are available for this slot.")
        self.write({"state": "confirmed"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def name_get(self):
        result = []
        for booking in self:
            display = booking.name
            if booking.partner_name:
                display = f"{booking.name} - {booking.partner_name}"
            result.append((booking.id, display))
        return result

    def unlink(self):
        slots = self.mapped("slot_id")
        res = super().unlink()
        if slots:
            slots.invalidate_cache(["booked_count", "available_capacity", "is_fully_booked"], slots.ids)
            slots.with_context(skip_slot_state_update=True)._update_state()
        return res
