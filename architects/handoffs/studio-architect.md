# Handoff: Studio Architect (current state, 2026-10-14 22:20Z)

Seat `arch-studio@architects`. History lives in `studio/ARCHITECTURE-LOG.md` (AD-001 to AD-035), not here.

## 1. Scope
I own `studio/`: `STUDIO-PLAN.md`, stage templates in `studio/rigs/`, `studio/briefs/`, `studio/setup/` and
`studio/ARCHITECTURE-LOG.md`. Pipeline: pitch rooms → prototype sprints → design team → production
(`studio/rigs/production/`, AD-027). Cross-team rules belong to the Rig Architect (`briefs/SHARED-RULES.md`,
now v1.11); templates point at them, never copy them. Console needs go in `dashboard/REQUESTS.md`.

## 2. Phase and what's running
- **Bridge priority (owner, 14 Oct).** bridge-prod is in m2a (crossings 1-4 grey-box, then a short owner
  depth gate). bridge-design supports it; the design-levels seat is added and working.
- **Gate scope:** m2a is **c01-c04** (`bridge-prod/decisions/m1.json` note 2). Corrected 21:13Z,
  qitem-20261014211308-28ad0ba3453590ea; my miss is logged in AD-034. Check gate lists against decision files.
- **Status at 21:04Z:** c01 and c03 routes complete on the exact sim; c02 and c04 wait on design (q-60).
  T-061 (loader) is the critical path; T-064 proof runner is blocked on it. ETA to the gate is about 02:00-08:00Z
  on 15 Oct (`~/openrig/scratch/studio/eta-2026-10-14-2115Z.md`; that text says c01-c03, corrected in my reply).
- **Oversight (AD-034):** the tech lead checks in at stage boundaries; watchdog `01M4XNYR72JN845VZNAKNHK4YA`
  runs every 4 h. Stop it when Bridge production ends. Course-correct only through the tech lead or the director.
- **Parked by the owner:** coop-2, proto-3, sunrise-design. No co-op recommendation until the owner resumes it.

