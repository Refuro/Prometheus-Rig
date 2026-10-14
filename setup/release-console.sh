#!/usr/bin/env bash
# Commit and deploy a console release in one command (owner-approved 2026-10-13; proposal:
# jobs/architects/ops/simpler-deploy-proposal.md).
#
# rig-console-deploy installs a root-owned copy of this script as /usr/local/sbin/rig-console-release, from
# the commit you reviewed. Start THAT copy straight from Windows, so no shell profile runs first:
#     Win+R:  wsl --exec /usr/local/sbin/rig-console-release
# Agents can edit files on /mnt/c and your shell profile, so neither the repo copy nor an interactive shell
# is trusted.
#
# What it does:
#   1. Reads the release note the Platform Architect wrote (~/openrig/jobs/architects/releases/next.json):
#      {"message": "<commit message>", "files": ["dashboard/...", ...], "smoke": "237/237"}. It is untrusted
#      data: paths must be plain names under dashboard/ or setup/, the message one plain line.
#   2. Refuses unless the listed files are EXACTLY the changed files in dashboard/ and setup/, and nothing
#      else is already staged anywhere in the repo. Nothing is staged blindly.
#   3. Shows the files and every changed line, with agents' git settings switched off (no hooks, filters,
#      external diff or pager config).
#   4. Asks "Commit these N files?", stages exactly those paths and commits.
#   5. Asks "Deploy now?" and runs rig-console-deploy (which has its own review, smoke test and sudo).
set -euo pipefail

# Start again with a clean environment: nothing from the caller's shell (LESSOPEN, GIT_*, aliases...) gets in.
if [ -z "${_RCR_CLEAN:-}" ]; then
  exec /usr/bin/env -i _RCR_CLEAN=1 PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    TERM="${TERM:-xterm-256color}" LANG=C.UTF-8 \
    RCR_TEST_NOTE="${RCR_TEST_NOTE:-}" RCR_TEST_DEPLOY="${RCR_TEST_DEPLOY:-}" /bin/bash "$0" "$@"
fi

REPO="@REPO@"   # filled in when rig-console-deploy installs this command
HOME_DIR="$(getent passwd "$(id -un)" | cut -d: -f6)"
NOTE="$HOME_DIR/openrig/jobs/architects/releases/next.json"
DEPLOY=/usr/local/sbin/rig-console-deploy
case "$REPO" in @*)   # not installed: running from the repo, which is only for the test harness
  REPO="$(cd "$(dirname "$0")/.." && pwd)"
  [ -n "$RCR_TEST_NOTE" ] && NOTE="$RCR_TEST_NOTE"
  [ -n "$RCR_TEST_DEPLOY" ] && DEPLOY="$RCR_TEST_DEPLOY" ;;
esac
export HOME="$HOME_DIR"
EMPTY_TREE=4b825dc642cb6eb9a060e54bf8d69288fbee4904
safe_git() { /usr/bin/git --literal-pathspecs --attr-source=$EMPTY_TREE -c core.fsmonitor=false -c core.hooksPath=/dev/null \
  -c core.pager=cat -c diff.external= -c commit.gpgsign=false -c status.showUntrackedFiles=all --no-pager -C "$REPO" "$@"; }
stop() { echo; echo "$*"; echo "Nothing committed or deployed."; read -rp "Press Enter to close. " _ || true; exit 1; }
[ -d "$REPO/.git" ] || stop "Can't find the console's repo at $REPO."
[ -f "$NOTE" ] && [ ! -L "$NOTE" ] || stop "There's no release note at $NOTE, so there's nothing to release."

# 1. The note, parsed by Python in isolated mode (it ignores the environment and the current folder).
PARSED="$(/usr/bin/python3 -I -c '
import json, re, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception as e:
    sys.exit(f"The release note is not valid JSON ({e.__class__.__name__}).")
if not isinstance(d, dict): sys.exit("The release note is not a JSON object.")
msg, files, smoke = d.get("message"), d.get("files"), d.get("smoke", "")
if not isinstance(msg, str) or not re.fullmatch(r"[ -~]{1,120}", msg) or msg.startswith("-"):
    sys.exit("The message must be one plain line of 1 to 120 characters.")
if not isinstance(smoke, str) or not re.fullmatch(r"[0-9/]{0,12}", smoke): sys.exit("smoke must look like 237/237.")
ok = re.compile(r"(dashboard|setup)/[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*")
if not isinstance(files, list) or not files or len(files) > 200: sys.exit("files must be a list of 1 to 200 paths.")
for f in files:
    if not isinstance(f, str) or not ok.fullmatch(f) or any(p in (".", "..") for p in f.split("/")):
        sys.exit(f"Not a plain path under dashboard/ or setup/: {f!r}")
