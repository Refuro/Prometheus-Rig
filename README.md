# prometheus-rig

My local multi-agent setup on OpenRig (WSL2 Ubuntu on the PC named Prometheus): research, validation and game-studio teams,
plus **Rig Console**, a dashboard for watching and steering them from desktop or phone.

| Folder | What's in it |
|---|---|
| `dashboard/` | Rig Console: `serve.py` (server), `store.py` (SQLite event store), `gates.py` (decisions and playable builds), pages (`index`, `graph`, `runs`, `decide`, `play`, `m` for phones). See `dashboard/JOBS.md` and `dashboard/ROADMAP.md`. |
| `briefs/` | Team briefs and shared rules (web access rule v2). Agents read copies from `~/openrig/briefs/`. |
| `setup/` | WSL bootstrap, snapshot logger, dashboard and keep-alive services. |
| `studio/` | Game studio plan and rig specs. |
| `model-test/` | Local model (Ollama) evaluation harness and results. |
| `runs/` | Run logs. |

Setup notes: `SETUP.md`. Day-to-day commands: `CHEATSHEET.md`.

Not in the repo: live snapshots, research mirrors, dashboard state and the event database
(`~/.local/share/rig-console/console.db`). Secrets live in `~/.config/` inside Ubuntu.
