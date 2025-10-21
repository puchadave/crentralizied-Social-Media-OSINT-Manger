# Centralized Social Media OSINT Manager

Dieses Projekt stellt den Grundstein für eine Plattform bereit, die automatisiert Social-Media- und Newsletter-Inhalte generiert, Veröffentlichungen plant und Interaktionen im Sinne einer OSINT-Analyse aggregiert.

## Features (aktueller Stand)

- **Content API** – generiert strukturierte Social-Media-Posts, Threads oder Newsletter. Ohne OpenAI-Key wird automatisch ein deterministischer Fallback genutzt.
- **Scheduling API** – speichert geplante Beiträge in einem In-Memory-Store.
- **Monitoring API** – nimmt Interaktionen entgegen, erstellt Reichweiten-Schätzungen und liefert Netzwerkdaten.
- **Test-Suite** – erste Integrationstests zur Absicherung der Kern-Endpunkte.

## Erste Schritte

### Lokale Entwicklung (ohne Container)

1. Abhängigkeiten installieren (empfohlen in einer virtuellen Umgebung):

   ```bash
   pip install -r requirements.txt
   ```

2. Entwicklungsserver starten:

   ```bash
   uvicorn backend.app.main:app --reload
   ```

3. Die OpenAPI-Dokumentation ist anschließend unter `http://127.0.0.1:8000/docs` verfügbar.

### Betrieb mit Docker & Docker Compose

1. Optional einen `.env`-File anlegen, um z. B. den OpenAI-Key für den Container bereitzustellen:

   ```bash
   cat <<'ENV' > .env
   OPENAI_API_KEY=dein-openai-key
   OPENAI_API_BASE=https://api.openai.com/v1
   OPENAI_MODEL=gpt-4o-mini
   ENV
   ```

2. Container bauen und starten:

   ```bash
   docker compose up --build
   ```

   Der FastAPI-Dienst ist danach unter `http://localhost:8000` erreichbar.

3. Container stoppen:

   ```bash
   docker compose down
   ```

### OpenAI-Integration

Falls ein OpenAI API-Key vorhanden ist, kann er als Umgebungsvariable `OPENAI_API_KEY` gesetzt werden. Ohne Key fällt der Generator automatisch auf eine vorgefertigte Vorlage zurück.

### Tests ausführen

```bash
pytest
```
