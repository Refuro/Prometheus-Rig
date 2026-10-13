#!/usr/bin/env bash
# R-005 step 3, option A: run Rig Console as its own Linux user, from code and secrets the agents can't
# touch. Run ONCE, as yourself (not with sudo), between runs:
#     bash setup/install-console-user.sh
# Full runbook, with the order of steps and how to check each one: dashboard/ARCHITECTURE-LOG.md, PL-013.
#
# What it does (sudo asks for your password):
#   1. Creates the system user "rigconsole" (no login, home /var/lib/rig-console).
#   2. Installs a root-owned helper that lets the console run only "rig send" / "rig ps" as you.
#   3. Moves the console's settings to /etc/rig-console/env (readable by root and rigconsole only), with a
#      NEW console token: the old one sat where agents could read it.
#   4. Gives rigconsole access to your job folders with ACLs (read + write for jobs and research, read for
#      launches and briefs). Nothing else in your home.
#   5. Copies the event history and console state to /var/lib/rig-console.
#   6. Deploys the code to /opt/rig-console and switches the rig-dashboard service to run as rigconsole.
set -euo pipefail
if [ "$(id -u)" = 0 ]; then echo "Run this as yourself, not with sudo: it needs to know whose agents to serve."; exit 1; fi
OWNER="$(id -un)"; OWNER_HOME="$HOME"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OLD_ENV="$OWNER_HOME/.config/rig-console.env"
STATE=/var/lib/rig-console

echo "== 1. Console user"
id rigconsole >/dev/null 2>&1 || sudo useradd --system --home-dir "$STATE" --create-home --shell /usr/sbin/nologin rigconsole
sudo install -d -o rigconsole -g rigconsole -m 750 "$STATE" "$STATE/state"

echo "== 2. rig helper and its sudo rule"
command -v setfacl >/dev/null && command -v rsync >/dev/null || sudo apt-get install -y acl rsync
sudo install -D -o root -g root -m 755 "$REPO/setup/rig-owner" /usr/local/lib/rig-console/rig-owner
RULE="rigconsole ALL=($OWNER) NOPASSWD: /usr/local/lib/rig-console/rig-owner"
echo "$RULE" | sudo tee /etc/sudoers.d/rig-console >/dev/null
sudo chmod 440 /etc/sudoers.d/rig-console
sudo visudo -cf /etc/sudoers.d/rig-console
sudo -u rigconsole sudo -n -u "$OWNER" /usr/local/lib/rig-console/rig-owner ps --json >/dev/null \
  && echo "   rigconsole can run 'rig ps' as $OWNER: ok" || echo "   WARNING: rigconsole couldn't run rig ps as $OWNER"

echo "== 3. Settings and a new token"
get() { [ -f "$OLD_ENV" ] && sed -n "s/^$1=//p" "$OLD_ENV" | tail -1 || true; }
NEW_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
HOSTS="$(get RIG_CONSOLE_HOSTS)"
if ! echo "$HOSTS" | grep -q '\.ts\.net'; then
  echo "   Your Tailscale name pins which address the console answers to (MA-013)."
  echo "   Find it in the Tailscale app or with 'tailscale status' in PowerShell, e.g. prometheus.tail1234.ts.net"
  read -rp "   Tailscale name (Enter to skip; health will remind you): " TSNAME
  [ -n "$TSNAME" ] && HOSTS="${HOSTS:+$HOSTS,}$TSNAME"
fi
TMP="$(mktemp)"
cat > "$TMP" <<ENV
# Rig Console settings (R-005 step 3). Readable by root and rigconsole only.
# Edit with: sudoedit /etc/rig-console/env   then: sudo systemctl restart rig-dashboard
HOME=$STATE
HOST=$(get HOST || true)
RIG_CONSOLE_TOKEN=$NEW_TOKEN
NTFY_TOPIC=$(get NTFY_TOPIC)
NTFY_CLICK=$(get NTFY_CLICK)
RIG_CONSOLE_HOSTS=$HOSTS
RIG_BIN=sudo -n -u $OWNER /usr/local/lib/rig-console/rig-owner
RIG_SNAPSHOTS=$REPO/snapshots
RIG_MODELS_DIR=$REPO/models
RIG_RESEARCH_DIR=$OWNER_HOME/openrig/research
RIG_LAUNCHES_DIR=$OWNER_HOME/openrig/launches
RIG_BRIEFS_DIR=$OWNER_HOME/openrig/briefs
RIG_JOBS_CONFIG=/etc/rig-console/jobs.json
RIG_STATE_DIR=$STATE/state
RIG_DB=$STATE/console.db
ENV
sed -i 's/^HOST=$/HOST=127.0.0.1/' "$TMP"
sudo install -D -o root -g rigconsole -m 640 "$TMP" /etc/rig-console/env
sed "s#~/#$OWNER_HOME/#g" "$REPO/dashboard/jobs.json" > "$TMP"
sudo install -o root -g rigconsole -m 640 "$TMP" /etc/rig-console/jobs.json
rm -f "$TMP"
if [ -f "$OLD_ENV" ]; then
  # The old file is readable by agents: keep it, minus the secrets.
  sed -i -e 's/^RIG_CONSOLE_TOKEN=.*/# RIG_CONSOLE_TOKEN moved to \/etc\/rig-console\/env (R-005)/' \
         -e 's/^NTFY_TOPIC=.*/# NTFY_TOPIC moved to \/etc\/rig-console\/env (R-005)/' "$OLD_ENV"
fi

echo "== 4. Access to your job folders (ACLs)"
mkdir -p "$OWNER_HOME/openrig/launches"
setfacl -m u:rigconsole:x "$OWNER_HOME" "$OWNER_HOME/openrig"
for d in jobs research; do
  [ -d "$OWNER_HOME/openrig/$d" ] && setfacl -R -m u:rigconsole:rwX -m d:u:rigconsole:rwX "$OWNER_HOME/openrig/$d"
done
for d in launches briefs; do
  [ -d "$OWNER_HOME/openrig/$d" ] && setfacl -R -m u:rigconsole:rX -m d:u:rigconsole:rX "$OWNER_HOME/openrig/$d"
done

echo "== 5. History and state"
[ -f "$OWNER_HOME/.local/share/rig-console/console.db" ] && sudo cp -n "$OWNER_HOME/.local/share/rig-console/console.db" "$STATE/console.db" || true
[ -d "$REPO/dashboard/state" ] && sudo cp -rn "$REPO/dashboard/state/." "$STATE/state/" || true
sudo chown -R rigconsole:rigconsole "$STATE"

echo "== 6. Code and service"
sudo tee /etc/systemd/system/rig-dashboard.service >/dev/null <<UNIT
[Unit]
Description=Rig Console dashboard (runs as rigconsole, code in /opt/rig-console)
After=local-fs.target rig-snapshots.service

[Service]
User=rigconsole
EnvironmentFile=/etc/rig-console/env
WorkingDirectory=/opt/rig-console
ExecStart=/usr/bin/python3 /opt/rig-console/serve.py
Restart=always
RestartSec=5
ProtectSystem=full
PrivateTmp=true

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
bash "$REPO/setup/deploy-console.sh"

cat <<DONE

Done. Your NEW console token (the old one no longer works):

    $NEW_TOKEN

Sign in again on this PC (the "Sign in to make changes" button) and on your phone (open your console
link with ?token=<new token> once). Store the token in your password manager.
From now on, after changing dashboard code: bash setup/deploy-console.sh
Next: setup/harden-wsl.sh (interop off, sudo with a password). Runbook: PL-013.
DONE
