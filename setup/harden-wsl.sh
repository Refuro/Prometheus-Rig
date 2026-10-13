#!/usr/bin/env bash
# R-005 step 3, option A: close the two ways any process in WSL can become root.
# Run as yourself, between runs:   bash setup/harden-wsl.sh
# It changes one thing itself (Windows interop off in /etc/wsl.conf) and tells you how to do the other
# (sudo needs your password), because editing sudo rules from a script can lock you out.
set -euo pipefail
if [ "$(id -u)" = 0 ]; then echo "Run this as yourself, not with sudo."; exit 1; fi

echo "== Your password"
if sudo passwd -S "$USER" | awk '{exit !($2=="P")}'; then
  echo "   You have a password set: good. Check you know it: sudo -k; sudo true"
else
  echo "   You have NO usable password. Set one first:  sudo passwd $USER"
  echo "   Then run this script again."; exit 1
fi

echo "== Windows interop off"
# Keeps your existing [boot] and other settings; sets [interop] enabled=false and appendWindowsPath=false.
sudo python3 - <<'PY'
import configparser, io
p = "/etc/wsl.conf"
c = configparser.ConfigParser(); c.optionxform = str
c.read(p)
if not c.has_section("interop"): c.add_section("interop")
c.set("interop", "enabled", "false"); c.set("interop", "appendWindowsPath", "false")
buf = io.StringIO(); c.write(buf)
open(p, "w").write(buf.getvalue())
print(open(p).read())
PY
echo "   Takes effect after 'wsl --shutdown' (PowerShell). That stops every team: do it between runs."

echo "== Passwordless sudo"
FOUND="$(sudo grep -rn 'NOPASSWD' /etc/sudoers /etc/sudoers.d 2>/dev/null | grep -v '/etc/sudoers.d/rig-console' || true)"
if [ -z "$FOUND" ]; then
  echo "   None found besides the console's own narrow rule: good."
else
  echo "   Found these lines. Remove the one that gives YOU passwordless sudo:"
  echo "$FOUND" | sed 's/^/     /'
  echo "   Edit safely with:  sudo visudo -f <that file>   (keep a second terminal open with 'sudo -s' until it works)"
  echo "   If you ever lock yourself out: in PowerShell, 'wsl -u root' still opens a root shell from Windows."
fi

cat <<DONE

After 'wsl --shutdown' and reopening Ubuntu, these must FAIL:
    /mnt/c/Windows/System32/wsl.exe -u root id
    sudo -n true
and the console's health list must show "Console isolation" green.
DONE
