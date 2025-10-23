# Realtime Social Media Marketing OSINT Manager

Ein modular aufgebautes OSINT-, SEO- und Marketing-Command-Center für Social Media Teams.
Das System analysiert Erwähnungen in Echtzeit, generiert KI-gestützten Content, optimiert
Metadaten für gängige CMS-Plattformen und bietet automatisierte Playbooks für Marketing-Teams.

## Features

- **Echtzeit-OSINT**: WebSocket-Stream für Social-Media-Ereignisse mit Sentiment- und
  Tag-Analyse.
- **SEO Intelligence**: On-Demand On-Page-Checks mit Meta-Optimierung und CMS-Bridges
  für WordPress, Ghost und Odoo.
- **Content Hub**: Zentrale Content-Bibliothek, KI-generierte Captions, Zielnetzwerk-Übersicht
  und KI-gesteuertes Multi-Publishing.
- **Marketing Insights**: Automatisierte Empfehlungen für Posting-Zeitpunkte und
  Kampagnen-Health.
- **Automatisierung**: Regel-Engine, die auf OSINT- oder SEO-Ereignisse reagiert.
- **Analytics Hub**: Vollwertiger Ersatz für Google Analytics & Search Console mit KPIs,
  Traffic-Breakdown und Echtzeit-Engagement.
- **Mandanten & Abrechnung**: Multi-Site- und Kundenverwaltung inkl. Google-Ads-Budgets,
  Rechnungslegung, KPI-Auswertung und KI-basierter Angebotskalkulation pro Minute.
- **Visualisierung & Web-GUI**: Einseitiges Control-Center mit KPI-Cards, Live-OSINT-Stream,
  Content Hub, Mandanten- und Billing-Workflow sowie SEO-Analyse.

## Architektur

```
FastAPI (REST & WebSocket)
├── Routers: /osint, /seo, /content, /automation, /analytics, /clients, /billing
├── Services: OSINTStream, SEOOptimizer, MarketingOptimizer, ContentHub,
│            SocialNetworkRouter, Dashboard Analytics, AutomationEngine,
│            ClientPortfolioManager, BillingEngine
├── CMS-Connectoren: WordPress, Ghost, Odoo (API-basiert)
└── SQLModel + SQLite: Persistenzschicht für Events, Content, Analytics, SEO-Reports,
   Mandanten, Budgets, Rechnungen und Angebote
```

## Schnellstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Öffne anschließend `http://127.0.0.1:8000/` für die vollwertige Web-GUI. Die API bleibt
parallel erreichbar – wichtige Endpunkte:

- `GET /osint/events` – letzte OSINT-Events
- `POST /osint/events` – neue Erwähnungen einspeisen
- `WS /osint/stream` – Echtzeit-Stream
- `POST /seo/analyse?url=` – SEO-Analyse
- `POST /seo/metadata` – Metadaten speichern und optional Richtung CMS pushen
- `GET /content/` – Content-Repository
- `POST /content/generate` – KI-gestützte Content-Erstellung
- `GET /content/destinations` – verfügbare Social & CMS Connectors
- `POST /content/{id}/publish` – KI-Dispatch zu mehreren Netzwerken
- `GET /analytics/overview` – Echtzeit-Dashboard mit KPIs & OSINT
- `GET /analytics/search-console` – Keywords, Klicks, CTR & Positionen
- `GET /analytics/traffic` – Traffic-Breakdown je Quelle
- `GET /analytics/engagement` – 24h-Engagement-Radar
- `GET /clients/` – Mandantenübersicht inkl. Kontaktinformationen
- `POST /clients/{id}/sites` – weitere Sites & Workspaces für einen Kunden anlegen
- `GET /clients/{id}/summary` – KPI-Zusammenfassung aus Budgets, Rechnungen & Proposals
- `GET /billing/budgets` – Kanal- und Kampagnenbudgets mit Spend-Tracking
- `POST /billing/proposals/generate` – Automatische Angebotserstellung nach Minutenpreisen

Demo-Daten werden beim Start automatisch erzeugt (`Settings.enable_demo_data`).

### Web-GUI Überblick

Die Oberfläche bündelt alle Workflows auf einer Seite:

- **Analytics Board**: Sessions, Pageviews, Conversions, Bounce-Rate, Engagement sowie
  Search-Console-Queries und Traffic-Quellen.
- **OSINT Stream**: Live-Table mit WebSocket-Events, Sentiment, Engagement und Tagging.
- **Content Hub**: KI-Themen-Generator, Status-Steuerung und Multi-Channel-Publishing.
- **SEO & Metadata**: Ad-hoc-URL-Analyse samt Issue-/Recommendation-Liste und
  Formular für Meta-Push in angebundene CMS.
- **Mandantenverwaltung**: Anlage von Kunden & Sites inkl. Integrations-Setup und
  zusammengefassten KPIs pro Mandant.
- **Billing Center**: Budgetplanung, Spend-Tracking, Rechnungen, Angebotsgenerator und
  Gesamtübersicht aller finanziellen Artefakte.

### Demo-Daten

Die Seed-Daten erzeugen zwei Beispielkunden (`Digital Growth GmbH` & `Ecom Sprint AG`) mit
mehreren Sites, Google-Ads- und SEO-Budgets, offenen & bezahlten Rechnungen sowie
Angebotsentwürfen. Dadurch lässt sich das Multi-Tenant-Controlling sofort im Dashboard,
über die `/clients`- und `/billing`-APIs sowie in den Analytics-KPIs nachvollziehen.

## Konfiguration

Einstellungen können über Umgebungsvariablen oder eine `.env` Datei angepasst werden.
Wichtige Parameter:

| Variable | Beschreibung | Default |
| --- | --- | --- |
| `DATABASE_URL` | SQLModel Connection String | `sqlite:///./osint_manager.db` |
| `OSINT_REFRESH_INTERVAL` | Hintergrundintervall für Abrufe | `60` |
| `MARKETING_LOOKBACK_HOURS` | Lookback-Fenster für Analysen | `24` |
| `ENABLE_DEMO_DATA` | Seed-Daten beim Start aktivieren | `True` |

## Erweiterungsideen

- Live-Konnektoren zu Twitter, LinkedIn, Mastodon & Reddit.
- Integration eines Message-Brokers (Kafka, Redis Streams) für Skalierung.
- Erweiterte Charting-Widgets (z. B. zusätzliche Diagramme, Drill-Downs) für die bestehende GUI.
- Feinere AI-Modelle (OpenAI, HuggingFace) für Text- und Bild-Generierung.
- Bidirektionale CMS-Synchronisation inkl. Publishing-Workflows.
