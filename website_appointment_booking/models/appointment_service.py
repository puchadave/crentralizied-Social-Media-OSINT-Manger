from odoo import api, fields, models


class AppointmentService(models.Model):
    _name = "appointment.service"
    _description = "Appointment Service"
    _order = "name"

    name = fields.Char(required=True)
    description = fields.Text()
    duration = fields.Float(
        string="Duration (hours)",
        default=1.0,
        help="Default length of an appointment for this service.",
    )
    active = fields.Boolean(default=True)
    color = fields.Integer()
    slot_ids = fields.One2many("appointment.slot", "service_id", string="Slots")
    next_slot_id = fields.Many2one(
        "appointment.slot",
        compute="_compute_next_slot_id",
        string="Next Available Slot",
    )

    @api.depends("slot_ids.start_datetime", "slot_ids.state")
    def _compute_next_slot_id(self):
        for service in self:
            upcoming_slots = service.slot_ids.filtered(
                lambda slot: slot.state == "open" and slot.start_datetime >= fields.Datetime.now()
            ).sorted(key=lambda slot: slot.start_datetime)
            service.next_slot_id = upcoming_slots[:1].id if upcoming_slots else False
