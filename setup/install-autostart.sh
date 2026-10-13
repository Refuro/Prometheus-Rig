#!/usr/bin/env bash
# Run in Ubuntu once:  bash /mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/setup/install-autostart.sh
# Makes the snapshot/activity logger a system service that starts whenever
# Ubuntu starts and restarts itself if it crashes.
set -euo pipefail
SCRIPT="/mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/setup/rig-snapshots.sh"
# Stop a manually started copy so there aren't two loggers.
tmux kill-session -t snapshots 2>/dev/null || true
sudo tee /etc/systemd/system/rig-snapshots.service >/dev/null <<UNIT
[Unit]
Description=OpenRig agent snapshots and activity log
After=local-fs.target

[Service]
User=$USER
Environment=HOME=$HOME
ExecStart=/bin/bash $SCRIPT
Restart=always
RestartSec=10
# Copies fill the page cache, and systemd counts it against the service (3.6 GB on 2026-10-12).
# Past MemoryHigh the kernel reclaims that cache first; MemoryMax is a backstop (Restart=always recovers).
MemoryHigh=256M
MemoryMax=1G

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable rig-snapshots.service
sudo systemctl restart rig-snapshots.service   # picks up a changed unit or script
sleep 3
systemctl --no-pager --lines=0 status rig-snapshots.service | head -3
echo "Done. Check: systemctl status rig-snapshots"
