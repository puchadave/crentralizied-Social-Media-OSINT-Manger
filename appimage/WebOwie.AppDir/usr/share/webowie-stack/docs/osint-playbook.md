# OSINT Playbook für Social Media Analysen

Dieser Leitfaden beschreibt, wie du SpiderFoot, n8n, OpenSearch und Open WebUI kombinierst, um Social-Media-Kommentare, Posts und Mentions automatisiert zu erfassen, zu bewerten und zu visualisieren.

## 1. SpiderFoot vorbereiten
1. Melde dich unter `http://localhost:${SPIDERFOOT_HTTP_PORT:-5001}` an.
2. Erstelle unter **Settings → API Keys** einen neuen Key und kopiere ihn.
3. Hinterlege den Key in deiner `.env` Datei als `SPIDERFOOT_API_KEY` und passe bei Bedarf `SPIDERFOOT_BASE_URL` an (Standard: `http://spiderfoot:5001`). Nach einem `docker compose up -d` stehen die Werte n8n Workflows als `{{$env.SPIDERFOOT_API_KEY}}` bzw. `{{$env.SPIDERFOOT_BASE_URL}}` zur Verfügung.
4. Lege Scans für relevante Ziele an (z. B. Hashtags, Unternehmensnamen, Domains, Social-Media-Profile).

## 2. n8n Workflow: SpiderFoot → OpenSearch
1. Starte `http://localhost:5678` und aktiviere Basic Auth mit den `.env` Zugangsdaten.
2. Erzeuge einen **HTTP Request**-Node, der `GET {{ $env.SPIDERFOOT_BASE_URL }}/api/v1/scan/list?api_key={{ $env.SPIDERFOOT_API_KEY }}` aufruft, um abgeschlossene Scans abzuholen.
3. Ergänze einen **Function**-Node, der die Findings nach Social-Media-Quellen filtert (z. B. Module `sfp_twitter`, `sfp_reddit`, `sfp_youtube`).
4. Speichere Treffer mit dem **OpenSearch**-Node in einem Index wie `social_intel-*` (Host: `${OPENSEARCH_HOST}` aus der n8n-Umgebung).
5. Plane den Workflow mit einem **Cron**-Trigger, damit neue SpiderFoot-Ergebnisse automatisiert landen.

## 3. Visualisierung in OpenSearch Dashboards
1. Öffne `http://localhost:${OPENSEARCH_DASHBOARDS_PORT:-5601}` und füge den Index `social_intel-*` als Data View hinzu.
2. Baue Visualisierungen für:
   - Mention-Volumen pro Plattform (Bar/Line Chart)
   - Reichweiten-Schätzung (`followers`, `views`, `subscribers` Felder)
   - Sentiment-Score (falls im Workflow berechnet)
   - Geo-Karten (falls SpiderFoot Geo-Informationen liefert)
3. Stelle ein Dashboard „Social OSINT Overview“ zusammen und binde es in Appsmith ein (Widget → iFrame) oder exportiere als PNG/PDF für Reports.

## 4. KI-gestützte Auswertung
1. Richte in n8n einen weiteren Workflow ein, der neue Findings aus OpenSearch abfragt.
2. Übergib die Texte (Kommentare, Post-Inhalte) an einen **OpenAI**- oder **Open WebUI**-Node für Summaries, Sentiment oder Handlungs-Empfehlungen.
3. Speichere die Ergebnisse wieder in OpenSearch oder sende sie an Slack/Matrix für schnelle Reaktionen.

## 5. Erweiterungen
- Nutze zusätzliche SpiderFoot-Module (z. B. `sfp_tiktok`, `sfp_linkedin`) oder ergänze Airbyte/Meltano-Konnektoren für APIs mit höheren Limits.
- Kombiniere Listmonk/Mautic mit OSINT-Daten, um Influencer:innen oder aktive Community-Mitglieder gezielt anzusprechen.
- Verwende Metabase, um OpenSearch-Daten via PostgreSQL-Gateway (z. B. Logstash Output `jdbc`) in klassische Reports zu übernehmen.

> Dokumentiere deine n8n-Workflows und Dashboard-IDs im Repository (`docs/`) für dein Team.
