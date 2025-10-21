# Centralized Social Media OSINT Manager

Dieses Repository enthält ein Odoo-Modul zur Terminverwaltung inklusive Website-Integration.

## Modul: `website_appointment_booking`

### Funktionsumfang

* Verwaltung von angebotenen Leistungen (Dauer, Beschreibung, Aktivität).
* Planung einzelner Terminslots mit Kapazitätsverwaltung und Veröffentlichung auf der Website.
* Erfassung von Buchungen mit automatischer Vergabe einer Referenznummer sowie Statusverwaltung (ausstehend, bestätigt, storniert).
* Öffentliche Website-Seiten zur Anzeige freier Termine und zur Online-Buchung inklusive Bestätigungsseite.
* Automatische Erstellung bzw. Verknüpfung von Kontakten anhand der eingegebenen Kundendaten.

### Installation

1. Das Verzeichnis `website_appointment_booking` in ein Odoo-Addons-Verzeichnis kopieren oder per Pfad einbinden.
2. Den Odoo-Server neu starten und die App-Liste aktualisieren.
3. Das Modul **Website Appointment Booking** installieren.

Nach der Installation stehen im Backend die Menüpunkte **Services**, **Slots** und **Bookings** zur Verfügung. Website-Besucher können freie Slots unter `/appointments` einsehen und direkt buchen.
