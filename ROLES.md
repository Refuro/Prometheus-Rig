# Roles and how they work together

Five roles run this setup. The rule that keeps them out of each other's way:
**every file has one owner, and the only way to change someone else's file is to ask them through a
file they read.** The owner is the hub and has the final say.

## Who does what

| Role | Is | Owns (only they edit) | Does | Never |
|---|---|---|---|---|
| **Owner** (you) | The human | Every decision; `~/.config/` secrets | Decides at gates, sets priorities and budgets, approves new rules, relays instructions to the operator | — |
| **Rig Architect** | Claude chat session | `briefs/` (shared rules, research and validation templates), `ARCHITECTURE-LOG.md`, `SETUP.md`, `CHEATSHEET.md` | Designs research and validation teams; owns the **cross-team rules**; supervises research and validation runs; drafts operator prompts for those teams | Edit console code, studio files, or other architects' logs |
| **Studio Architect** | Claude chat session | `studio/` (plan, briefs, rig templates, `studio/ARCHITECTURE-LOG.md`) | Designs the game studio pipeline and stage templates; supervises studio runs; drafts operator prompts for studio teams | Edit console code, `briefs/`, or shared rules |
| **Platform Architect** | Claude Code session in this repo | `dashboard/` (code, `JOBS.md`, `ROADMAP.md`, `REQUESTS.md` triage, its log), `setup/`, tests, `README.md`, `docs/`, `CLAUDE.md`/`AGENTS.md`, `.gitignore` | Builds and maintains Rig Console and setup scripts; keeps the repo safe to publish; implements requests | Change team behaviour, briefs or templates; touch the live rig |
| **Model Architect** | Opus session (+ Codex reviewer) | `models/` (ledger, report cards, role grades, routing guide) | Grades models, roles, briefs **and the four other roles** on evidence; proposes experiments and routing | Edit anything it grades; give orders to seats |
| **Operator** | Codex seat in the rig (kernel) | `~/openrig` runtime: rigs, seats, queue, the standing-rules file seats read | Starts, stops and configures teams; enforces standing rules; closes gates for chat decisions | Act on anyone but the owner; answer gates; use GitHub |

Team seats (leads, analysts, builders…) work only from their brief and their job folder. They never read
architect logs, `ROLES.md` or this repo's design docs.

## Shared things and their one owner
| Shared thing | Owner | Others… |
|---|---|---|
| **Cross-team rules**: decisions in files, gates, web access rule, no GitHub, fresh sessions, dry runs, no spending or contacting people without approval | Rig Architect (`briefs/`) | Studio may add **stricter** studio rules in `studio/`, never looser. A conflict goes to the owner. |
| **The console contract**: `job.json`, `gate.json`, `events.jsonl`, `builds/` (`dashboard/JOBS.md`) | Platform Architect | Rig and Studio use it in their templates and request changes via `REQUESTS.md`. Breaking changes need a migration note and the owner's OK. |
| **Model and seat routing** (which model in which seat) | The owning architect decides per team | The Model Architect recommends with evidence; the owner settles disagreements. |
| **Usage budget** | Owner sets it | The operator tracks it and pauses teams on warnings; architects design within it. |
| **Running teams** | The architect whose template launched them supervises | Others only observe, via the console. |

## How they talk (all through the owner, all in files)
1. **Feature or fix for the console:** add `### R-nnn` to `dashboard/REQUESTS.md`. The Platform Architect triages it; the owner settles priority.
2. **Input on another architect's design:** write it under "Notes for <Role> (input, not edits)" at the end of **your own** log. The owner points the other architect at it, and they decide and log the outcome.
3. **Evidence and grades:** the Model Architect publishes findings in its ledger and report cards. The owning architect responds in its own log (accepted, rejected and why, or an experiment proposed).
4. **Instructions to the rig:** architects draft operator prompts; **the owner sends them**. No architect messages seats or the operator directly.
5. **A new cross-team rule:** the proposer drafts it, the Rig Architect writes it into `briefs/` after the owner approves, and the operator adds it to the standing-rules file seats read. One rule, one home: no copies in seat memories.
6. **Decisions:** always gates in job folders, answered by the owner in the console. Decisions made in chat get their gates closed by the operator.

## Before changing anything, check
- **Is it mine?** If not, request it through the channel above.
- **Does it change how teams behave?** Then it's the Rig or Studio Architect's call, with the owner's approval.
- **Does it touch the console contract or security rules?** Then it goes to the Platform Architect, with the smoke test green.
- **Will the Model Architect be able to grade it?** Log what you decided and why, and fill in the outcome later.

## When roles disagree
The owning role decides for its own files; the owner decides anything that crosses ownership or changes a
shared rule. Disagreements are written down (in the logs), not settled by editing each other's files.

## Owner's quick guide: who to go to for what
| You want to… | Go to |
|---|---|
| Answer a decision, approve a plan, pick pitches | The console, yourself. For advice first, ask the architect who owns that team. |
| Unstick an agent at an approval prompt | Its terminal (the attach command is in the console's agent panel) |
| Understand or fix a team acting strangely | Its architect (research/validation → Rig, studio → Studio). They diagnose and draft a prompt; you send it to the operator. |
| Start, stop or reshape a team | Its architect designs it; the operator runs it |
| A business, research or validation idea | Rig Architect |
| Game ideas or how the studio works | Studio Architect |
| A console bug or feature, setup scripts, the repo/README, going public | Platform Architect (or a line in `dashboard/REQUESTS.md`) |
| PC, WSL, Tailscale or notification trouble | Platform Architect |
| A new rule for every team | Rig Architect writes it; the operator applies it |
| Which model for what, is it working, where usage goes | Model Architect |
| Not sure | Whoever owns the files that would change (table above) |

**Rhythm:**
- **Daily:** phone alerts and console decisions.
- **After each run:** the retro goes to that team's architect, who updates the template.
- **Weekly:** the Model Architect reports, each architect responds in its log, the Platform Architect clears requests, and you commit and push.

**Habits:** the owner sends every operator prompt personally, and points architects at each other's
"Notes for <Role>" sections instead of relaying them in full.
