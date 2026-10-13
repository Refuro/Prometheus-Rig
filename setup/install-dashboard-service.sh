#!/usr/bin/env bash
# FIRST-TIME SETUP ONLY. Once the console runs as its own user (R-005 step 3), use
# setup/install-console-user.sh and setup/deploy-console.sh instead: re-running this script would put the
# console back under your user, running code from this folder, where agents can reach both.
# Run in Ubuntu once:  bash setup/install-dashboard-service.sh
# Makes Rig Console start with Ubuntu and restart itself if it crashes.
set -euo pipefail
if [ -f /etc/rig-console/env ]; then
  echo "The console already runs as its own user (/etc/rig-console/env exists). Use setup/deploy-console.sh."; exit 1
fi
DASH="$(cd "$(dirname "$0")/../dashboard" && pwd)"
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
NODE_BIN="$(dirname "$(command -v rig)")"
ENVFILE="$HOME/.config/rig-console.env"
mkdir -p "$(dirname "$ENVFILE")"
[ -f "$ENVFILE" ] || cat > "$ENVFILE" <<'ENV'
# Rig Console settings. Restart after editing: sudo systemctl restart rig-dashboard
# Laptop/phone access over Tailscale: set HOST=0.0.0.0 and a long random token.
#HOST=0.0.0.0
#RIG_CONSOLE_TOKEN=
# Phone push alerts via ntfy.sh (alert text goes to ntfy's servers). Pick a hard-to-guess topic.
#NTFY_TOPIC=
ENV
tmux kill-session -t dashboard 2>/dev/null || true
sudo tee /etc/systemd/system/rig-dashboard.service >/dev/null <<UNIT
[Unit]
Description=Rig Console dashboard
After=local-fs.target rig-snapshots.service

[Service]
User=$USER
Environment=HOME=$HOME
Environment=PATH=$NODE_BIN:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=-$ENVFILE
WorkingDirectory=$DASH
ExecStart=/usr/bin/python3 $DASH/serve.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now rig-dashboard.service
sleep 2
systemctl --no-pager --lines=3 status rig-dashboard.service | head -5
echo
echo "Rig Console runs at http://localhost:8800 from now on."
echo "After changing dashboard files: sudo systemctl restart rig-dashboard"
