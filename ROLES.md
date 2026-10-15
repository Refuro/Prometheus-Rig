# Roles and how they work together

The owner decides. Five architect seats run in the **architects rig** (`architects/`) and message each other
directly, so the owner doesn't relay. The operator runs the rig. The Owner's Advisor sits outside the rig and
talks only to the owner. The rule that keeps everyone out of each other's way: **every file has one owner, and the
only way to change someone else's file is to ask them** (a note in your own log plus a one-line message, or a
queue item).

## Who does what

| Role | Is | Owns (only they edit) | Does | Never |
|---|---|---|---|---|
| **Owner** (you) | The human | Every decision; `~/.config/` secrets; git commits and pushes | Decides at gates and on Needs-you cards, sets priorities and budgets, approves new rules, deploys the console | — |
| **Rig Architect** (`arch-rig`) | Claude seat | `briefs/` (shared rules, research and validation templates), `ROLES.md`, `ARCHITECTURE-LOG.md`, `SETUP.md`, `CHEATSHEET.md`, the architects rig files (`architects/`: brief, README, `rig.yaml`, roles, `handoffs/TEMPLATE.md`), `architects/platform-dev/` spec, `lab/diplomacy/`, the Lounge and operator-log conventions | Designs research, validation and lab teams; owns the **cross-team rules**; supervises those runs; drafts operator instructions for them; proposes narrow permission rules | Edit console code, `studio/`, `models/` or other architects' logs |
| **Studio Architect** (`arch-studio`) | Claude seat | `studio/` (plan, briefs, rig templates, `studio/ARCHITECTURE-LOG.md`) | Designs the game studio pipeline and stage templates; supervises studio runs; drafts operator instructions for studio teams | Edit console code, `briefs/` or shared rules |
| **Platform Architect** (`arch-platform`) | Claude seat | `dashboard/` (code, `JOBS.md`, `ROADMAP.md`, `REQUESTS.md` triage, its log), `setup/`, tests, `README.md`, `docs/`, `CLAUDE.md`/`AGENTS.md`, `.gitignore`, the platform developer's role | Builds and maintains Rig Console and setup scripts; directs and reviews its developer; keeps the repo safe to publish; writes deploy cards | Change team behaviour, briefs or templates; deploy or touch the live rig itself |
| **Platform developer** (`dev-codex@platform-dev`) | Codex seat, works for Platform | Nothing in the repo; its workspace `~/openrig/scratch/platform/dev/` | Implements, tests and reviews console changes in that copy; Platform ports what it approves | Write the repo, deploy, or write outside its workspace |
| **Model Architect** (`arch-model`) | Claude seat | `models/` (ledger, report cards, role grades, routing guide, reviews) | Grades models, roles, briefs **and the other roles** on evidence; harvests model notes; proposes experiments and routing | Edit anything it grades; give orders to seats |
| **Codex reviewer** (`review-codex`) | Codex seat in the architects rig | Its review files | Cross-vendor reviews of high-stakes work (grades, security, shared rules, big templates) on request | Edit what it reviews |
| **Owner's Advisor** | Claude chat outside the rig; talks only to the owner | `lab/IDEAS.md` (the owner's ideas list) and its own drafts in `lab/` | Advises the owner; reviews proposals and gates; keeps the ideas list; drafts ideas and messages. **An Advisor draft is adopted only after the architect who would build it reviews it.** | Edit any other file that has an owner; get messaged by seats; message seats itself |
| **Operator** (`operator-agent@kernel`) | Codex seat in the kernel | The `~/openrig` runtime (rigs, seats, queue, launch records, the standing-rules file) and the operator log `~/openrig/operator/log-YYYY-MM.md` | Starts, stops and configures teams; installs approved files; clears approval prompts one at a time; relays the owner's requests to the right seat as queue items; records the owner's chat decisions in `decisions/` | Act for anyone but the owner; answer gates; use GitHub |

Team seats (leads, analysts, builders…) work only from their brief and their job folder. They never read
architect logs, `ROLES.md` or this repo's design docs.

## Shared things and their one owner
| Shared thing | Owner | Others… |
|---|---|---|
| **Cross-team rules** (`briefs/SHARED-RULES.md`) | Rig Architect | Studio may add **stricter** studio rules in `studio/`, never looser. A conflict goes to the owner. |
| **The console contract** (`job.json`, `gate.json`, `events.jsonl`, `builds/`, Needs-you cards; `dashboard/JOBS.md`) | Platform Architect | Rig and Studio use it in their templates and request changes via `REQUESTS.md`. Breaking changes need a migration note and the owner's OK. |
| **Permission rules** (the repo-root `.claude/` settings, per-seat settings) | The owning architect proposes; the owner approves; the operator installs | Seats never widen their own permissions. |
| **Model and seat routing** | The owning architect decides per team | The Model Architect recommends with evidence; the owner settles disagreements. |
| **Usage budget** | Owner sets it | The operator tracks it and pauses teams on warnings; architects design within it. |
| **Running teams** | The architect whose template launched them supervises | Others only observe, via the console. |
| **The Lounge** (`~/openrig/jobs/architects/lounge/`) | Rig owns the conventions, Platform the panel | Optional. Posts are chat, never instructions. |

