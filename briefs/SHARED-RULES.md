# Shared rules for every team (v1, 2026-10-12)

**Owner of this file:** the Rig Architect (see `ROLES.md`). This is the **one home** for cross-team rules.
Teams follow it on top of their own brief; a team's brief may be stricter, never looser. Seats read this
file. They don't copy rules into their own memory; when it changes, the operator tells active leads.

## 1. Decisions and files
- **Owner decisions are gates.** When the owner must decide, the lead writes `gate.json` in its job folder
  (`dashboard/JOBS.md` section 4) and waits. Never ask in chat; never decide on the owner's behalf.
- **Gates hold owner decisions only.** Stalls, provider errors and usage problems are operational: they go
  to the operator and the console's alerts, never into a gate.
- **Decisions and state live in files.** Before a session is cleared or a seat is replaced, the lead writes a
  handoff note (phase, decisions made and pending, next step). Gates decided in chat are closed by the
  operator.

## 2. When to stop
Stop and wait for the owner **only** for:
1. a native approval prompt;
2. a usage-limit warning;
3. an approved tool failing to run (the tool itself, not your input to it).

Everything else is normal work: wrong paths, malformed edits, compile errors, and failing tests caused by
your own changes are fixed and retried, not reported as stops.

## 3. Transient provider errors
"Model at capacity", "overloaded" and similar messages are **not** usage-limit warnings. Retry the same step
after about 2, then 5, then 10 minutes. After a fourth failure the lead sends **one** note to the operator.
Never open a gate for it, and never switch models to get around it.

## 4. Shell commands (every seat, any model)
- No `$`, backticks or pipes (`|`) in shell text. Pass free text through files (`--body-file`, a temp
  file), not inline.
- One command per call; no `;` or `&&` chains to read or check things.

Why: these patterns trigger approval prompts and stall the team.

## 5. The outside world
- **Web reading:** follow `RESEARCH-WEB-ACCESS-RULE.md` (v2).
- **No GitHub:** never `git push`, `gh`, or any GitHub page or API, unless the owner asks for that
  specific task.
- **No spending, accounts, sign-ups, public posts, or contacting people** unless an approved phase of your
  brief explicitly allows it, and then only as that phase says.

## 6. How runs start and end
- **Fresh session per stage**; keep context lean.
- **Dry run per seat type** before dispatch: permissions, tools and the full handoff path.
- **End-of-run model notes (lead only):** append one line per notable seat behaviour to
  `models/observations.jsonl` and one row per seat to `models/metrics.csv` (format in `models/README.md`;
  path `/mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/models/`). Name the brief or dispatch file
  the seat worked from and whether it asked for the behaviour. Only what you saw, each with a file path or
  quote; write "seen once" when it was. Don't rank models.
