# Postiz Social Media Manager for Odoo

Dieses Repository enthält ein Odoo-Addon, das die wichtigsten Funktionen der Plattform Postiz in Odoo nachbildet. Das Modul ermöglicht es Marketing-Teams, Social-Media-Konten zu verbinden, Inhalte zu planen, Veröffentlichungen zu automatisieren und Leistungskennzahlen direkt in Odoo auszuwerten.

## Hauptfunktionen

- **Arbeitsbereiche und Zusammenarbeit** – Organisieren Sie Konten und Mitglieder in Workspaces mit optionalen Freigabeprozessen.
- **Kontenverwaltung** – Verbinden Sie Facebook, Instagram, LinkedIn, X (Twitter), TikTok, YouTube, Pinterest, Mastodon oder eigene APIs und halten Sie Tokens aktuell.
- **Content-Planung** – Erstellen Sie Posts mit Rich-Text-Inhalten, Medienanhängen und kanalabhängigen Zeitplänen. Nutzen Sie Kalender-, Kanban- oder Listenansichten und veröffentlichen Sie Beiträge manuell oder automatisch.
- **Bulk-Aktionen** – Planen oder veröffentlichen Sie mehrere Beiträge gleichzeitig über den integrierten Wizard.
- **Automatische Webhooks und Cronjobs** – Reagieren Sie auf Webhooks von Social-Media-Plattformen und lassen Sie geplante Beiträge sowie Analytics-Synchronisationen automatisch ausführen.
- **Analytics** – Sammeln Sie Kennzahlen wie Impressions, Klicks oder Likes, visualisieren Sie sie in Listen-, Diagramm- oder Pivot-Ansichten und speichern Sie Rohdaten für individuelle Auswertungen.

## Installation

1. Kopieren Sie den Ordner `postiz_odoo_integration` in Ihr Odoo-Addons-Verzeichnis.
2. Aktualisieren Sie die App-Liste in Odoo.
3. Installieren Sie die App **Postiz Social Media Manager** und weisen Sie den Benutzern die Gruppen *Postiz User* bzw. *Postiz Manager* zu.

## Entwicklung

Das Modul nutzt ausschließlich Standard-Bibliotheken sowie das Python-Paket `requests`. Für produktive Umgebungen sollten Sie eigene API-Schlüssel, Webhook-URLs und Sicherheitsmaßnahmen hinterlegen.

## Lizenz

LGPL-3
