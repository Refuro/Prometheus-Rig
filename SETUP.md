# OpenRig setup

This folder holds setup scripts and notes. The rig itself will live inside
WSL at `~/openrig`, not here: OneDrive syncing and Windows-mounted folders are
slow for git, tmux and SQLite, and can corrupt them.

## Step 1: WSL2 + Ubuntu  (done 2026-10-11)

Result: Ubuntu 24.04, Node v22.23.3, tmux 3.4, git 2.43.0, RTX 4080 SUPER
visible in WSL (16 GB, driver 591.86). Linux user: you.

Follow-up (done, PATH verified clean): stop WSL from inheriting the Windows PATH (Windows npm globals
were leaking in). Inside Ubuntu:

    printf '[boot]\nsystemd=true\n\n[interop]\nappendWindowsPath=false\n' | sudo tee /etc/wsl.conf

then `wsl --shutdown` from PowerShell and reopen Ubuntu.


1. Open **PowerShell as Administrator** and run:

       wsl --install -d Ubuntu-24.04

2. **Restart the PC.**
3. Ubuntu opens (or launch it from the Start menu). Pick a Linux username
   and password.
4. Back in a normal PowerShell, apply the WSL settings:

       Copy-Item "$env:USERPROFILE\OneDrive\Documents\Projects\OpenRig\setup\wslconfig.txt" "$env:USERPROFILE\.wslconfig"
       wsl --shutdown

5. Open Ubuntu again and run the bootstrap:

       bash /mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/setup/bootstrap-wsl.sh

6. Paste the output back to Claude.

## Step 2: Remote access from the laptop
Tailscale on both machines, SSH into WSL. (Deferred until after step 3,
since we're at the desktop now.)

## Step 3: Local model  (done 2026-10-11)

Winner: gemma4:12b as the default local model. Test results (model-test/):
both passed strict-JSON and tool-call format; gemma was faster (90-200 tok/s
vs ~70) and clearly better on the skeptic task (caught the utility-data API
problem and churn risk; qwen's tests were vaguer and partly off-target).
qwen3-coder:30b kept for possible coding seats; remove with `ollama rm` if
disk is tight. Single run, small sample: revisit if gemma struggles in real use.

Ollama installed natively on Windows (simplest GPU path); WSL reaches it at
http://localhost:11434 through mirrored networking. Ollama has no Qwen3-Coder 14B; candidates checked on ollama.com:
- gemma4:12b (~8 GB): fits fully on the 16 GB GPU with room for context.
- qwen3-coder:30b (19 GB, MoE, ~3B active): spills partly into RAM; the
  smarter-but-slower experiment.

## Step 4: Minimal rig  (done 2026-10-11)

Smoke test passed: starter team (dev-build = Claude Code, dev-review = Codex
GPT-6-Astra) in ~/openrig. Chain operator -> builder -> reviewer -> operator
worked through the durable queue; builder cut its draft 160 -> 130 words to meet
the limit, reviewer verified independently (wc -w). Output:
~/openrig/handoff-smoke-test.md. Both seats idle afterwards.
Snapshots: setup/rig-snapshots.sh mirrors agent screens to snapshots/ every 10s
so Claude can read them directly.


Installed in WSL: Claude Code + Codex CLI (both logged in), OpenRig CLI.
`rig setup --no-herdr` complete; `rig doctor` all OK (cmux warning is optional,
ignore). Daemon listens on 127.0.0.1:7433.
Dry run reviewed: setup edits ~/.claude.json and ~/.codex/config.toml (trust
managed workspaces), plus per-project .claude/settings.local.json (status line,
auto-accept edits inside the project) and .mcp.json. Acceptable.
Choices: core profile, --no-herdr (plain tmux; fewer moving parts on WSL),
Standard permission policy, never YOLO. Keep the kernel (operator + advisor)
but watch Pro usage.

`npm install -g @openrig/cli`, then a 3-seat rig: Claude lead, Codex
implementer, local-model researcher.

## Decisions
- Rig runs on this desktop in WSL2; the Ubuntu laptop reaches it remotely.
- Local model runs on Windows (Ollama), shared by WSL agents over localhost.
- WSL does not inherit the Windows PATH, so Windows Node/npm can't shadow Linux tools.
- WSL capped at 16 GB RAM to leave room for Windows and model offload.

## Tooling research (2026-10-11)
- Start from OpenRig's shipped starter rigs (first-project, research-team,
  adversarial-review) instead of writing RigSpecs from scratch.
- Local-model seats: OpenRig's Pi adapter + the pi-ollama extension
  (auto-discovers Ollama models). Review its source before installing.
- Shared memory: plain markdown decision/experiment logs in the rig repo first.
  Upgrade path: Basic Memory MCP (also plain markdown, no lock-in).
- Reddit: self-service API access closed (Nov 2025) and unauthenticated .json
  reportedly blocked (May 2026). Don't plan the research pod around Reddit
  MCP servers; use web search/fetch, app-store reviews, review sites, HN.
- Skip for now: Claude Code Agent Teams (Claude-only, ~3-4x tokens),
  oh-my-claudecode / other orchestrators (would overlap with OpenRig).

## Always-on measurement
- setup/install-autostart.sh: snapshot + activity logger as a systemd service.
- setup/install-wsl-keepalive.ps1: Windows logon task keeping Ubuntu (and the
  agents' tmux sessions) alive when no terminal is open.

## Rig Console (dashboard)
- Auto-start: `bash setup/install-dashboard-service.sh` (once). Restart after changes:
  `sudo systemctl restart rig-dashboard`. Settings: `~/.config/rig-console.env`.
- Laptop/phone access (not set up yet):
  1. Install Tailscale on this PC (Windows) and on the laptop/phone; sign in to the same account.
  2. In `~/.config/rig-console.env` set `HOST=0.0.0.0` and `RIG_CONSOLE_TOKEN=<long random string>`
     (generate one with `openssl rand -hex 24`), then restart rig-dashboard.
  3. Allow port 8800 into WSL (PowerShell as admin):
     `New-NetFirewallHyperVRule -Name RigConsole -DisplayName "Rig Console" -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Protocol TCP -LocalPorts 8800`
  4. On the laptop/phone open `http://<PC's Tailscale name>:8800/?token=<token>` once; a cookie remembers it.
- Phone push: set `NTFY_TOPIC=<hard-to-guess name>` in the env file, install the ntfy app, subscribe to that
  topic. Alert text is sent through ntfy.sh, so keep it to non-sensitive projects.
