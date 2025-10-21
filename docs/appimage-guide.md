# WebOwie AppImage Guide

Das WebOwie-AppImage bündelt den Docker-Compose-Stack, das Launch-Skript sowie die Branding-Assets in einer einzigen ausführbaren Datei. Beim Start wird die Stack-Konfiguration automatisch in ein lokales Arbeitsverzeichnis kopiert, sodass du deine `.env` oder zusätzliche Dokumente ohne erneutes Mounten anpassen kannst.

## Voraussetzungen

- 64-Bit-Linux-Distribution
- Docker und Docker Compose (Plugin `docker compose` oder `docker-compose` Binary)
- ca. 10 GB freier Speicherplatz für Container-Images und Daten

## AppImage erstellen

```bash
./appimage/build-appimage.sh
```

Der Build-Prozess erledigt folgende Schritte:

1. Kopiert die vorbereitete `WebOwie.AppDir` in einen temporären Build-Ordner.
2. Synchronisiert `docker-compose.yml`, `.env.example`, `docs/` und `branding/` aus dem Repository.
3. Kopiert den aktuellen `scripts/webowie-launcher.sh` in die AppDir.
4. Lädt bei Bedarf `appimagetool` herunter und erstellt `dist/WebOwie.AppImage`.

> Tipp: Mit der Umgebungsvariable `APPIMAGETOOL_BINARY` kannst du ein bereits vorhandenes `appimagetool` angeben, z. B. aus `/usr/local/bin`.

## Ausführung & Workflow

```bash
./dist/WebOwie.AppImage            # Startet den Stack (docker compose up -d)
./dist/WebOwie.AppImage stop       # docker compose down
./dist/WebOwie.AppImage status     # docker compose ps
./dist/WebOwie.AppImage logs n8n   # docker compose logs -f n8n
./dist/WebOwie.AppImage exec <...> # Beliebige docker compose Argumente
```

Beim ersten Start erzeugt das AppImage automatisch ein Konfigurationsverzeichnis unter:

```
~/.local/share/webowie-stack/
```

Darin findest du u. a.:

- `.env` – Kopie der `.env.example`; hier trägst du Passwörter, URLs und Ports ein.
- `docker-compose.yml` – Compose-Datei, die vom Launcher verwendet wird.
- `docs/`, `branding/` – Referenzdokumente für Workflows und Assets.

Du kannst das Verzeichnis mit `WEBOWIE_RUNTIME_DIR` anpassen, z. B. für portable Installationen auf USB-Sticks:

```bash
WEBOWIE_RUNTIME_DIR="/media/user/WebOwie" ./dist/WebOwie.AppImage start
```

## Integration in Desktop-Umgebungen

- Verschiebe `WebOwie.AppImage` nach `~/Applications` oder `/opt` und mache die Datei ausführbar.
- Optional: erstelle einen Desktop-Eintrag (`~/.local/share/applications/webowie.desktop`) mit dem Befehl `Exec=/pfad/zu/WebOwie.AppImage`.
- Das mitgelieferte Icon (`webowie.svg`) wird automatisch eingebunden.

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| `Docker Compose konnte nicht gefunden werden.` | Stelle sicher, dass `docker compose` oder `docker-compose` im `PATH` liegt. |
| Dienste starten nicht wegen `vm.max_map_count` | Führ `sudo sysctl -w vm.max_map_count=262144` aus, bevor du das AppImage startest. |
| Portkonflikte | Passe die Ports in `~/.local/share/webowie-stack/.env` an und starte neu. |

## Automatisierte Updates

Bei neuen Git-Versionen musst du lediglich `appimage/build-appimage.sh` erneut ausführen. Das Skript synchronisiert automatisch alle relevanten Dateien in die AppDir, bevor die neue Version paketiert wird.

Viel Erfolg beim Einsatz der WebOwie.AppImage!
