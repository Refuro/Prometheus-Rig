# Working in this repo

This is **prometheus-rig**: an OpenRig agent-team setup, Rig Console (`dashboard/`), team briefs and the
game studio templates. Read `README.md` first.

- **Which role are you?** The owner names it. Code in `dashboard/`, `setup/` and tests belongs to the
  **Platform Architect**: read `PLATFORM-ARCHITECT.md` before changing it. Briefs and shared rules
  belong to the Rig Architect; `studio/` belongs to the Studio Architect. Requests for console changes
  go in `dashboard/REQUESTS.md`.
- **Test before committing:** `python3 dashboard/tests/smoke.py` must pass.
- **The repo is public:** no secrets, personal details or run outputs. Secrets live in `~/.config/`.
- **Never touch the live rig** (`~/openrig`, tmux seats, `rig` commands), and never push or use GitHub,
  unless the owner asks.
