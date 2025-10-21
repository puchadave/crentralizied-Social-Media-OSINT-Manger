import logging

from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request


class AppointmentController(http.Controller):

    _logger = logging.getLogger(__name__)

    @http.route([
        "/appointments",
        "/appointments/service/<model('appointment.service'):service>",
    ], type="http", auth="public", website=True)
    def appointments_index(self, service=None, **kwargs):
        services = request.env["appointment.service"].sudo().search([("active", "=", True)])
        slot_domain = [("state", "=", "open"), ("website_published", "=", True)]
        if service:
            slot_domain.append(("service_id", "=", service.id))
        slots = request.env["appointment.slot"].sudo().search(slot_domain, order="start_datetime")
        return request.render(
            "website_appointment_booking.appointment_listing",
            {
                "services": services,
                "slots": slots,
                "selected_service": service,
            },
        )

    @http.route(
        "/appointments/book/<int:slot_id>",
        type="http",
        auth="public",
        website=True,
        methods=["GET", "POST"],
    )
    def appointments_book(self, slot_id, **post):
        Slot = request.env["appointment.slot"].sudo()
        slot = Slot.browse(slot_id).exists()
        if not slot or slot.state != "open" or not slot.website_published or slot.is_fully_booked:
            return request.redirect("/appointments")

        Booking = request.env["appointment.booking"].sudo()
        values = {
            "slot": slot,
            "services": request.env["appointment.service"].sudo().search([("active", "=", True)]),
        }

        if request.httprequest.method == "POST":
            name = post.get("partner_name")
            email = post.get("partner_email")
            phone = post.get("partner_phone")
            notes = post.get("notes")
            try:
                with request.env.cr.savepoint():
                    partner = False
                    Partner = request.env["res.partner"].sudo()
                    if email:
                        partner = Partner.search([("email", "=ilike", email)], limit=1)
                    if not partner and (name or email or phone):
                        partner_vals = {
                            "name": name or email or phone,
                            "email": email,
                            "phone": phone,
                        }
                        partner = Partner.create(partner_vals)

                    booking_vals = {
                        "slot_id": slot.id,
                        "partner_id": partner.id if partner else False,
                        "partner_name": name,
                        "partner_email": email,
                        "partner_phone": phone,
                        "notes": notes,
                        "website_source": post.get("website_source") or request.httprequest.referrer,
                    }
                    booking = Booking.create(booking_vals)
                    booking.action_confirm()
                return request.render(
                    "website_appointment_booking.appointment_confirmation",
                    {
                        "booking": booking,
                        "slot": slot,
                    },
                )
            except ValidationError as error:
                values["error"] = error.args[0] if error.args else str(error)
                values.update(post)
            except Exception:
                self._logger.exception("Unexpected error while processing a website appointment booking")
                values["error"] = _("An unexpected error occurred while creating your booking. Please try again.")
                values.update(post)
        else:
            values.update({
                "partner_name": request.env.user.name if request.env.user != request.env.ref("base.public_user") else "",
                "partner_email": request.env.user.email,
                "partner_phone": request.env.user.phone,
            })

        return request.render("website_appointment_booking.appointment_booking", values)