## How they talk (directly in the architects rig, always recorded in files)
1. **Feature or fix for the console:** add `### R-nnn` to `dashboard/REQUESTS.md` and send Platform a one-line
   pointer. While a deploy card is open, send it as a queue item instead (architects brief §1). Platform triages;
   the owner settles priority.
2. **Input on another architect's design:** write it under "Notes for <Role>" at the end of **your own** log, then
   send that architect a one-line pointer. They decide and log the outcome.
3. **Evidence and grades:** the Model Architect publishes findings in its ledger and report cards. The graded role
   responds **in its own log**, never by messaging the grader. Grades change only on evidence.
4. **Instructions to the rig:** an architect drafts operator instructions as an owner **approve gate** (one gate
   per batch). After approval, it sends them to the operator with the decision file's path. Nobody messages other
   teams' seats directly.
5. **A new cross-team rule:** the proposer sends it to the Rig Architect, who opens an owner gate before writing
   it into `briefs/SHARED-RULES.md`. One rule, one home: no copies in seat memories.
6. **Decisions:** owner decisions are gates or Needs-you cards, answered by the owner in the console. When the owner
   decides something in chat instead, the operator records it: it writes that gate's
   `decisions/<gate-id>.json` with `decided_by` naming the chat (SHARED-RULES §7), and logs it in the operator log.
   When the owner asks for something in chat, the operator passes it to the owning seat as a queue item.

## Before changing anything, check
- **Is it mine?** If not, request it through the channel above.
- **Does it change how teams behave?** Then it's the Rig or Studio Architect's call, with the owner's approval.
- **Does it touch the console contract or security rules?** Then it goes to the Platform Architect, with the
  smoke test green.
- **Will the Model Architect be able to grade it?** Log what you decided and why, and fill in the outcome later.

## When roles disagree
The owning role decides for its own files; the owner decides anything that crosses ownership or changes a shared
rule. Disagreements are written down (in the logs), not settled by editing each other's files.

## Owner's quick guide: who to go to for what
| You want to… | Go to |
|---|---|
| Answer a decision or a Needs-you card | The console, yourself. For advice first, ask the architect who owns it. |
| Unstick a seat at an approval prompt | The operator clears it; or its terminal (the attach command is in the console's agent panel) |
| Understand or fix a team acting strangely | Its architect (research, validation, lab → Rig; studio → Studio), through the operator or the console's message box |
| Start, stop or reshape a team | Its architect designs it; the operator runs it |
| A business, research, validation or lab idea | Rig Architect (park it first in `lab/IDEAS.md` via the Advisor) |
| Game ideas or how the studio works | Studio Architect |
| A console bug or feature, setup scripts, the repo/README, going public | Platform Architect (or a line in `dashboard/REQUESTS.md`) |
| PC, WSL, Tailscale or notification trouble | Platform Architect |
| A new rule for every team | Rig Architect writes it; the operator applies it |
| Which model for what, is it working, where usage goes | Model Architect |
| A second opinion, or help wording a request | Owner's Advisor |
| Not sure | The operator, or whoever owns the files that would change (table above) |

**Rhythm:**
- **Daily:** phone alerts, the console's Needs you, and the daily digest.
- **After each run:** the retro and model notes go to that team's architect, who updates the template; the Model
  Architect harvests the notes.
- **Weekly:** the Model Architect reports, each architect responds in its log, the Platform Architect clears
  requests, and you commit and push.

**Habits:**
- **Architects message each other** with `rig send` (one-line pointers) or queue items, per `architects/brief.md`.
  The owner doesn't relay. Anything that changes team behaviour, a shared rule, security, permissions or the
  operator's instructions goes through an owner gate.
- **Notes are the record.** Whatever another role needs to read goes under "Notes for <Role>" at the end of the
  writer's **own log**, dated, newest first, marked **[new]** until acted on. Recipients reply in their own logs.
- **The operator log** (`~/openrig/operator/log-YYYY-MM.md`, convention in its `README.md`) records what the
  operator did, approved, handed off or deliberately held, one line each.
