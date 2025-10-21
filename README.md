![puchalla.pro logo](branding/puchalla-pro-logo.svg)

# WebOwie Marketing & Automation Stack

Der WebOwie-Stack bündelt alle Bausteine, die ein Social Media & Marketing Specialist für Analyse, Kampagnensteuerung und Content-Automatisierung benötigt – inklusive deiner **puchalla.pro** Brand Identity.

> **Kurzüberblick**
> - KPI- und Besuchsanalysen mit Matomo & Metabase
> - Keyword- & SERP-Monitoring via SEO Panel
> - Kampagnen-, Social- & Newsletter-Automatisierung mit Mautic, n8n und Listmonk
> - Single-Sign-On über Keycloak
> - Low-Code-Dashboard für die „WebOwie“-Oberfläche mit Appsmith
> - KI-Unterstützung durch Open WebUI + Ollama für Content- und Newsletter-Generierung
> - OSINT Social Listening & Reichweiten-Monitoring mit SpiderFoot + OpenSearch Dashboards

---

## Projektstruktur

```
├── branding/
│   └── puchalla-pro-logo.svg   # Logo für WebOwie & Branding
├── docs/                       # Platz für Architektur- & Workflow-Dokumentation
├── docker-compose.yml          # Multi-Service-Stack
├── .env.example                # Beispiel-Umgebungsvariablen
└── README.md                   # Diese Datei
```

## Schnellstart

1. **Konfiguration anpassen**
   ```bash
   cp .env.example .env
   # Danach alle Passwörter, Domains, Ports & Secrets im neuen .env anpassen
   ```

2. **Container bauen und starten**
   ```bash
   docker compose pull
   docker compose up -d
   ```

   > **Hinweis:** Für OpenSearch ist auf Linux-Hosts `sudo sysctl -w vm.max_map_count=262144` erforderlich, bevor du den Stack startest.

3. **Erstkonfiguration durchführen**
   | Service          | Adresse                       | Zweck |
   |------------------|-------------------------------|-------|
   | Keycloak         | http://localhost:${KEYCLOAK_HTTP_PORT:-8080} | Benutzer & Rollen anlegen, SSO konfigurieren |
   | Appsmith         | http://localhost:${APPSMITH_HTTP_PORT:-8085} | WebOwie-Dashboards & Formulare bauen |
   | Matomo           | http://localhost:4000         | Tracking-Setup und KPI-Widgets |
   | SEO Panel        | http://localhost:${SEOPANEL_HTTP_PORT:-8020} | Keyword- & SERP-Analysen |
   | Mautic           | http://localhost:8050         | Kampagnen-, Social- & Newsletter-Automatisierung |
   | n8n              | http://localhost:5678         | Workflow-Orchestrierung & Crossposting |
   | Listmonk         | http://localhost:9000         | Newsletter-Verwaltung |
   | Metabase         | http://localhost:${METABASE_HTTP_PORT:-3030} | KPI-Dashboards & Reporting |
   | Open WebUI       | http://localhost:${OPEN_WEBUI_PORT:-3000} | KI-gestützte Content-Generierung |
   | SpiderFoot       | http://localhost:${SPIDERFOOT_HTTP_PORT:-5001} | OSINT-Scans & Social-Media-Recherche |
   | OpenSearch       | http://localhost:${OPENSEARCH_HTTP_PORT:-9200} | OSINT-Datenablage & API |
   | OpenSearch Dashboards | http://localhost:${OPENSEARCH_DASHBOARDS_PORT:-5601} | Visualisierung & Social Listening |

---

## Service-Highlights

### Zentralisierung mit Appsmith (WebOwie)
* Verbinde Appsmith mit den REST-APIs von Matomo, Mautic, n8n und Listmonk.
* Baue Widgets für Kampagnenstatus, Redaktionskalender und Content-Review an einer Stelle.
* Nutze Keycloak als SSO-Provider (OpenID Connect) und erstelle rollenbasierte Zugriffe für Social Media Team, SEO Analyst:innen und Management.

### Social-, SEO- & Newsletter-Automation
* **Mautic** deckt Kampagnen, Lead-Scoring, Social Monitoring und Automations ab.
* **n8n** orchestriert deine Crossposting-Flows: Prompt → KI-Text/Bild → Freigabe → Scheduling → Publish.
* **Listmonk** übernimmt Serienmails, Newsletter und RSS-zu-E-Mail-Strecken.

### Analytics & Reporting
* **Matomo** dient als datenschutzfreundliche Alternative zu Google Analytics.
* **SEO Panel** liefert Keyword- und Wettbewerbs-Metriken.
* **Metabase** aggregiert Daten aus den Datenbanken der Dienste (Postgres/MariaDB) und visualisiert KPI-Boards, Funnels und OKRs.

### OSINT Social Media Intelligence
* **SpiderFoot** durchsucht Social-Media-Profile, Kommentare, Mentions und Whois/Netzwerkdaten vollautomatisch.
* Ergebnisse kannst du via SpiderFoot-API oder CSV-Export in **n8n** Workflows einspeisen.
* **OpenSearch** fungiert als Data Lake für strukturierte Social Listening-Daten (z. B. Reddit-Threads, YouTube-Kommentare, TikTok-Statistiken).
* **OpenSearch Dashboards** zeigen Reichweiten-Trends, Sentiment-Analysen und Mention-Heatmaps; zusätzlich kannst du die Daten in Appsmith/Metabase spiegeln.
* Trage den in SpiderFoot erzeugten API-Key in `.env` (`SPIDERFOOT_API_KEY`) ein, damit n8n ihn über `{{$env.SPIDERFOOT_API_KEY}}` nutzen kann.
* Ausführliche Schritt-für-Schritt-Workflows findest du im [OSINT Playbook](docs/osint-playbook.md).

### KI-gestützte Content-Produktion
* **Open WebUI** + **Ollama** stellen lokale Sprachmodelle (z. B. Llama 3, Mistral) bereit.
* n8n kann Open WebUI- oder OpenAI-Prompts triggern, Assets erzeugen und an Mautic/Listmonk übergeben.
* Hinterlege Prompt-Vorlagen in Appsmith, damit dein Team wiederverwendbare Content-Briefs hat.

---

## Persistenz & Backups
Alle Services schreiben in Docker-Volumes (siehe `docker-compose.yml`). Für Produktivbetrieb empfiehlt sich:

- regelmäßige Dumps der MariaDB- und Postgres-Container (`matomo-db`, `mautic-db`, `listmonk-db`, `keycloak-db`)
- Sicherung der Verzeichnisse `appsmith-stacks`, `metabase-data`, `open-webui-data`, `ollama-data`
- Optional: externe Object Storage Backups via n8n-Workflows

---

## Nächste Schritte

1. **Appsmith als WebOwie-Dashboard konfigurieren** – Widgets, Auth mit Keycloak und Datenquellen verbinden.
2. **n8n-Workflows modellieren** – von Content-Briefing bis Auto-Publishing in Social Networks, inklusive QA-Schleifen.
3. **KI-Modelle in Ollama installieren** – z. B. `ollama run llama3` für schnelle Textgenerierung.
4. **Monitoring & Alerts** – Mautic- und Matomo-Events mit n8n verknüpfen, Slack/Matrix/Teams Alerts ausspielen.
5. **Branding einbinden** – Logo (`branding/puchalla-pro-logo.svg`) in Appsmith, Landingpages, Newsletter-Templates verwenden.

Viel Erfolg beim Aufbau deiner zentralisierten Marketing-Plattform!