## 3. Open items
| Item | Waiting on | Next step |
|---|---|---|
| Bridge lag (AD-036) | Tech lead diagnosing (rows qitem-20261015082207-ba56faf2043cbf7b, qitem-20261015082553-4ad4905a6a32a25d) | Cause found 08:34Z: c02 terrain drawing ~82 ms/frame (fix T-094) plus per-frame work growing with history (T-093). Gate waits for a smooth owner build (or owner chooses). Expect: proxy numbers after fixes, then the owner's in-game frame log. The pre-m2b relaunch batch must also copy the current template brief.md (Three checks, determinism-by-price, cost rule), tech-lead role.md, templates/packet.md and templates/architecture.md into bridge-prod, and design-team brief section 4 into bridge-design (AD-036, AD-037; shared rules v1.13 has the canonical cost rule) |
| m2a gate packet | Tech lead | Check it has c01-c04, Pace (hours per crossing, usage stops apart, 20-crossing range), and v1.11 model notes at milestone end |
| E2 answer key | Done 08:00Z: v3 frozen read-only, sha256 361b0bab. Its location is private: see queue row qitem-20261015080133-48eab5a0 (Studio to Model), never a tracked file | At launch, copy the hash and disclosures from the key record beside it into the job's run-record.md; never put the key's location in the job folder or any tracked file. Run compare with `--key` on the frozen copy |
| E2 critic run (AD-035) | Me: when `bridge-prod/gates/m2a.json` exists with no matching decision (the tech lead's before-gate check-in tells me), send the operator an E2 launch row; they verify, launch the two seats and return readiness | When the seats are up: send both start messages together; record times, stops and prompts in `run-record.md`; run `tools/compare.py`; write `model-notes.jsonl` and `model-metrics.csv` (I act as lead); send `results.md` to arch-model naming both files |
| Role block in bridge-prod shared files (owner approved both, `jobs/architects/decisions/bridge-role-guidance.json`) | Operator (qitem-20261015031740-4eebf60c08ada788) | Part 1 done: installed 03:18Z, 7 files verified identical to the template. Role blocks stripped from both shared files 05:20Z (record `ops/studio-role-block-cleanup.json`; any seat restart writes one back). Part 2: when the m2a decision lands, send the tech lead the handoff row (also relay shared rules v1.12 section 4b there: hand result rows back with `rig queue handoff`, settle pending rows before ending a turn), then the operator runs `relaunch.md`; check its grep results (0 after launch and after one restart) |
| GodotSteam | Owner, before m2c | `studio/setup/install-godotsteam.sh <zip> ~/openrig/jobs/bridge-prod` (tested on fake zips only) |
| m2b art | After the m2a gate | Art seats read `bridge-prod/asset-pipeline.md` and `research/assets-1/recommendation.md` first; give a real m2b estimate at the gate |
| Next template batch | Rig's combined gate, for any rule or permission change | AD-031 reviewer worktree, merge-tree pre-approval, AD-032 scaffold mouse fix, brief section 7 checks (repo only, not synced) |
| Platform requests | Platform | R-012 audio in gate options; R-013/R-014 Assets and Docs tabs (manifest v1 now); R-015 `milestones.json` |
| Next pitch round items | Before any new pitch round | Critic anchors + bottom-third ranking (E2 tests this), deck draws, E1/E3, lessons file (AD-011, AD-015, AD-025) |
| Bring down finished rigs | Operator via owner | proto-2, depth-1, coop-1 after their notes |

Done and installed: Studio batch studio-assets-1 (record `bridge-prod/ops/studio-assets-1-installed.json`, checked
21:05Z); manifest v1; STUDIO-PLAN stage 4. The director keeps the approved art
route in `bridge-design/data/art/kit.json` `pipeline.research_recommendation`, not in the bible.

## 4. Decisions that matter
- Prototypes are throwaway; production is a clean Godot 4 + GodotSteam build (AD-009).
- Presentation rules and the player-eyes seat (AD-017, AD-018). Player-eyes judges screenshots only.
- Agents must see the game: builds screenshot every stage and write `build.json`.
- The design team designs the polished, buildable product (AD-020). Feel, art and juice are values with
  checks, never adjectives.
- Art direction makes or breaks the game (AD-021). Approved route: assets-1 gate 2, summarised in each job's
  `asset-pipeline.md`.
- Up to two send-backs; open exploits named first in every gate (AD-010). Cheese policy: bug / degenerate / clever.
- Roles arrive only as send_text startup files. `guidance: []` alone did not stop the shared-file role block.

## 5. The owner
- Ambitious and fast; plays every build and gives blunt, specific feedback.
- Expects a recommendation with reasons, then decides. Never decide for them or reopen a decision they made.
- Short replies, exact commands (say Ubuntu or PowerShell). No spending, accounts, posting or contacting people.
- Original ideas only. Ideas source: `lab/IDEAS.md` (Owner Advisor).

## 6. Working knowledge
- **Sync:** `rsync -a --exclude runs/ <repo>/studio/ ~/openrig/studio/`.
  Template changes don't reach running jobs; copying into one needs an approved operator batch.
- **Test** template changes in `~/openrig/scratch/studio/`, never in a live job.
- **Godot** 4.7.1 in WSL; screenshots via `studio/setup/install-shots-wsl.sh`.
- **Owner `[msg <id>]`:** reply file `~/openrig/jobs/architects/replies/<id>.json`.
- **Queue:** close with `rig queue update <id> --state done --closure-reason no-follow-on --note "..."`; hand off
  with `rig queue handoff`. Use `rig queue create` when `rig send` is refused at a prompt.
- **Supervision:** read `~/openrig/jobs/<job>/` directly, read-only.
- **Ids collide:** x-19 is Shovel the Sunrise (proto) and Borrow My Door (co-op). Always say the title.

## 7. Read first
1. `rig whoami --json`, then my queue.
2. `architects/brief.md`, `ROLES.md`, `briefs/SHARED-RULES.md` (v1.11).
3. `studio/ARCHITECTURE-LOG.md` AD-033 to AD-035.
4. `bridge-prod/milestones/m2/plan.md` and `lead-pace.md`.
5. `studio/rigs/critic-check/README.md`.

## 8. Don't
- Edit outside `studio/` and this handoff, or touch `decisions/`.
- Answer a gate for the owner, or act on a decision file that doesn't exist.
- Change a running job's files without an approved operator batch and telling its lead to re-read them.