if len(set(files)) != len(files): sys.exit("A file is listed twice.")
print(smoke); print(msg); print("\n".join(sorted(files)))
' "$NOTE" 2>&1)" || stop "Release note refused: $PARSED"
SMOKE="$(sed -n 1p <<<"$PARSED")"; MSG="$(sed -n 2p <<<"$PARSED")"; LISTED="$(sed -n '3,$p' <<<"$PARSED")"

# 2. The note must match what really changed, and nothing else may already be staged.
[ -z "$(safe_git diff --cached --name-only)" ] || stop "Something is already staged in the repo:
$(safe_git diff --cached --name-only | sed 's/^/   /')
Unstage it first (g restore --staged <path>), then run this again."
ACTUAL="$(safe_git status --porcelain=v1 -z --no-renames -- dashboard/ setup/ | tr '\0' '\n' | sed -n 's/^.. //p' | sort)"
if [ "$ACTUAL" != "$LISTED" ]; then
  stop "The release note doesn't match what changed in dashboard/ and setup/.
Changed but not in the note:
$(comm -13 <(echo "$LISTED") <(echo "$ACTUAL") | sed 's/^/   /')
In the note but not changed:
$(comm -23 <(echo "$LISTED") <(echo "$ACTUAL") | sed 's/^/   /')"
fi
while IFS= read -r f; do
  [ -L "$REPO/$f" ] && stop "$f is a symlink; releases refuse those."
done <<<"$LISTED"
N="$(grep -c . <<<"$LISTED")"

# 3. Show it.
echo "Release: $MSG"
echo "Files ($N):"; safe_git status --short --no-renames -- dashboard/ setup/ | sed 's/^/   /'
[ -n "$SMOKE" ] && echo "Expected smoke test: $SMOKE passed"
view() {
  while IFS= read -r f; do
    if safe_git ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then
      safe_git diff --no-ext-diff --no-textconv -- "$f" || true
    else
      echo "=== new file: $f"; safe_git diff --no-index --no-ext-diff --no-textconv -- /dev/null "$f" || true
    fi
  done <<<"$LISTED"
}
# What you're shown is what gets committed: note each file's content now, and check the staged copies match.
snapshot() { while IFS= read -r f; do printf '%s %s\n' "$(safe_git hash-object -- "$f")" "$f"; done <<<"$LISTED"; }
SEEN="$(snapshot)"
while true; do
  read -rp "d shows every changed line (q leaves the viewer). Commit these $N files? [y/N/d] " A || A=n
  case "$A" in
    d|D) if [ -t 1 ]; then view | /usr/bin/less -R; else view; fi ;;
    y|Y) break ;;
    *) stop "Stopped at your answer." ;;
  esac
done

# 4. Commit exactly these paths.
mapfile -t PATHS <<<"$LISTED"
safe_git add -- "${PATHS[@]}"
STAGED="$(safe_git diff --cached --name-only | sort)"
[ "$STAGED" = "$LISTED" ] || { safe_git restore --staged -- "${PATHS[@]}" || true; stop "Staging didn't match the note; unstaged again."; }
STAGED_IDS="$(safe_git ls-files -s -- "${PATHS[@]}" | awk '{print $2" "$4}' | sort -k2)"
[ "$STAGED_IDS" = "$(sort -k2 <<<"$SEEN")" ] || { safe_git restore --staged -- "${PATHS[@]}" || true
  stop "A file changed after you were shown it (something edited it meanwhile). Unstaged again; run this again to see the new version."; }
safe_git commit --quiet --no-verify -m "$MSG"
COMMIT="$(safe_git rev-parse --short HEAD)"
echo "Committed $COMMIT: $MSG"
mv -- "$NOTE" "${NOTE%.json}.done-$COMMIT.json"
[ -z "$(safe_git status --porcelain --no-renames -- dashboard/ setup/)" ] || echo "Note: dashboard/ or setup/ changed again since; the deploy will refuse until that's sorted."

# 5. Deploy.
read -rp "Deploy $COMMIT now? It asks once more, then wants your password. [y/N] " A || A=n
case "$A" in
  y|Y) "$DEPLOY" || stop "The deploy stopped (the commit $COMMIT stays; run rig-console-deploy later)." ;;
  *) echo "Committed, not deployed. Run rig-console-deploy when you're ready." ;;
esac
read -rp "Press Enter to close. " _ || true
