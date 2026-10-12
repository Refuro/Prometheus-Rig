#!/usr/bin/env bash
# Run in Ubuntu once:  bash /mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/setup/install-dashboard-service.sh
# Makes Rig Console start with Ubuntu and restart itself if it crashes.
set -euo pipefail
DASH="/mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/dashboard"
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
