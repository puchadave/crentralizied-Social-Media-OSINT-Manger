# Centralized Social Media OSINT Manager

Dieses Repository stellt einen Docker-Compose-Marketing-Stack bereit, der verschiedene Open-Source-Tools für Analytics, Automatisierung, Kampagnenmanagement und KI kombiniert. Die bereitgestellte `docker-compose.yml` orchestriert unter anderem Matomo, Listmonk, SEO Panel, Open WebUI, n8n, Metabase, Mautic, Keycloak, OpenSearch, Spiderfoot, Postiz sowie eine zentrale Heimdall-Übersichtsseite.

## Voraussetzungen
- Docker und Docker Compose v2
- Ausreichende Ressourcen (mindestens 16 GB RAM empfohlen)
- Offen gelegte Ports entsprechend der Services (siehe Compose-Datei)

## Verwendung
1. Passen Sie bei Bedarf die Zugangsdaten in der `docker-compose.yml` an (z. B. Passwörter, Zeitzone, Ports).
2. Optional: Ergänzen Sie die Heimdall-Konfiguration unter `config/heimdall/config.json`, um eigene Links oder Kategorien hinzuzufügen.
3. Starten Sie den Stack:
   ```bash
   docker compose up -d
   ```
4. Öffnen Sie Heimdall unter [http://localhost:8084](http://localhost:8084), um Schnellzugriffe auf alle Dienste zu erhalten.

## Enthaltene Services (Auszug)
- **Matomo** – Web Analytics
- **Listmonk** – Newsletter- und Kampagnenverwaltung
- **SEO Panel** – SEO-Monitoring
- **Open WebUI & Ollama** – LLM-Interface inkl. lokaler Modelle
- **n8n** – Automatisierungs-Workflows
- **Metabase** – Business-Intelligence-Dashboards
- **Mautic** – Marketing-Automation
- **Keycloak** – Identity & Access Management
- **OpenSearch & Dashboards** – Suche und Log-Analyse
- **Postiz** – Social-Media-Planung
- **Spiderfoot** – OSINT-Scanner
- **Heimdall** – Zentrales Portal mit vorkonfiguriertem Dashboard

> **Hinweis:** Die Standard-Zugangsdaten und Passwörter dienen nur als Beispiel. Ändern Sie diese unbedingt vor dem produktiven Einsatz.
