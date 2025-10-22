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
- **Visualisierung**: Aggregationen zu Mention-Volumen und Sentiment-Verläufen je Plattform.

## Architektur

```
FastAPI (REST & WebSocket)
├── Routers: /osint, /seo, /content, /automation, /analytics
├── Services: OSINTStream, SEOOptimizer, MarketingOptimizer, ContentHub,
│            SocialNetworkRouter, Dashboard Analytics, AutomationEngine
├── CMS-Connectoren: WordPress, Ghost, Odoo (API-basiert)
└── SQLModel + SQLite: Persistenzschicht für Events, Content, Analytics, SEO-Reports und Regeln
```

## Schnellstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Nach dem Start stehen folgende Komponenten zur Verfügung:

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

Demo-Daten werden beim Start automatisch erzeugt (`Settings.enable_demo_data`).

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
- Dashboard-Frontend mit Echtzeit-Charts (z. B. Streamlit, Next.js).
- Feinere AI-Modelle (OpenAI, HuggingFace) für Text- und Bild-Generierung.
- Bidirektionale CMS-Synchronisation inkl. Publishing-Workflows.
