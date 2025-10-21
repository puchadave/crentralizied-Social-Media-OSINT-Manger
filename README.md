# Crentralized Social Media OSINT Manager

Eine native Desktop-Anwendung für Linux (Ubuntu/Debian), die Social-Media-Engineering, Content-Management, Marketing-Automatisierung und OSINT-Auswertung in einer Oberfläche bündelt. Die Anwendung wird mit PyQt6 bereitgestellt und bietet einen Überblick über KPI-Dashboards, Content-Bibliothek, Social-Media-Streams und automatisierte Workflows.

## Funktionsüberblick

- **Setup Wizard**: Schritt-für-Schritt-Assistent zur API-Anbindung aller Social-Media-Netzwerke, Medienbibliotheken und des SORA-II-Video-Generators.
- **Dashboard**: Visualisierung wichtiger Kennzahlen (KPI) inklusive Trendverlauf der Engagement-Rate.
- **Content Manager**: Verwaltung sämtlicher Inhalte mit Tags, Zielnetzwerken, Anbindung von Google Photos/Unsplash/Pexels sowie AI-gestützter Text- und SORA-II-Storyboard-Generierung.
- **Web Analytics**: Echtzeitüberblick über Besucher, Conversion-Rate und Sitzungsdauer der eigenen Website inklusive Live-Chart.
- **Außenanalyse**: Live-Monitoring des externen Shares of Voice, Sentiments und Erwähnungen inklusive Echtzeit-Optimierungsempfehlungen für maximale Reichweite.
- **Social Streams**: Überwachung von Posts und Kommentaren aus allen angebundenen Netzwerken (Facebook & Facebook Business, Instagram & Instagram Business, LinkedIn, X, TikTok, YouTube, Mastodon, Snapchat, WhatsApp & WhatsApp Business, Reddit, Medium) mit einem zentralen Feed.
- **Automationen**: Übersicht und Steuerung automatisierter Aufgaben wie Newsletter-Erstellung, Cross-Posting und KPI-Snapshots.
- **SEO Optimierung**: KI-gestützte Empfehlungen, Keyword-Chancen sowie automatische Generierung von Meta-Description und Schema-Markup in Echtzeit.

## Voraussetzungen

- Python 3.11 oder neuer
- Linux Desktop mit X11/Wayland (getestet auf Ubuntu/Debian)
- Optional: Ein OpenAI API Key für die Generierung von Texten (`OPENAI_API_KEY`)

### Python-Abhängigkeiten installieren

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Anwendung starten

```bash
python -m src.main
```

Beim ersten Start wird automatisch ein Beispiel-Datensatz in `~/.crentralized_osint/content.json` angelegt. Eigene Inhalte lassen sich im Content-Manager anlegen; die Daten werden dauerhaft in dieser Datei gespeichert.

## Setup Wizard & Integrationen

Beim Erststart öffnet sich der Wizard und fragt nacheinander die API-Zugänge für alle relevanten Netzwerke sowie Google Photos, Unsplash, Pexels und den SORA-II-Video-Generator ab. Die Daten werden lokal in `~/.crentralized_osint/integrations.json` gespeichert und können jederzeit über **Einstellungen → Setup Wizard erneut ausführen…** angepasst werden.

## OpenAI-Integration konfigurieren

Setzen Sie die folgenden Umgebungsvariablen, um ChatGPT für Content-Vorschläge zu verwenden:

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4o-mini"  # optional
```

Ohne API-Schlüssel arbeitet der Content-Generator im Offline-Modus und liefert Platzhaltertexte, sodass die GUI vollständig nutzbar bleibt.

## Projektstruktur

```
├── data/
│   └── sample_content.json   # Beispiel-Inhalte
├── src/
│   ├── app/                  # GUI-Komponenten
│   ├── core/                 # Fachlogik für Content, Analytics, Automationen, AI
│   └── main.py               # Einstiegspunkt
└── requirements.txt
```

## Nächste Schritte

- Reale API-Anbindungen für jedes Netzwerk ergänzen (Graph API, LinkedIn Marketing Developer Platform, YouTube Data API, Mastodon REST, Reddit API, X API).
- Scheduler/Worker einführen, um Automationen im Hintergrund auszuführen.
- Erweiterte KPI-Berechnung mit echten Datenquellen (z. B. UTM-Tracking, SEA-Metriken).
- Reporting-Export als PDF/CSV direkt aus der GUI.

