# Centralized Social Media & OSINT Manager

Eine ganzheitliche Plattform, die Social-Media-Orchestrierung, OSINT, CRM/ERP, Automatisierung und KI-gestützte Content-Erstellung in einem vollständig personalisierbaren Web-Dashboard vereint.

## Vision

> "Alles können. Alles schaffen. Maximale Kontrolle."

Die Lösung bündelt sämtliche Kommunikations- und Vertriebskanäle sowie operative Prozesse in einem modularen, containerisierten Stack. Repetitive Aufgaben werden durch KI und Automatisierung übernommen, während Echtzeit-Insights fundierte Entscheidungen ermöglichen.

## Gesamtarchitektur

```
┌──────────────────────────────┐
│         Web Frontend         │
│ (React/Vue, Theme Engine)    │
│ Dashboard · Planner · CRM    │
└──────────────┬───────────────┘
               │GraphQL/REST
┌──────────────▼───────────────┐
│        API Gateway           │
│ Auth · Routing · Rate Limits │
└──────────────┬───────────────┘
      Event Bus│(Kafka/RabbitMQ)
┌──────────────▼───────────────┐
│       Microservice Mesh       │
│ Social Automation · CRM/ERP   │
│ E-Commerce · OSINT · AI Ops   │
└──────────────┬───────────────┘
               │PostgreSQL, Redis
┌──────────────▼───────────────┐
│   Data Lake & Analytics      │
│  (ClickHouse, Grafana, ELK)  │
└──────────────────────────────┘
```

Alle Komponenten laufen in Docker-Containern (Compose oder Swarm/Kubernetes) und lassen sich über Infrastructure-as-Code provisionieren.

## Kernmodule

| Domäne | Funktionsumfang | Technologie-Vorschlag |
| --- | --- | --- |
| **Frontend/UI** | Echtzeit-Dashboard, Kanban/Gantt, Kalender, White-Labeling | React/Vue, Tailwind, Socket.IO/GraphQL Subscriptions |
| **Identity & Access** | SSO, RBAC, Mandantenfähigkeit | Keycloak/Ory |
| **Social Automation** | Post-Planung, Cross-Posting, Monitoring | Node.js/TypeScript Services, CRON/Scheduler |
| **KI Content Engine** | Prompt-Templates, Auto-Generierung, Redaktions-Workflow | Python/FastAPI, OpenAI API, LangChain |
| **E-Mail Marketing** | Client, Kampagnen, Automationen, Newsletter mit KI | Postal/Mailhog (Dev), Integration in Content Engine |
| **CRM/ERP** | Kontakte, Projekte, Personal, Zeit, Billing, E-Rechnung | Odoo/Dolibarr-Module, Go/Python Services |
| **E-Commerce & Wawi** | Lager, Bestellungen, Shopware Connector, Payments | Python/Go Connector, Stripe/PayPal/Klarna SDKs |
| **OSINT & Security** | SpiderFoot, Ozen-Framework, Datenaufbereitung | Containerisierte Tools, ETL in Data Lake |
| **Automatisierung** | Workflows, Rule Engine, Notifications | Temporal.io/N8N, Redis Queue |
| **Monitoring & Observability** | Metrics, Logs, Audits | Prometheus, Grafana, Loki/Elastic |

## Daten- & Integrations-Strategie

1. **Gemeinsames Datenmodell** in PostgreSQL mit getrennten Schemas pro Domäne und einer zentralen Event-Sourcing-Schicht.
2. **CDC & Sync Jobs** zwischen Wawi und Shopware (REST/GraphQL), inkl. Mapping-Templates für Artikeltabellen und Lagerbestände.
3. **Payment Webhooks** (Stripe, PayPal, Revolut, Klarna) triggern Rechnungs- und Buchungsservices. E-Rechnungen (XRechnung/ZUGFeRD) werden automatisch erzeugt.
4. **OpenAI Content Pipelines** generieren Posts/Newsletter, führen QA-Checks durch und übergeben den Content an Scheduler bzw. E-Mail-Marketing.
5. **OSINT Aggregation** nutzt SpiderFoot & Ozen, speichert Ergebnisse im Data Lake und spielt sie ins Dashboard.

## Frontend-Personalisierung

- Theme-Konfiguration (JSON/YAML) mit Farben, Logo, Layout-Varianten.
- Modulbasierte Navigation – Administratoren aktivieren/deaktivieren Features mandantenweise.
- Widgets lassen sich per Drag & Drop anpassen; Zustand wird benutzerbezogen gespeichert.

