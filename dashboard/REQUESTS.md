# Requests for the Platform Architect

Anyone (the owner, or the Rig, Studio or Model Architect) adds a request; the Platform Architect triages it.
Format: `### R-nnn Title (from, date)`, then what's needed and why, and `Status:` (open / in progress /
done PL-nnn / declined, with the reason).

### R-001 Soft gate maximum (Rig Architect, 2026-10-12)
The owner has gone over gate maxima by note (friends-1: 4 of max 3). Add an optional `"max_soft": true` to
`gate.json`: allow going over with a confirm, and record it in the decision. Document it in JOBS.md.
Status: open

### R-002 Approve/deny agent permission prompts from the console (Rig Architect, 2026-10-12)
Show the exact pending command; Approve once / Deny with a confirm tap; log every answer; the token is
required. Prompt formats differ between Claude Code and Codex: verify the keystrokes on both before
shipping. Security-sensitive: write a PL entry with the threat model first.
Status: open

### R-003 Validation view (Rig Architect, 2026-10-12)
A funnel for `validation.json` (prospects → sent → replies → samples → paid) and a red banner when
`stopped` is true. See `briefs/validation-brief-1.md` section 7.
Status: open

### R-004 Split serve.py (Rig Architect, 2026-10-12)
See ROADMAP "Architecture: when to grow up". Behaviour unchanged; the smoke test must stay green.
Status: open
