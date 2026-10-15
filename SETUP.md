# Setup notes

How this rig was set up on one Windows PC, and why. **For the install steps, see `README.md` → Getting started.**
This file keeps the decisions behind them. Paths use `<you>` for the Windows and Linux user names.

## Where things run
- **The agents run inside WSL2 (Ubuntu 24.04),** in `~/openrig`, not in the Windows folder that holds this repo.
  OneDrive syncing and Windows-mounted folders are slow for git, tmux and SQLite, and can corrupt them.
- **This repo** lives on the Windows side (`/mnt/c/Users/<you>/…/OpenRig`), so the owner can edit and commit from
  either side.
- **WSL settings** (`setup/wslconfig.txt`, copied to `%USERPROFILE%\.wslconfig`): mirrored networking and a memory
  cap that leaves room for Windows.
- **`/etc/wsl.conf`** turns systemd on and stops WSL inheriting the Windows `PATH`, so Windows Node or npm can't
  shadow the Linux tools:

      [boot]
      systemd=true

      [interop]
      appendWindowsPath=false

  Then run `wsl --shutdown` in PowerShell and reopen Ubuntu.

## OpenRig
- **Install:** `npm install -g @openrig/cli`, then `rig setup --no-herdr` (plain tmux, fewer moving parts on WSL),
  then `rig doctor`. The daemon listens on `127.0.0.1:7433`.
- **What setup changes:** it edits `~/.claude.json` and `~/.codex/config.toml` to trust the managed workspaces,
  and writes per-project `.claude/settings.local.json` and `.mcp.json`. We use the standard permission policy,
  never "YOLO".
- **The kernel** (operator and advisor seats) starts with the daemon. Teams are launched from rig specs: the
  architects rig is `architects/rig.yaml`, and team templates live in `briefs/` and `studio/`.
- **Starting point:** OpenRig's shipped starter rigs, rather than specs written from scratch.

## Always-on services
- **Snapshot and activity logger:** `setup/install-autostart.sh` installs `rig-snapshots` as a systemd service. It
  mirrors agent screens and state every 10 s for the console.
- **Keep-alive:** `setup/install-wsl-keepalive.ps1` (PowerShell, once) is a logon task that keeps Ubuntu and the
  agents' tmux sessions running with no terminal open.

## Rig Console
- **Install once:** `bash setup/install-dashboard-service.sh`. Settings and secrets live in
  `~/.config/rig-console.env`, never in the repo.
- **Releasing changes:** the Platform Architect prepares a release note, and the owner runs the root-owned
  `rig-console-release` started straight from Windows (`wsl --exec /usr/local/sbin/rig-console-release`). It shows
  every changed line, commits only the listed files, then deploys with its own smoke test. See the header of
  `setup/release-console.sh`.
- **Phone and laptop access:** Tailscale on each device (same account, two-factor login). The console stays on
  `127.0.0.1`, and `tailscale serve` publishes it to your tailnet only. Steps are in the README.
- **Push alerts:** ntfy, with a hard-to-guess topic in the env file. On Android, only one VPN runs at a time, so
  Tailscale replaces any DNS-filter VPN app.

## Decisions worth knowing
- **Local models are parked.** Ollama ran on Windows with GPU access, and WSL reached it over localhost.
  `gemma4:12b` passed the format tests, but local models' tool calls failed in real agent loops, so every seat uses
  Claude Code or Codex.
- **Shared memory is plain Markdown:** logs, handoffs and briefs in this repo, with no memory service.
- **Skipped:** Claude Code agent teams (Claude-only, several times the tokens) and other orchestrators that would
  overlap with OpenRig.
- **Reddit isn't a research source.** Self-service API access closed in Nov 2025, and unauthenticated access was
  reportedly blocked in May 2026. Research teams use web search and fetch, app stores, review sites and HN, under
  `briefs/RESEARCH-WEB-ACCESS-RULE.md`.
