#!/usr/bin/env bash
# Stage GodotSteam (the GDExtension build) for a production job. The owner runs this; agents never
# download it. No sudo needed.
#
#   bash install-godotsteam.sh <zip file or https URL> <production job folder>
#   bash install-godotsteam.sh ~/Downloads/godotsteam-gdextension.zip ~/openrig/jobs/bridge-prod
#
# Get the zip from GodotSteam's official downloads (godotsteam.com, or the Godot Asset Library
# entry "GodotSteam GDExtension"). Pick the GDExtension build whose Godot version matches the WSL
# Godot (`godot --version`), not a precompiled editor or a module build.
#
# The script checks the zip and stages it in <job>/ops/godotsteam/<time>/. It never touches the
# game repo: the tech lead adds the addon to game/ as a normal task (the Platform service swaps its
# null version for GodotSteam), so the change is reviewed and tested like any other.
set -euo pipefail

SRC="${1:-}"
JOB="${2:-}"
[ -n "$SRC" ] && [ -n "$JOB" ] || { sed -n '2,14p' "$0"; exit 2; }
JOB="$(cd "$JOB" && pwd)"
grep -q '"production"' "$JOB/job.json" 2>/dev/null || { echo "Not a production job folder: $JOB"; exit 1; }

command -v unzip >/dev/null || { echo "unzip missing: run  sudo apt install -y unzip  then rerun"; exit 1; }
command -v sha256sum >/dev/null || { echo "sha256sum missing (coreutils)"; exit 1; }
GODOT="$(command -v godot || true)"
[ -n "$GODOT" ] || { echo "godot not on PATH: run studio/setup/install-godot-wsl.sh first"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
ZIP="$TMP/godotsteam.zip"
case "$SRC" in
  https://*)
    command -v curl >/dev/null || { echo "curl missing: run  sudo apt install -y curl  then rerun"; exit 1; }
    echo "== Download"
    curl -fSL --progress-bar -o "$ZIP" "$SRC" ;;
  *)
    [ -f "$SRC" ] || { echo "No such file: $SRC"; exit 1; }
    cp "$SRC" "$ZIP" ;;
esac
SHA="$(sha256sum "$ZIP" | cut -d' ' -f1)"
echo "== sha256 $SHA"

echo "== Check the zip"
unzip -q "$ZIP" -d "$TMP/x"
GDEXT="$(find "$TMP/x" -name '*.gdextension' -path '*godotsteam*' | head -n 1)"
[ -n "$GDEXT" ] || { echo "No godotsteam .gdextension file in the zip: is this the GDExtension build?"; exit 1; }
ADDON="$(dirname "$GDEXT")"
case "$ADDON" in */addons/godotsteam) ;; *) echo "Unexpected layout (want addons/godotsteam/): $ADDON"; exit 1 ;; esac

MIN="$(grep -E '^compatibility_minimum' "$GDEXT" | head -n 1 | sed -E 's/[^0-9.]//g')"
HAVE="$("$GODOT" --version | grep -oE '^[0-9]+\.[0-9]+(\.[0-9]+)?')"
echo "   needs Godot ${MIN:-unknown}, have $HAVE"
if [ -n "$MIN" ] && [ "$(printf '%s\n%s\n' "$MIN" "$HAVE" | sort -V | head -n 1)" != "$MIN" ]; then
  echo "This GodotSteam build needs Godot $MIN or newer; WSL has $HAVE. Get a matching build."; exit 1
fi

MISSING=""
find "$ADDON" -name 'libgodotsteam*linux*x86_64*.so' | grep -q . || MISSING="$MISSING linux-godotsteam"
find "$ADDON" -name 'libsteam_api.so' | grep -q . || MISSING="$MISSING linux-steam_api"
find "$ADDON" -name '*godotsteam*windows*x86_64*.dll' | grep -q . || MISSING="$MISSING windows-godotsteam"
find "$ADDON" -name 'steam_api64.dll' | grep -q . || MISSING="$MISSING windows-steam_api64"
[ -z "$MISSING" ] || { echo "Missing libraries:$MISSING (Windows and Linux are both needed)"; exit 1; }

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$JOB/ops/godotsteam/$STAMP"
mkdir -p "$DEST/addons"
cp -r "$ADDON" "$DEST/addons/"
cp "$ZIP" "$DEST/source.zip"
FILES="$(find "$DEST/addons" -type f | wc -l)"
cat > "$JOB/ops/godotsteam/installed.json" <<EOF
{"staged": "ops/godotsteam/$STAMP/addons/godotsteam", "source": "$(basename "$SRC")", "sha256": "$SHA",
 "compatibility_minimum": "${MIN:-unknown}", "godot": "$HAVE", "files": $FILES, "at": "$STAMP", "by": "owner"}
EOF

echo "== Done: staged at $DEST/addons/godotsteam ($FILES files)"
echo "Next: tell the operator \"GodotSteam staged, see ops/godotsteam/installed.json\"; the tech lead adds it to game/ as a task."
echo "Steam itself needs your Steamworks App ID before a real Steam build; until then tests use the null Platform."
