#!/usr/bin/env bash
# R-005 step 3, option A: run Rig Console as its own Linux user, from code and secrets the agents can't
# touch. Run ONCE, as yourself (not with sudo), in a clean shell (Win+R: wsl --exec /bin/bash --noprofile --norc):
#     bash setup/install-console-user.sh
# Your steps, with a success check for each: ~/openrig/jobs/architects/ops/console-user-runbook.md.
# Design: dashboard/ARCHITECTURE-LOG.md, PL-013, PL-027 and PL-030.
#
# What it does (sudo asks for your password):
#   0. Refuses unless dashboard/ and setup/ are committed: what it installs is what you reviewed.
#   1. Creates the system user "rigconsole" (no login, home /var/lib/rig-console).
#   2. Installs a root-owned helper (from the commit) that lets the console run only its four rig calls as you.
#   3. Moves the console's settings to /etc/rig-console/env (readable by root and rigconsole only), with a
#      NEW console token and a NEW ntfy topic: the old ones sat where agents could read them.
#   4. Gives rigconsole access to your job folders with ACLs (read + write for jobs and research, read for
#      launches and briefs). Nothing else in your home.
#   5. Copies the event history and console state to /var/lib/rig-console; the team pins only if you
#      confirm them.
#   6. Deploys the code to /opt/rig-console, installs the deploy command as root-owned rig-console-deploy,
#      and switches the rig-dashboard service to run as rigconsole.
set -euo pipefail
# Agents run as you and can put programs in your PATH (a fake "sudo" would see your password): use only the
# system's own (MA-016).
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
if [ "$(id -u)" = 0 ]; then echo "Run this as yourself, not with sudo: it needs to know whose agents to serve."; exit 1; fi
# The screen logger copies every tmux pane into files agents can read (MA-014 finding 2).
if [ -n "${TMUX:-}" ]; then echo "Run this in a plain Ubuntu window, not inside tmux: tmux screens are logged where agents can read them."; exit 1; fi
OWNER="$(id -un)"; OWNER_HOME="$HOME"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OLD_ENV="$OWNER_HOME/.config/rig-console.env"
STATE=/var/lib/rig-console
# No fsmonitor, hooks, pager, external diff or .gitattributes filters from the agents' repo (MA-016, MA-021, PL-033).
safe_git() { git --attr-source=4b825dc642cb6eb9a060e54bf8d69288fbee4904 -c core.fsmonitor=false -c core.hooksPath=/dev/null \
  -c core.pager=cat -c diff.external= --no-pager "$@"; }
# What gets installed must be what you reviewed and committed (MA-016 finding 2).
if [ -n "$(safe_git -C "$REPO" status --porcelain --untracked-files=no -- dashboard/ setup/)" ]; then
  echo "dashboard/ or setup/ has changes that aren't committed:"
  safe_git -C "$REPO" status --short --untracked-files=no -- dashboard/ setup/ | sed 's/^/   /'
  echo "Review and commit them first (runbook step A1). Nothing changed."; exit 1
fi
# A committed symlink would install whatever it points at (MA-021 R2-2).
LINKS="$(safe_git -C "$REPO" ls-tree -r HEAD -- dashboard setup | awk '$1 == "120000" {print $4}')"
if [ -n "$LINKS" ]; then
  echo "These are committed as symlinks, which this refuses:"; echo "$LINKS" | sed 's/^/   /'; exit 1
fi

echo "== 1. Console user"
id rigconsole >/dev/null 2>&1 || sudo useradd --system --home-dir "$STATE" --create-home --shell /usr/sbin/nologin rigconsole
sudo install -d -o rigconsole -g rigconsole -m 750 "$STATE" "$STATE/state"

echo "== 2. rig helper and its sudo rule"
command -v setfacl >/dev/null && command -v rsync >/dev/null || sudo apt-get install -y acl rsync
HELPER="$(mktemp)"
safe_git -C "$REPO" show HEAD:setup/rig-owner > "$HELPER"   # from the commit, not the working folder
sudo install -D -o root -g root -m 755 "$HELPER" /usr/local/lib/rig-console/rig-owner
rm -f "$HELPER"
RULE="rigconsole ALL=($OWNER) NOPASSWD: /usr/local/lib/rig-console/rig-owner"
echo "$RULE" | sudo tee /etc/sudoers.d/rig-console >/dev/null
sudo chmod 440 /etc/sudoers.d/rig-console
sudo visudo -cf /etc/sudoers.d/rig-console
sudo -u rigconsole sudo -n -u "$OWNER" /usr/local/lib/rig-console/rig-owner ps >/dev/null \
  && echo "   rigconsole can run 'rig ps' as $OWNER: ok (so sudo sets HOME and the helper finds rig)" \
  || echo "   WARNING: rigconsole couldn't run rig ps as $OWNER. If 'rig' isn't found, sudo isn't setting HOME=$OWNER_HOME (MA-014 point 7)."

echo "== 3. Settings, a new token and a new phone-alert topic"
# The old settings file is agent-writable: carry over only plain values, and show them to you (MA-016).
get() { [ -f "$OLD_ENV" ] && sed -n "s/^$1=//p" "$OLD_ENV" | tail -1 | tr -cd 'A-Za-z0-9.,:/_-' || true; }
NEW_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
# The ntfy topic sat in the same agent-readable file: anyone who knows it can push to your phone (MA-016 finding 3).
NEW_TOPIC="rig-$(python3 -c 'import secrets; print(secrets.token_hex(16))')"
HOSTS="$(get RIG_CONSOLE_HOSTS)"
if ! echo "$HOSTS" | grep -q '\.ts\.net'; then
  echo "   Your Tailscale name pins which address the console answers to (MA-013)."
  echo "   Find it in the Tailscale app or with 'tailscale status' in PowerShell, e.g. prometheus.tail1234.ts.net"
  read -rp "   Tailscale name (Enter to skip; health will remind you): " TSNAME
  TSNAME="$(printf '%s' "$TSNAME" | tr -cd 'A-Za-z0-9.-')"
  [ -n "$TSNAME" ] && HOSTS="${HOSTS:+$HOSTS,}$TSNAME"
