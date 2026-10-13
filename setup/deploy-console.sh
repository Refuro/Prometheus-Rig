#!/usr/bin/env bash
# Put the current dashboard/ code live (R-005 step 3, option A).
# Run as yourself from Ubuntu:  bash setup/deploy-console.sh
#
# The console no longer runs from this OneDrive folder, where agents can edit files. It runs from a
# root-owned copy in /opt/rig-console. This script runs the smoke test on the repo copy first, and only
# copies and restarts if it passes. sudo will ask for your password.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST=/opt/rig-console

echo "Smoke test..."
python3 "$REPO/dashboard/tests/smoke.py" > /tmp/rig-console-smoke.log 2>&1 || {
  tail -20 /tmp/rig-console-smoke.log; echo "Smoke test failed: nothing deployed."; exit 1; }
tail -1 /tmp/rig-console-smoke.log

sudo mkdir -p "$DEST"
# Architect seats can edit dashboard/, so look at what would go live before it does (PL-014).
echo "Files that differ from what's live in $DEST:"
diff -rq --exclude=state --exclude=__pycache__ --exclude=tests "$REPO/dashboard" "$DEST" 2>/dev/null | sed 's/^/   /' || true
read -rp "Deploy these? Check them with 'git diff' first if you didn't make them. [y/N] " OK
[ "$OK" = y ] || [ "$OK" = Y ] || { echo "Nothing deployed."; exit 1; }
# Code only: no runtime state, caches or tests.
sudo rsync -a --delete --exclude 'state/' --exclude '__pycache__/' --exclude 'tests/' "$REPO/dashboard/" "$DEST/"
sudo chown -R root:root "$DEST"
sudo chmod -R u=rwX,go=rX "$DEST"
sudo systemctl restart rig-dashboard
sleep 2
systemctl --no-pager --lines=3 status rig-dashboard | head -5
echo "Deployed $(cd "$REPO" && git rev-parse --short HEAD 2>/dev/null || echo 'working copy') to $DEST."
