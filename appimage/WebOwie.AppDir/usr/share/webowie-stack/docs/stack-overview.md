# WebOwie Stack – Architektur & Integrationsleitfaden

Dieser Leitfaden hilft dir beim technischen Onboarding des gesamten Docker-Compose-Stacks. Ergänze ihn mit deinen eigenen Projekt-Notizen, sobald du erste Automations und Dashboards in Betrieb genommen hast.

## 1. Infrastruktur & Netzwerke
- **Docker Compose Version 3.9** – alle Dienste laufen im gleichen Bridge-Netzwerk und können sich über Service-Namen erreichen.
- **Reverse Proxy** – optional kannst du Traefik oder Caddy ergänzen, um HTTPS, Routing und zentrale Domains abzubilden.
- **Persistenz** – alle wichtigen Daten liegen in benannten Volumes (siehe `docker-compose.yml`). Plane Backups von MariaDB- und Postgres-Datenbanken sowie Appsmith-, Metabase- und Ollama-Verzeichnissen ein.

## 2. Authentifizierung & Zugriffsmodelle
- **Keycloak** dient als Identity Provider. Aktiviere die OpenID-Clients für Appsmith, n8n, Mautic und ggf. Matomo.
- Typische Rollenstruktur:
  - `webowie-admin` – Vollzugriff auf Keycloak, Appsmith, n8n, Datenbanken.
  - `marketing-lead` – Zugriff auf Appsmith, Matomo, Mautic, Metabase.
  - `content-creator` – Zugriff auf Appsmith, n8n Workflows, Open WebUI.
- Synchronisiere Rollen per n8n (Keycloak API) oder manuell via Admin-Konsole.

## 3. Datenflüsse & Integrationen
1. **Tracking & KPIs**
   - Matomo sammelt Traffic-Daten; Metabase nutzt die Matomo-Datenbank als Quelle für Dashboards.
2. **SEO Monitoring**
   - SEO Panel crawlt Keywords; Ergebnisse können via MySQL-Connector in Appsmith oder Metabase angezeigt werden.
3. **Marketing Automation**
   - Mautic nutzt Redis als Cache und spricht mit externen Kanälen (E-Mail, Social APIs, Webhooks).
4. **Newsletter**
   - Listmonk verwaltet Abonnent:innen und sendet Kampagnen; n8n kann Kontakte aus Mautic synchronisieren.
5. **Content-Automatisierung**
   - n8n orchestriert Content-Pipelines, triggert Open WebUI/Ollama, pusht fertige Inhalte an Mautic, Listmonk oder Social APIs.
6. **OSINT & Social Listening**
   - SpiderFoot scannt Social-Media-Profile, Kommentare und Erwähnungen; n8n ruft die API ab und legt Ergebnisse in OpenSearch ab.
   - OpenSearch Dashboards visualisieren Reichweiten, Sentiment und Erwähnungen; Appsmith kann Dashboards per iFrame oder REST einbinden.

## 4. Empfohlene Erstkonfiguration
1. **Keycloak Realm anlegen** (`webowie`), Clients für Appsmith, n8n, Mautic erstellen.
2. **Appsmith** starten, Datenquellen für Matomo (MySQL), SEO Panel (MySQL), Mautic (REST), Listmonk (Postgres) hinzufügen.
3. **Metabase** mit Datenbanken verbinden: Matomo (MariaDB), Mautic (MariaDB), Listmonk (Postgres).
4. **n8n** konfigurieren: Credentials für Social-Netzwerk-APIs (LinkedIn, Meta, X, Reddit, etc.) und Open WebUI.
5. **Open WebUI**: gewünschte Ollama-Modelle (`ollama run llama3:8b`, `ollama pull mistral`) vorinstallieren.
6. **Mautic**-Cronjobs prüfen (`docker compose logs mautic`), Kanäle einrichten (E-Mail, Social, Push).

## 5. Automatisierungs-Beispiele
- **Crossposting-Pipeline**
  1. Appsmith-Formular → n8n Webhook → Prompt-Generierung in Open WebUI → Asset-Review in Appsmith → Veröffentlichung via Social APIs.
- **SEO Alerting**
  1. Cron in SEO Panel → Export in Datenbank → n8n Job prüft Veränderungen → Slack/Matrix/Teams Alarm via Webhook.
- **Newsletter-Automation**
  1. Matomo Segment → n8n synchronisiert Kontakte nach Listmonk → Automatischer Versand neuer Kampagne.
- **OSINT Monitoring & Reichweite**
  1. SpiderFoot-Scan → n8n extrahiert Findings → Speicherung in OpenSearch → OpenSearch Dashboards & Metabase zeigen Reichweiten-, Sentiment- und Quellen-Statistiken.

## 6. Betrieb & Observability
- Aktiviere Healthchecks (bereits für Datenbanken vorhanden) auch für weitere Dienste via Compose.
- Nutze `docker compose logs -f <service>` für Echtzeit-Fehleranalyse.
- Ergänze nach Bedarf einen Monitoring-Stack (Prometheus, Grafana, Loki) für tiefergehende Auswertungen.

## 7. Sicherheit
- Setze in `.env` ausschließlich starke Passwörter / Secrets.
- Hinterlege TLS-Zertifikate über Reverse Proxy.
- Aktiviere Zwei-Faktor-Authentisierung in Keycloak.
- Nutze Security-Updates der Images (`docker compose pull`) regelmäßig.

## 8. Weiterführende Ideen
- Headless CMS (z. B. Strapi) anbinden, um Content-Quellen zu zentralisieren.
- Social Listening mit zusätzlichen Datenquellen (Airbyte, Meltano) erweitern und in Appsmith visualisieren.
- Experimentiere mit KI-gesteuerten Workflows (z. B. automatische Video-Zusammenfassungen via ffmpeg + Whisper + Ollama).

> Dokumentiere jede Änderung im `docs/` Ordner, damit dein Team den Wissenstransfer nachvollziehen kann.
