#!/usr/bin/env bash
# Put the console code live (R-005 step 3, option A).
#
# install-console-user.sh installs a root-owned copy of this script as /usr/local/sbin/rig-console-deploy,
# from the commit you reviewed. Run THAT copy, as yourself, in a clean shell (see the runbook):
#     rig-console-deploy
# not the one in the repo: agents can edit files on /mnt/c, including this one (MA-016 finding 1).
#
# It deploys only what you've COMMITTED: agents can still edit the working folder, so the commit you
# reviewed is the boundary.
#   1. refuses if dashboard/ or setup/ has uncommitted changes;
#   2. copies the commit into a fresh clone (no config or hooks from the agents' repo), shows the commits
#      and files changed in dashboard/ and setup/ since the last deploy, and asks;
#   3. unpacks it into root-owned, read-only staging and runs the smoke test there as the user "nobody";
#   4. copies dashboard/ to /opt/rig-console, updates this script and the rig helper from the same commit,
#      records the commit in /var/lib/rig-console/deployed, and restarts.
set -euo pipefail
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin   # never a planted sudo or git
REPO="@REPO@"   # filled in by install-console-user.sh
case "$REPO" in @*) REPO="$(cd "$(dirname "$0")/.." && pwd)" ;; esac   # not installed yet: run from the repo
DEST=/opt/rig-console
MARK=/var/lib/rig-console/deployed
SELF=/usr/local/sbin/rig-console-deploy
SUDO=/usr/bin/sudo
# Never let the agents' repo config run anything: no fsmonitor, hooks, pager or external diff (MA-016 finding 1),
# and no .gitattributes filters or textconv (attributes read from the empty tree, PL-033).
EMPTY_TREE=4b825dc642cb6eb9a060e54bf8d69288fbee4904
safe_git() { /usr/bin/git --attr-source=$EMPTY_TREE -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.pager=cat -c diff.external= --no-pager "$@"; }

if [ -n "$(safe_git -C "$REPO" status --porcelain --untracked-files=no -- dashboard/ setup/)" ]; then
  echo "dashboard/ or setup/ has changes that aren't committed:"
  safe_git -C "$REPO" status --short --untracked-files=no -- dashboard/ setup/ | sed 's/^/   /'
  echo "Review and commit them (or discard them), then run this again. Nothing deployed."
  exit 1
fi
COMMIT="$(safe_git -C "$REPO" rev-parse --verify HEAD^{commit})"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
# A fresh clone has its own clean config and no hooks; everything below runs git there.
safe_git clone --quiet --no-local --no-checkout --no-hardlinks "$REPO" "$WORK/repo"
G() { safe_git -C "$WORK/repo" "$@"; }
# A committed symlink would install whatever it points at, and --stat doesn't show it (MA-021 R2-2).
LINKS="$(G ls-tree -r "$COMMIT" -- dashboard setup | awk '$1 == "120000" {print $4}')"
if [ -n "$LINKS" ]; then
  echo "These are committed as symlinks, which deploys refuse:"; echo "$LINKS" | sed 's/^/   /'
  echo "Nothing deployed."; exit 1
fi

LAST="$($SUDO cat "$MARK" 2>/dev/null || true)"   # /var/lib/rig-console is the console user's
if [ -n "$LAST" ] && [ "$LAST" = "$COMMIT" ]; then echo "Commit ${COMMIT:0:7} is already live. Nothing to do."; exit 0; fi
if [ -n "$LAST" ] && G cat-file -e "$LAST^{commit}" 2>/dev/null; then
  echo "Commits touching dashboard/ or setup/ since the last deploy (${LAST:0:7}):"
  G log --format='   %h %an, %ar: %s' "$LAST..$COMMIT" -- dashboard/ setup/
  echo "Files:"
  G diff --stat "$LAST" "$COMMIT" -- dashboard/ setup/ | sed 's/^/   /'
  FROM="$LAST"
elif [ -n "$LAST" ]; then
  echo "The last deployed commit (${LAST:0:7}) isn't in the repo any more (history rewritten?)."
  echo "So there's no diff since then: read the whole of dashboard/ and setup/ at ${COMMIT:0:7} (d) before deploying."
  FROM=""
else
  echo "First deploy: everything in dashboard/ at commit ${COMMIT:0:7} ($(G log -1 --format='%an, %ar: %s' "$COMMIT"))."
  FROM=""
fi
# Read the changes here, from the clean clone: never with plain git in the agents' repo (MA-021 R2-1).
while true; do
  read -rp "Deploy commit ${COMMIT:0:7}? d shows the full changes first (q leaves the viewer). [y/N/d] " OK
  case "$OK" in
    d|D) if [ -n "$FROM" ]; then G diff --no-ext-diff --no-textconv "$FROM" "$COMMIT" -- dashboard/ setup/
         else G grep -I -n "" "$COMMIT" -- dashboard/ setup/ ':!dashboard/tests/fixtures'; fi | less -R ;;   # every line
    y|Y) break ;;
    *) echo "Nothing deployed."; exit 1 ;;
  esac
done

# Staging is root-owned and read-only to everyone else, so nothing can change it between the test and the
# copy. The smoke test runs committed code, so it runs as "nobody": it can't use your sudo, touch your files
# or change the staging (MA-016 cross-check).
STAGE="$($SUDO mktemp -d /var/tmp/rig-console-stage.XXXXXX)"
trap 'rm -rf "$WORK"; $SUDO rm -rf "$STAGE"' EXIT
G archive "$COMMIT" dashboard setup | $SUDO tar -x --no-same-owner -C "$STAGE"
$SUDO chown -R root:root "$STAGE"
$SUDO chmod -R u=rwX,go=rX "$STAGE"
echo "Smoke test on that commit (as the unprivileged user 'nobody')..."
$SUDO -u nobody env -i PATH=/usr/bin:/bin HOME=/tmp TMPDIR=/tmp python3 -B "$STAGE/dashboard/tests/smoke.py" \
  > "$WORK/smoke.log" 2>&1 || { tail -20 "$WORK/smoke.log"; echo "Smoke test failed: nothing deployed."; exit 1; }
tail -1 "$WORK/smoke.log"

echo "Copying..."
$SUDO mkdir -p "$DEST"
# Code only: no runtime state, caches or tests.
$SUDO rsync -a --delete --exclude 'state/' --exclude '__pycache__/' --exclude 'tests/' "$STAGE/dashboard/" "$DEST/"
$SUDO chown -R root:root "$DEST"
$SUDO chmod -R u=rwX,go=rX "$DEST"
# This script and the rig helper come from the same reviewed commit.
sed "s#@REPO@#$REPO#" "$STAGE/setup/deploy-console.sh" > "$WORK/deploy"
$SUDO install -o root -g root -m 755 "$WORK/deploy" "$SELF"
$SUDO install -o root -g root -m 755 "$STAGE/setup/rig-owner" /usr/local/lib/rig-console/rig-owner
echo "$COMMIT" | $SUDO tee "$MARK" >/dev/null
$SUDO systemctl restart rig-dashboard
sleep 2
systemctl --no-pager --lines=3 status rig-dashboard | head -5
echo "Deployed commit ${COMMIT:0:7} to $DEST. The console's health list shows it under \"Console isolation\"."
