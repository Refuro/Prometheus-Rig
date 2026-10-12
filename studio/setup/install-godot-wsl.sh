#!/usr/bin/env bash
# Install Godot (Linux editor binary + export templates) in WSL for headless
# builds and web exports. Free, official downloads from GitHub; no sudo needed.
#
#   bash install-godot-wsl.sh            # installs 4.7.1 (matches the Windows editor)
#   GODOT_VERSION=4.7.2 bash install-godot-wsl.sh
#
# Result:
#   ~/.local/opt/godot/<version>/godot          the binary
#   ~/.local/bin/godot                          symlink (on PATH in Ubuntu by default)
#   ~/.local/share/godot/export_templates/<version>.stable/   templates (web included)
# Download size: ~75 MB editor + ~1.3 GB templates (only kept unpacked, ~1.2 GB).
set -euo pipefail

VER="${GODOT_VERSION:-4.7.1}"
TAG="${VER}-stable"
BASE="https://github.com/godotengine/godot/releases/download/${TAG}"
EDITOR_ZIP="Godot_v${TAG}_linux.x86_64.zip"
TPL="Godot_v${TAG}_export_templates.tpz"
OPT="$HOME/.local/opt/godot/${VER}"
BIN="$HOME/.local/bin"
TPL_DIR="$HOME/.local/share/godot/export_templates/${VER}.stable"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

command -v unzip >/dev/null || { echo "unzip missing: run  sudo apt install -y unzip  then rerun"; exit 1; }
command -v curl >/dev/null || { echo "curl missing: run  sudo apt install -y curl  then rerun"; exit 1; }

echo "== Godot ${VER}: editor binary"
curl -fSL --progress-bar -o "$TMP/$EDITOR_ZIP" "$BASE/$EDITOR_ZIP"
mkdir -p "$OPT" "$BIN"
unzip -o -q "$TMP/$EDITOR_ZIP" -d "$TMP/editor"
install -m 755 "$TMP/editor/Godot_v${TAG}_linux.x86_64" "$OPT/godot"
ln -sf "$OPT/godot" "$BIN/godot"

echo "== Godot ${VER}: export templates (large download)"
curl -fSL --progress-bar -o "$TMP/$TPL" "$BASE/$TPL"
mkdir -p "$TPL_DIR"
unzip -o -q "$TMP/$TPL" -d "$TMP/tpl"
cp -f "$TMP"/tpl/templates/* "$TPL_DIR/"

echo "== Check"
"$BIN/godot" --version
ls "$TPL_DIR" | grep -E '^web_(nothreads_)?release\.zip$' || { echo "web templates missing"; exit 1; }
case ":$PATH:" in *":$BIN:"*) ;; *) echo "NOTE: $BIN is not on PATH in this shell. Open a new Ubuntu terminal (Ubuntu adds it at login when it exists)." ;; esac
echo "Done: godot ${VER} at $BIN/godot, templates in $TPL_DIR"