## Automatisierung & KI

- **Workflow Engine:** Geschäftsregeln (z. B. "neuer Lead" → "erstelle Aufgabe" → "sende Follow-up") als deklarative Pipelines.
- **Agentenbasierte Content-Produktion:** Prompt-Bibliothek, Mehrstufen-GPT-Checks (Entwurf → Review → Tone of Voice → Finalisierung).
- **Smart Scheduling:** Optimiert Post-Zeitpunkte anhand vergangener Performance und Zielgruppenaktivität.

## Sicherheit & Compliance

- Mandantenfähige Rechteverwaltung, Audit-Trails, DSGVO-konforme Datenaufbewahrung.
- Secrets Management via Vault/SOPS; Ende-zu-Ende TLS (LetsEncrypt/ACME).
- E-Rechnungen durch zertifiziertes Modul, automatisierte Archivierung & Export.

## Infrastruktur-Stack (Vorschlag)

- **Orchestrierung:** Docker Compose → Swarm/K8s (optional)
- **CI/CD:** GitHub Actions + ArgoCD/Fleet
- **IaC:** Terraform (Cloud-Ressourcen), Ansible (Provisioning)
- **Storage:** S3-kompatibel (Backups, Assets), MinIO lokal

## Roadmap (High-Level)

1. **Discovery & Domain-Cut** – Epics definieren, Bounded Contexts festlegen.
2. **PoC Phase** – MVP für Social Scheduler, KI-Content, CRM-Basis.
3. **Integrationsphase** – Wawi/Shopware-Sync, Payment-Automation, E-Rechnung.
4. **OSINT & Analytics** – SpiderFoot/Ozen anbinden, Dashboards aufbauen.
5. **Hardening & Skalierung** – Sicherheit, Observability, Mandantenfähigkeit.

## Schnellstart

Dieses Repository enthält einen lauffähigen, dockerisierten Einstieg mit zwei Services:

- **Frontend** (`frontend/`): Vite + React UI mit Demo-Dashboard.
- **Core API** (`services/core-api/`): FastAPI-Service mit Health- und Modulendpunkten.

### Voraussetzungen

- Docker & Docker Compose v2
- Node.js 18+ (nur erforderlich, wenn du das Frontend außerhalb von Docker entwickeln willst)

### Docker-Umgebung prüfen

Falls `docker compose` auf deinem System mit einer Fehlermeldung abbricht (z. B. weil das Compose-Plugin fehlt oder der Daemon nicht läuft), hilft der folgende Check:

```bash
./verify-docker-env.sh
```

Das Skript prüft, ob Docker-CLI, Daemon und Compose (v2 oder v1) korrekt installiert sind und gibt konkrete Hinweise zur Fehlerbehebung. In restriktiven Umgebungen (z. B. Sandboxen oder CI ohne Daemon) beendet es sich trotzdem mit Exit-Code `0`, damit dein Setup nicht gestoppt wird; verwende optional `./verify-docker-env.sh --strict`, wenn fehlende Komponenten einen Fehler provozieren sollen.

Auf Debian/Ubuntu-Systemen installiert man das Compose-Plugin beispielsweise mit:

```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin
```

Alternativ steht weiterhin das klassische `docker-compose` (v1) zur Verfügung:

```bash
sudo apt-get install docker-compose
```

### Stack starten

```bash
git clone https://github.com/<dein-account>/crentralizied-Social-Media-OSINT-Manger.git
cd crentralizied-Social-Media-OSINT-Manger
docker compose up --build
```

Anschließend erreichst du:

- Frontend: http://localhost:5173
- Core API: http://localhost:8000/docs (Swagger UI)

Zum Stoppen nutze `docker compose down`. Für lokale Entwicklung kannst du das Frontend auch direkt starten:

```bash
cd frontend
npm install
npm run dev
```

Die API startet lokal mit `uvicorn`:

```bash
cd services/core-api
uvicorn main:app --reload --port 8000
```

> **Tipp:** In stark eingeschränkten Containern oder CI-Umgebungen ohne Docker-Daemon lässt sich der Stack nicht bauen. Nutze in diesem Fall die lokalen Dev-Befehle (`npm run dev`, `uvicorn ...`) oder setze Docker auf einem Host-System/VM mit vollständigen Kernel-Rechten auf.

---

Dieses Repository dient als Ausgangspunkt. Weitere Verzeichnisse (z. B. `frontend/`, `services/`, `deploy/`) können gemäß obiger Architektur angelegt und iterativ mit Leben gefüllt werden.