fi
HOSTV="$(get HOST)"; CLICK="$(get NTFY_CLICK)"
echo "   Carried over from your old settings; check they look right:"
echo "     HOST=${HOSTV:-127.0.0.1}"
echo "     RIG_CONSOLE_HOSTS=$HOSTS"
echo "     NTFY_CLICK=$CLICK"
read -rp "   Use these? [y/N] " OK
[ "$OK" = y ] || [ "$OK" = Y ] || { echo "Stopped. Fix $OLD_ENV and run this again."; exit 1; }
TMP="$(mktemp)"
cat > "$TMP" <<ENV
# Rig Console settings (R-005 step 3). Readable by root and rigconsole only.
# Edit with: sudoedit /etc/rig-console/env   then: sudo systemctl restart rig-dashboard
HOME=$STATE
HOST=${HOSTV:-127.0.0.1}
RIG_CONSOLE_TOKEN=$NEW_TOKEN
NTFY_TOPIC=$NEW_TOPIC
NTFY_CLICK=$CLICK
RIG_CONSOLE_HOSTS=$HOSTS
RIG_BIN=sudo -n -u $OWNER /usr/local/lib/rig-console/rig-owner
RIG_SNAPSHOTS=$REPO/snapshots
RIG_MODELS_DIR=$REPO/models
RIG_RESEARCH_DIR=$OWNER_HOME/openrig/research
RIG_LAUNCHES_DIR=$OWNER_HOME/openrig/launches
RIG_BRIEFS_DIR=$OWNER_HOME/openrig/briefs
RIG_OPERATOR_DIR=$OWNER_HOME/openrig/operator
RIG_ACTIVITY_ARCHIVE=$OWNER_HOME/openrig/activity
RIG_JOBS_CONFIG=/etc/rig-console/jobs.json
RIG_STATE_DIR=$STATE/state
RIG_DB=$STATE/console.db
ENV
sudo install -D -o root -g rigconsole -m 640 "$TMP" /etc/rig-console/env
# Never printed: read them once from root-only files, in a plain terminal (MA-014 finding 2).
sudo install -o root -g root -m 600 /dev/null /root/rig-console-token
printf '%s\n' "$NEW_TOKEN" | sudo tee /root/rig-console-token >/dev/null
sudo install -o root -g root -m 600 /dev/null /root/rig-console-ntfy-topic
printf '%s\n' "$NEW_TOPIC" | sudo tee /root/rig-console-ntfy-topic >/dev/null
unset NEW_TOKEN NEW_TOPIC
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
mkdir -p "$OWNER_HOME/openrig/activity"   # older activity-log days (R-011)
for d in launches briefs operator activity; do   # operator: its log (R-022); activity: older log days (R-011)
  [ -d "$OWNER_HOME/openrig/$d" ] && setfacl -R -m u:rigconsole:rX -m d:u:rigconsole:rX "$OWNER_HOME/openrig/$d"
done

echo "== 5. History and state"
[ -f "$OWNER_HOME/.local/share/rig-console/console.db" ] && sudo cp -n "$OWNER_HOME/.local/share/rig-console/console.db" "$STATE/console.db" || true
# The trust anchors sat where seats could write (MA-016 finding 4):
# - decision-fingerprints.json is carried over. Starting empty would trust every existing decision anyway
#   (gates.unverified_decisions), and an empty-but-valid ledger would flag every past decision as forged.
#   Option A protects decisions from here on, not retroactively (PL-030).
# - job-pins.json routes decisions for jobs without a launch record: you check the list, or it starts fresh.
# - lounge-owner.json isn't carried over (no owner posts exist before this deploy).
# --no-links: a planted symlink must not become protected state that reads a seat-writable file (MA-021 R2-3).
[ -d "$REPO/dashboard/state" ] && sudo rsync -a --no-links --ignore-existing --exclude job-pins.json \
  --exclude lounge-owner.json --exclude '*.tmp' "$REPO/dashboard/state/" "$STATE/state/" || true
PINS="$REPO/dashboard/state/job-pins.json"
if [ -s "$PINS" ] && [ ! -L "$PINS" ]; then
  echo "   Team pins (which team each job's decisions go to, for jobs without a launch record):"
  python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); [print("     %s -> %s" % (k, v)) for k, v in sorted(d.items())]' "$PINS" || true
  read -rp "   Do these look right? y keeps them; anything else starts fresh. [y/N] " OK
  if [ "$OK" = y ] || [ "$OK" = Y ]; then
    sudo install -o rigconsole -g rigconsole -m 640 "$PINS" "$STATE/state/job-pins.json"
  fi
fi
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

Done. Your console has a NEW token; the old one no longer works. It isn't shown here. Read it once with

    sudo cat /root/rig-console-token

in this plain window (never inside tmux), and store it in your password manager. Then sign in again on
EVERY device: this PC (the "Sign in to make changes" button) and your phone (open your console link with
?token=<new token> once). Until you do, the decision page just says "sign in".

Phone alerts now use a NEW ntfy topic (the old one sat where agents could read it). Read it with

    sudo cat /root/rig-console-ntfy-topic

then in the ntfy app subscribe to it and unsubscribe from the old one.

From now on, after committing console changes: rig-console-deploy   (the root-owned copy, not the repo's)
Next: setup/harden-wsl.sh (interop off, sudo with a password). Runbook: ops/console-user-runbook.md.
DONE
