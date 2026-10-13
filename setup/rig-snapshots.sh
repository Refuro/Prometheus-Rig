#!/usr/bin/env bash
# Mirrors every agent's screen into OpenRig/snapshots/ so Claude (in the
# desktop app) can read it without copy/paste, and logs each seat's activity
# to snapshots/activity-log.csv for measuring team efficiency. No AI usage.
# Normally runs as the rig-snapshots service (setup/install-autostart.sh).
# By hand:  tmux new -d -s snapshots "bash <repo>/setup/rig-snapshots.sh"
#
# Nothing in a round may block the next one (2026-10-12: a `cp` into OneDrive hung for 10+ minutes and
# every snapshot and console alert went stale). So every step has a timeout, and the research mirror runs in
# the background, at most one at a time. A copy stuck inside the kernel (state D) can't be killed even by
# `timeout`; it then only blocks later mirrors, never the snapshots, and each skip is logged.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${RIG_SNAPSHOTS:-$REPO/snapshots}"
INTERVAL="${INTERVAL:-10}"              # seconds between rounds
LINES="${LINES_BACK:-300}"              # scrollback lines per agent
MIRROR_EVERY="${MIRROR_EVERY:-60}"      # seconds between research-mirror copies
MIRROR_TIMEOUT="${MIRROR_TIMEOUT:-300}" # a copy taking longer than this is stopped and logged
MIRROR_MAX_SIZE="${MIRROR_MAX_SIZE:-20M}"
STEP_TIMEOUT="${STEP_TIMEOUT:-20}"      # any one rig or tmux command
RESEARCH="$HOME/openrig/research"
OPERATOR="${RIG_OPERATOR_DIR:-$HOME/openrig/operator}"   # the operator's log (R-022), mirrored for reading (owner, 2026-10-13)
MIRROR="${RESEARCH_MIRROR:-$REPO/research-mirror}"
LOCK="$HOME/.cache/rig-snapshots/mirror.lock"
LOG="$OUT/activity-log.csv"
# R-011: the log rotates daily. Today's and yesterday's stay here (OneDrive) for reading; older days move to
# ARCHIVE, off OneDrive. The console reads both (RIG_ACTIVITY_ARCHIVE).
ARCHIVE="${RIG_ACTIVITY_ARCHIVE:-$HOME/openrig/activity}"
HEADER="timestamp,rig,session,lifecycle,activity,work"
ERRLOG="$OUT/_logger.log"   # timeouts and skips; also in the journal (journalctl -u rig-snapshots)
mkdir -p "$OUT" "$ARCHIVE" "$(dirname "$LOCK")"
[ -f "$LOG" ] || echo "$HEADER" > "$LOG"

# Once a day: the log's first day isn't today any more, so it becomes activity-log-<first day>.csv, and
# finished days older than yesterday move to ARCHIVE. A move that times out is retried next round.
rotate_log() {
  local today first yday f d
  today="$(date +%F)"
  first="$(sed -n '2{s/^\([0-9-]\{10\}\).*/\1/p;q}' "$LOG" 2>/dev/null)"
  if [ -n "$first" ] && [ "$first" != "$today" ] && [ ! -e "$OUT/activity-log-$first.csv" ]; then
    mv -f "$LOG" "$OUT/activity-log-$first.csv" && echo "$HEADER" > "$LOG" && note "activity log rotated: activity-log-$first.csv"
  fi
  yday="$(date -d yesterday +%F)"
  for f in "$OUT"/activity-log-*.csv; do
    [ -e "$f" ] || continue
    d="${f##*/activity-log-}"; d="${d%.csv}"
    if [[ "$d" < "$yday" ]]; then
      t 300 "archive $d" mv -f "$f" "$ARCHIVE/" && note "activity log archived: activity-log-$d.csv"
    fi
  done
}
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

note() {   # one line to the journal and to _logger.log (kept to its last 500 lines)
  local line; line="$(date '+%Y-%m-%d %H:%M:%S') $*"
  echo "$line" >&2
  { tail -n 499 "$ERRLOG" 2>/dev/null; echo "$line"; } > "$ERRLOG.tmp" && mv -f "$ERRLOG.tmp" "$ERRLOG"
}
# t <seconds> <name> <command...>: run with a timeout; log if it ran out of time.
t() {
  local secs="$1" name="$2"; shift 2
  timeout -k 5 "$secs" "$@"; local rc=$?
  if [ "$rc" = 124 ] || [ "$rc" = 137 ]; then note "TIMEOUT after ${secs}s: $name"; fi
  return "$rc"
}

