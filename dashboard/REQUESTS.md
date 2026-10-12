# Requests for the Platform Architect

Anyone (the owner, or the Rig, Studio or Model Architect) adds a request; the Platform Architect triages it.
Format: `### R-nnn Title (from, date)`, then what's needed and why, and `Status:` (open / in progress /
done PL-nnn / declined, with the reason).

### R-001 Soft gate maximum (Rig Architect, 2026-10-12)
The owner has gone over gate maxima by note (friends-1: 4 of max 3). Add an optional `"max_soft": true` to
`gate.json`: allow going over with a confirm, and record it in the decision. Document it in JOBS.md.
Status: open. Triaged (PL-001): accept. Effort S, risk low. An additive contract change, so no migration needed. The decision records `"over_max": true` and its `.md` says so. Confirm happens in the page (no browser dialog). Needs a restart.

### R-002 Approve/deny agent permission prompts from the console (Rig Architect, 2026-10-12)
Show the exact pending command; Approve once / Deny with a confirm tap; log every answer; the token is
required. Prompt formats differ between Claude Code and Codex: verify the keystrokes on both before
shipping. Security-sensitive: write a PL entry with the threat model first.
Status: open. Triaged (PL-001): accept in principle, **blocked on R-005**. Effort L, risk high. Until seats can't reach the console API, they could approve their own prompts. Design: approve once only (never "always"). At press time, re-read the screen and send keys only if the prompt text still matches the hash you saw. Deny = Esc. It needs a test seat on the live rig, which is your call.

### R-003 Validation view (Rig Architect, 2026-10-12)
A funnel for `validation.json` (prospects → sent → replies → samples → paid) and a red banner when
`stopped` is true. See `briefs/validation-brief-1.md` section 7.
Status: open. Triaged (PL-001): accept. Effort M, risk low. Changes: read `validation.json` from any job, not only `research/`; make `stopped` a real alert so it pushes to the phone; show `waiting_on_user` in Needs you. Desktop and phone. Needs a restart.

### R-004 Split serve.py (Rig Architect, 2026-10-12)
See ROADMAP "Architecture: when to grow up". Behaviour unchanged; the smoke test must stay green.
Status: open. Triaged (PL-001): accept, after characterisation tests for `graph()` alerts. Effort M, risk medium. Flat modules (`auth.py`, `api.py`, `live.py`, `actions.py`), not folders, at this size. Needs a restart.

### R-005 Seats can act as the owner through the console (Platform Architect, 2026-10-12)
See PL-001 risk 1. Steps:
1. Alert on decision files the console didn't write.
2. Require the cookie for POSTs from loopback too.
3. Run the console as its own Linux user, with a token file seats can't read. Step 3 needs your OK.
Effort M, risk medium. Needs a restart.
Status: open

### R-006 Isolate agent-written builds and research files (Platform Architect, 2026-10-12)
See PL-001 risk 2. Serve `/play/` from a second port (a separate origin, so no cookie and no API access).
Add `sandbox` and `nosniff` to `/data/`. Phone access also needs `tailscale serve` for the second port.
Effort S–M, risk low. Needs a restart.
Status: open

### R-007 System diagram (owner, 2026-10-12)
A setup graph like the README's that shows the whole system, viewable in the dashboard.
Status: done PL-002 (`dashboard/system.html`, plus `docs/SYSTEM.md` for GitHub)
