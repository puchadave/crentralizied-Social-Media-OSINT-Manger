{
    "name": "Website Appointment Booking",
    "version": "16.0.1.0.0",
    "summary": "Manage appointments and allow website visitors to book slots",
    "category": "Website",
    "license": "LGPL-3",
    "author": "Your Company",
    "depends": ["base", "website"],
    "data": [
        "security/ir.model.access.csv",
        "data/appointment_sequence.xml",
        "views/appointment_menus.xml",
        "views/appointment_service_views.xml",
        "views/appointment_slot_views.xml",
        "views/appointment_booking_views.xml",
        "views/website_templates.xml",
    ],
    "assets": {
        "website.assets_frontend": [
            "website_appointment_booking/static/src/js/appointment_booking.js",
        ],
    },
    "installable": True,
    "application": True,
}