# Research outputs only: agents' text, JSON and images. Tools, models, virtualenvs and builds stay out
# (assets-1 put 40 GB of them in research/ and the old full copy pushed it all into OneDrive).
mirror_research() {
  (
    flock -n 9 || { note "mirror skipped: the previous copy is still running"; exit 0; }
    mkdir -p "$MIRROR"
    t "$MIRROR_TIMEOUT" "research mirror" nice -n 10 ionice -c 3 \
      rsync -rt --modify-window=2 --max-size="$MIRROR_MAX_SIZE" \
        --exclude='tools/' --exclude='models/' --exclude='checkpoints/' --exclude='build/' --exclude='builds/' \
        --exclude='*venv*/' --exclude='node_modules/' --exclude='.git/' --exclude='__pycache__/' \
        --exclude='*.wasm' --exclude='*.pck' --exclude='*.zip' --exclude='*.tar*' --exclude='*.7z' \
        --exclude='*.safetensors' --exclude='*.gguf' --exclude='*.ckpt' --exclude='*.pt' --exclude='*.pth' \
        --exclude='*.onnx' --exclude='*.bin' --exclude='*.so' --exclude='*.so.*' \
        "$RESEARCH/" "$MIRROR/" 2>>"$ERRLOG"
  ) 9>"$LOCK" &
}

# One-time help dumps so Claude can learn the CLI's JSON shapes.
for c in "ps" "queue list" "queue show"; do
  t "$STEP_TIMEOUT" "rig $c --help" rig $c --help > "$OUT/_help_${c// /_}.txt" 2>&1
done
last_mirror=$((-MIRROR_EVERY))   # mirror on the first round
while true; do
  rotate_log
  now="$(date '+%Y-%m-%d %H:%M:%S')"
  ps_out="$(t "$STEP_TIMEOUT" "rig ps" rig ps --nodes -A 2>&1)"
  {
    echo "updated $now"; echo
    t "$STEP_TIMEOUT" "rig status" rig status 2>&1; echo
    echo "$ps_out"
  } > "$OUT/_status.tmp" && mv -f "$OUT/_status.tmp" "$OUT/_status.txt"
  t "$STEP_TIMEOUT" "rig ps json" rig ps --nodes -A --json > "$OUT/_ps.tmp" 2>&1 && mv -f "$OUT/_ps.tmp" "$OUT/_ps.json"
  t "$STEP_TIMEOUT" "rig queue list" rig queue list -a -A --limit 300 --json > "$OUT/_queue.tmp" 2>&1 && mv -f "$OUT/_queue.tmp" "$OUT/_queue.json"
  # Active items with their summaries, for the console's Docket tab (R-023); the compact list leaves summaries out.
  t "$STEP_TIMEOUT" "rig queue list active" rig queue list -A --full --limit 300 --json > "$OUT/_queue_active.tmp" 2>&1 \
    && mv -f "$OUT/_queue_active.tmp" "$OUT/_queue_active.json"
  t "$STEP_TIMEOUT" "rig ps ctx" rig ps --nodes -A --json --fields rigName,canonicalSessionName,contextUsage > "$OUT/_ctx.tmp" 2>&1 && mv -f "$OUT/_ctx.tmp" "$OUT/_ctx.json"
  # Log the daemon's own activity state (includes needs_input, which the text table hides).
  python3 - "$OUT/_ps.json" "$now" >> "$LOG" <<'PY' || echo "$ps_out" | awk -v ts="$now" 'NR>1 && NF>=5 {print ts","$1","$2","$3","$4","$5}' >> "$LOG"
import json, sys
rows = json.load(open(sys.argv[1]))
rows = rows.get("items", rows) if isinstance(rows, dict) else rows
for r in rows:
    if r.get("sessionStatus") not in (None, "running"):
        continue   # R-011: live seats only; stopped teams added a row per seat every 10 s
    a = r.get("agentActivity") or {}
    st = a.get("state", "unknown")
    if st == "running": st = "working"
    if a.get("reason"): st = f"{st}:{a['reason']}"
    print(f'{sys.argv[2]},{r.get("rigName")},{r.get("canonicalSessionName")},{r.get("lifecycleState")},{st},{"yes" if r.get("hasAssignedWork") else "no"}')
PY
  for s in $(t "$STEP_TIMEOUT" "tmux list-sessions" tmux list-sessions -F '#{session_name}' 2>/dev/null); do
    [ "$s" = "snapshots" ] && continue
    f="$OUT/${s//[:\/]/_}.txt"
    { echo "updated $now"; echo;
      t "$STEP_TIMEOUT" "capture $s" tmux capture-pane -p -J -S "-$LINES" -t "=$s:" 2>&1; } > "$f.tmp" && mv -f "$f.tmp" "$f"
  done
  # Read-only mirror of the research output so Claude can review it.
  if [ $((SECONDS - last_mirror)) -ge "$MIRROR_EVERY" ]; then
    last_mirror=$SECONDS
    [ -d "$RESEARCH" ] && mirror_research
    # The operator's folder: small text files, copied one way into snapshots/operator/. Only the copy is
    # ever changed (--delete applies to the mirror); links are skipped, never followed.
    if [ -d "$OPERATOR" ]; then
      t "$STEP_TIMEOUT" "operator mirror" rsync -rt --delete --no-links --max-size=5M "$OPERATOR/" "$OUT/operator/" 2>>"$ERRLOG"
    fi
  fi
  sleep "$INTERVAL"
done
