#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
APPIMAGE_DIR="$ROOT_DIR/appimage"
TEMPLATE_APPDIR="$APPIMAGE_DIR/WebOwie.AppDir"
BUILD_DIR="$APPIMAGE_DIR/build"
APPDIR="$BUILD_DIR/WebOwie.AppDir"
DIST_DIR="$ROOT_DIR/dist"
OUTPUT_APPIMAGE="$DIST_DIR/WebOwie.AppImage"

sync_item() {
  local src="$1" dst="$2"
  if command -v rsync >/dev/null 2>&1; then
    if [[ -d "$src" ]]; then
      rsync -a --delete "$src/" "$dst/"
    else
      rsync -a "$src" "$dst"
    fi
  else
    if [[ -d "$src" ]]; then
      mkdir -p "$dst"
      cp -a "$src/." "$dst/"
    else
      cp "$src" "$dst"
    fi
  fi
}

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cp -a "$TEMPLATE_APPDIR" "$APPDIR"

sync_item "$ROOT_DIR/docker-compose.yml" "$APPDIR/usr/share/webowie-stack"
sync_item "$ROOT_DIR/.env.example" "$APPDIR/usr/share/webowie-stack"
sync_item "$ROOT_DIR/docs" "$APPDIR/usr/share/webowie-stack/docs"
sync_item "$ROOT_DIR/branding" "$APPDIR/usr/share/webowie-stack/branding"
cp "$ROOT_DIR/scripts/webowie-launcher.sh" "$APPDIR/usr/bin/webowie-launcher"
chmod +x "$APPDIR/usr/bin/webowie-launcher" "$APPDIR/AppRun"

mkdir -p "$DIST_DIR"

APPIMAGETOOL_BINARY="${APPIMAGETOOL_BINARY:-$APPIMAGE_DIR/appimagetool-x86_64.AppImage}"
if [[ ! -x "$APPIMAGETOOL_BINARY" ]]; then
  echo "[WebOwie] Lade appimagetool herunter..."
  curl -L "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
    -o "$APPIMAGETOOL_BINARY"
  chmod +x "$APPIMAGETOOL_BINARY"
fi

"$APPIMAGETOOL_BINARY" "$APPDIR" "$OUTPUT_APPIMAGE"

echo "[WebOwie] AppImage erzeugt: $OUTPUT_APPIMAGE"
