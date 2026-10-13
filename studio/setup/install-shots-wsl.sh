#!/usr/bin/env bash
# One-time setup so prototype builds can screenshot themselves (tools/build.py "shots" step).
# Installs the Playwright package and its Chromium under ~/.local/share/studio-shots.
# Free; about 150-250 MB. Needs node/npm (already in WSL).
set -euo pipefail
DIR="$HOME/.local/share/studio-shots"
mkdir -p "$DIR"
cd "$DIR"
[ -f package.json ] || npm init -y >/dev/null
npm install --no-audit --no-fund playwright@1.50.1
npx playwright install chromium
echo
echo "If the test below fails with missing libraries, run once:"
echo "  sudo apt-get update && sudo apt-get install -y libnss3 libnspr4 libasound2t64"
echo "  (if it still names missing libraries: sudo env PATH=\"\$PATH\" npx --prefix $DIR playwright install-deps chromium)"
echo
NODE_PATH="$DIR/node_modules" node -e "require('playwright').chromium.launch({args:['--no-sandbox']}).then(b=>{console.log('chromium OK');return b.close()}).catch(e=>{console.error('chromium FAILED: '+e.message);process.exit(1)})"
