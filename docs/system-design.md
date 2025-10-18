# System Design Blueprint

## 1. Domänen & Bounded Contexts

| Kontext | Verantwortung | Hauptschnittstellen |
| --- | --- | --- |
| **Engage** | Social-Media-Planung, Automatisierung, Monitoring | Social APIs (Meta, X, LinkedIn, TikTok, YouTube) |
| **Create** | KI-basierte Content-Erstellung, Redaktion, Review | OpenAI API, Asset Storage |
| **Reach** | Newsletter & Kampagnen, E-Mail-Client, Automationen | SMTP/IMAP, Postal, CRM |
| **Relate** | CRM, Lead-Management, Sales Funnels | Engage, Reach, Payments |
| **Operate** | Projekt- & Zeitmanagement, Ressourcen, Tickets | Relate, Identity |
| **Commerce** | Wawi, Shopware-Connector, Payments, Lager | Shopware API, Stripe, PayPal, Klarna, Revolut |
| **Finance** | Billing, Buchhaltung, E-Rechnung, Reporting | Commerce, Payments, External Accounting |
| **Intel** | OSINT, SpiderFoot, Ozen, Threat Intelligence | External OSINT APIs, Data Lake |
| **Core** | Identity, Mandanten, Rollen, Audit, Settings | Alle Kontexte |

## 2. Technologie-Stack (Empfehlung)

- **Frontend**: React + TypeScript, Zustand/Redux Toolkit, Tailwind, Vite.
- **APIs**: GraphQL (Apollo Federation) + gRPC interne Services.
- **Backend Services**: Mischung aus Node.js (Automation, Scheduler), Python/FastAPI (AI, ETL), Go (High-Performance-Connectoren).
- **Eventing**: Kafka für Streams, Redis Streams für kurze Workflows.
- **Speicher**:
  - PostgreSQL (OLTP), TimescaleDB-Extension für Zeitreihen.
  - ClickHouse für Analytics, ElasticSearch für Volltext/OSINT.
  - MinIO/S3 für Dateien & KI-Assets.
- **Infrastructure**: Docker Compose (Dev), Helm Charts (Prod), Traefik/NGINX Ingress.

## 3. Integrationsflüsse

### 3.1 Social Posting

1. Content-Redakteur erstellt Kampagne → Create-Service generiert Vorschläge.
2. Workflow Engine fordert Freigaben ein (optional mehrstufig).
3. Engage-Scheduler publiziert Inhalte pro Plattform, überwacht Status, sammelt Engagement-Metriken.
4. KPIs gehen an Analytics Pipeline, triggern Optimierungen.

### 3.2 Newsletter Automatisierung

1. Segmentierung in CRM (Relate) → Zielgruppenliste.
2. Create-Service generiert E-Mail-Content & Betreff-Varianten.
3. Reach-Service führt A/B-Tests durch, verschickt Newsletter, tracked Öffnungen/Klicks.
4. Ergebnisse fließen in Relate und Analytics zurück.

### 3.3 Commerce & Billing

1. Shopware-Events (Produkt, Bestellung) → Commerce-Sync.
2. Lagerbewegungen aktualisieren Wawi; Seriennummern & Chargen werden nachgeführt.
3. Payment-Webhook → Finance-Service erstellt Rechnung, ordnet Transaktion zu, erzeugt E-Rechnung.
4. Buchungen werden in DATEV/lexoffice-kompatible Exporte überführt.

### 3.4 OSINT Insights

1. Intel-Service stößt SpiderFoot/Ozen Scans an (Cron/On Demand).
2. Ergebnisse werden normalisiert, in ElasticSearch/ClickHouse gespeichert.
3. Dashboard zeigt Alerts, Trends, Reputation Scores in Echtzeit.

## 4. Sicherheit & Governance

- **Zero-Trust-Architektur**: mTLS zwischen Services, OPA/Gatekeeper Policies.
- **Auditing**: Alle kritischen Aktionen erzeugen Event-Logeinträge; revisionssichere Speicherung.
- **Datenschutz**: Mandantenisolierung, Verschlüsselung (at rest + in transit), Consent-Management.
- **Compliance**: ISO 27001 Controls, DSGVO, GoBD, eIDAS (für E-Rechnung).

## 5. Entwicklungsprozess

1. **Backlog Refinement** – Epics → User Stories pro Kontext.
2. **Design Reviews** – ADRs (Architecture Decision Records) pro wichtiger Technologieentscheidung.
3. **CI/CD Pipelines** – Tests (Unit, Integration, E2E), Sicherheits-Scans, Infrastructure Tests.
4. **Observability** – Dev-Sandboxes mit zentralem Logging & Metrics.

## 6. Nächste Schritte

1. Repository-Struktur etablieren (`frontend/`, `services/<context>/`, `deploy/compose`, `deploy/k8s`).
2. Basis-Infrastruktur mit Docker Compose & Traefik als Reverse Proxy erstellen.
3. Skeleton-Service pro Kontext (FastAPI/Express) anlegen, CI-Pipeline definieren.
4. Proof-of-Concept: Social Scheduler + OpenAI Content → Demonstrator.
5. Datenmodell-Blueprint (ER-Diagramm) ausarbeiten, Migrationsstrategie festlegen.

### Dev-Sandbox (Ist-Zustand)

Das Repository liefert bereits:

- `docker-compose.yml` mit React-Frontend und Core-FastAPI.
- Healthchecks & Demo-Endpunkte (`/health`, `/modules`).
- Hot-Reload-Workflows (`npm run dev`, `uvicorn --reload`) für lokale Entwicklung außerhalb von Docker.

Nächste Ausbaustufe: Reverse Proxy (Traefik), Persistenzschicht (PostgreSQL/Redis) sowie Identity-Service hinzufügen und in Compose aufnehmen.

