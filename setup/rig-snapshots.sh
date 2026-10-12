#!/usr/bin/env bash
# Mirrors every agent's screen into OpenRig/snapshots/ so Claude (in the
# desktop app) can read it without copy/paste, and logs each seat's activity
# to snapshots/activity-log.csv for measuring team efficiency. No AI usage.
# Start:  tmux new -d -s snapshots "bash /mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/setup/rig-snapshots.sh"
# Stop:   tmux kill-session -t snapshots
OUT="/mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/snapshots"
INTERVAL="${INTERVAL:-10}"   # seconds
LINES="${LINES_BACK:-300}"   # scrollback lines per agent
LOG="$OUT/activity-log.csv"
mkdir -p "$OUT"
[ -f "$LOG" ] || echo "timestamp,rig,session,lifecycle,activity,work" > "$LOG"
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
# One-time help dumps so Claude can learn the CLI's JSON shapes.
for c in "ps" "queue list" "queue show"; do
  rig $c --help > "$OUT/_help_${c// /_}.txt" 2>&1
done
while true; do
  now="$(date '+%Y-%m-%d %H:%M:%S')"
  ps_out="$(rig ps --nodes -A 2>&1)"
  {
    echo "updated $now"; echo
    rig status 2>&1; echo
    echo "$ps_out"
  } > "$OUT/_status.tmp" && mv -f "$OUT/_status.tmp" "$OUT/_status.txt"
  rig ps --nodes -A --json > "$OUT/_ps.tmp" 2>&1 && mv -f "$OUT/_ps.tmp" "$OUT/_ps.json"
  rig queue list -a -A --limit 300 --json > "$OUT/_queue.tmp" 2>&1 && mv -f "$OUT/_queue.tmp" "$OUT/_queue.json"
  rig ps --nodes -A --json --fields rigName,canonicalSessionName,contextUsage > "$OUT/_ctx.tmp" 2>&1 && mv -f "$OUT/_ctx.tmp" "$OUT/_ctx.json"
  # Log the daemon's own activity state (includes needs_input, which the text table hides).
  python3 - "$OUT/_ps.json" "$now" >> "$LOG" <<'PY' || echo "$ps_out" | awk -v ts="$now" 'NR>1 && NF>=5 {print ts","$1","$2","$3","$4","$5}' >> "$LOG"
import json, sys
rows = json.load(open(sys.argv[1]))
rows = rows.get("items", rows) if isinstance(rows, dict) else rows
for r in rows:
    a = r.get("agentActivity") or {}
    st = a.get("state", "unknown")
    if st == "running": st = "working"
    if a.get("reason"): st = f"{st}:{a['reason']}"
    print(f'{sys.argv[2]},{r.get("rigName")},{r.get("canonicalSessionName")},{r.get("lifecycleState")},{st},{"yes" if r.get("hasAssignedWork") else "no"}')
PY
  for s in $(tmux list-sessions -F '#{session_name}' 2>/dev/null); do
    [ "$s" = "snapshots" ] && continue
    f="$OUT/${s//[:\/]/_}.txt"
    { echo "updated $now"; echo;
      tmux capture-pane -p -J -S "-$LINES" -t "=$s:" 2>&1; } > "$f.tmp" && mv -f "$f.tmp" "$f"
  done
  # Read-only mirror of the research output so Claude can review it.
  if [ -d "$HOME/openrig/research" ]; then
    mkdir -p "$OUT/../research-mirror"
    cp -ru "$HOME/openrig/research/." "$OUT/../research-mirror/" 2>/dev/null
  fi
  sleep "$INTERVAL"
done
