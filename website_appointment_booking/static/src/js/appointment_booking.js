/** @odoo-module */

/**
 * Handle small UX niceties for the appointment booking form.
 */
odoo.define('website_appointment_booking.booking_form', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.AppointmentBookingForm = publicWidget.Widget.extend({
        selector: '.o_appointment_booking_form',
        events: {
            'change input[name="slot_id"]': '_onSlotChange',
        },

        _onSlotChange: function () {
            const selectedOption = this.el.querySelector('input[name="slot_id"]:checked');
            const summaryTarget = this.el.querySelector('[data-appointment-summary]');
            if (selectedOption && summaryTarget) {
                summaryTarget.textContent = selectedOption.dataset.summary || '';
            }
        },
    });
});
