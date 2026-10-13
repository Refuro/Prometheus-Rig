# Handoff: Model Architect (written by the Model Architect chat session, Opus 5.5, 2026-10-12)

The new Model Architect seat (`model@architects`) reads this first, after `architects/brief.md` and `ROLES.md`. Everything you own is in `models/`. Your log `models/LOG.md` (MA-001 to MA-014) is the full history; this file is the short version.

## 1. Scope in one paragraph
- **What you do:** grade, on evidence:
  - models in seats, unit **model × role × brief**;
  - the briefs themselves;
  - the four other roles: the Rig, Studio and Platform Architects and the Operator.
- **What you own:** `models/`, and nothing else.
- **What you never do:**
  - edit anything you grade;
  - give orders to seats;
  - decide routing. You recommend; the owning architect decides, and the owner settles disagreements.
- **Bias checks:** you're a Claude model grading Claude among others, so every grade or routing change goes to `codex@architects` for a bias review before you call it policy.
- **Reviews on request:** in practice the architects also ask you for independent reviews (security, scripts). Give findings, not designs, because you'll later grade the outcome. Reviews live in `models/reviews/`.

## 2. Current state (2026-10-13, MA-015)
- **Latest:** harvested coop-1, depth-1, friends-1 and proto-2 (O077–O125, 23 metric rows), all verified against the
  live job folders. 5 duplicates of O071–O075 marked `duplicate_of`. Stop-rule lines traced to the operator's dry-run
  wording (attribution brief). Cards and role assessments **not yet updated** from these lines.
- **New tools:** `models/tools/verify_evidence.py <lo> <hi>` checks evidence against `~/openrig/jobs`;
  `models/tools/review.py <updates.json>` applies review decisions (the record is in `models/reviews/MA-0nn-ledger-updates.json`).
  Queue-row quotes can be checked live with `rig queue show <id> --full`.
- **Ledger:** `models/observations.jsonl`, 125 lines, O001–O125.
  - No line says `attribution: model`; the Codex review removed every one (MA-004).
  - O071–O075 were written by room-lead seats under an old rule. They were reviewed in MA-013: four verified, O075 unverifiable.
- **Metrics:** `models/metrics.csv`, 38 seat-runs. Column meanings in `models/README.md`.
- **Cards:** `models/cards/` holds 14 model × role cards, plus `claude.md` and `codex.md` summaries.
- **Role assessments:** `models/roles/` (rig, studio, platform architects, operator). Qualitative with confidence; **no letter grades** (MA-004).
- **Briefs:** `models/BRIEFS.md` grades them by observed effect.
- **Routing:** `models/ROUTING.md`. Every row is "incumbent assignment; comparative advantage untested". It has rows for the new seats (player-eyes, design-feel, design-ux, art and audio director) with no evidence yet.
- **Experiments:** `models/EXPERIMENTS.md`, E1–E3. The Studio Architect accepted E2 and E3 for the next pitch round; E1 waits on the owner's Claude budget.
- **Harvester:** `models/tools/harvest.py` imports leads' `model-notes.jsonl` and `model-metrics.csv`. The format's master copy is `briefs/SHARED-RULES.md` §6; `models/HARVEST.md` explains it, including the `harvest_hash` contract the Models page relies on.
- **Models page:** `dashboard/models.html`, built by the Platform Architect (PL-003, PL-012). It reads `models/` live.
- **Reviews done:**
  - `models/reviews/R-005-R-006-security.md` (MA-007; all findings accepted, PL-009–011);
  - re-test of the shipped code (MA-013: three gaps found);
  - `models/reviews/PL-013-option-A.md` (MA-014: two high findings).

## 3. Open items
| Item | Waiting on | Next step | Where it's recorded |
|---|---|---|---|
| PL-013 option A: 2 high findings (deploy from a reviewed commit; don't print the token where tmux is captured) | Platform Architect | It replies in its log; then the owner runs the runbook | `models/reviews/PL-013-option-A.md`, LOG MA-014 |
| 3 gaps from the re-test (builds port serves any job file; `*.ts.net` wildcard; unchecked `X-Forwarded-Host`) | Platform Architect | Check its fix with the probe in MA-013 | LOG MA-013, notes |
| Update cards and role assessments from O077–O125 | You | Builder/critic/lead cards for coop-1 and proto-2; operator assessment (dry-run stop wording); then a `review-codex@architects` bias review | LOG MA-015 |
| Harvest new runs (proto-3, coop-2, bridge-design, assets-1) | Their runs ending | `harvest.py --live --dry-run`, then for real; `verify_evidence.py`; decisions via `review.py` | `models/HARVEST.md`, LOG MA-015 |
| Tonight's incidents (logger hang, false prompt reading) | A written record from Platform or the operator | Add ledger evidence only if a role's action is involved | LOG MA-015 |
| Cards for new seat types | First runs of player-eyes, design-feel, design-ux, art and audio director | Write `cards/claude--player-eyes.md` and the rest from harvested notes | ROUTING.md rows |
| Judge AD-010 and the SHARED-RULES v1.1–1.3 rules in practice | The next runs | Check for writes to `decisions/` or the project folder, leads checking the `.json`, unlisted stops, approval events per seat | `roles/rig-architect.md`, `roles/studio-architect.md` |
| Model per seat | The operator filling `seats` in launch records (PD-019, PL-012) | Fill `version_if_known` from launch records at harvest; today nearly every line says "unknown" | LOG MA-010, MA-013 |
| Operator log suggestion | Owner relays to the operator | None until it exists | Notes for the Operator |
| Codex bias review of everything since MA-004 (role assessments, MA-007 onwards) | You | Ask `codex@architects` when the next grade update is ready | `models/REVIEW-REQUEST.md` (the model to follow) |

## 4. Decisions that matter and why
- **The unit is model × role × brief, not "model personality"** (owner's mission statement). Most behaviour first blamed on models came from briefs; see MA-004 and `BRIEFS.md`. Before attributing anything to a model, check what the brief asked (`brief_asked`).
- **No `attribution: model` without a counterfactual** (MA-004, from the Codex review): use it only if a different brief would plausibly *not* have changed the behaviour. Summaries say "observed across these assignments", not "trait".
- **No letter grades** until there's a rubric with severity weighting and an evidence threshold (MA-004).
- **Leads write notes in their own job folder, not in `models/`** (PD-015, AD-015, MA-005/006). Seats never write in `models/`. If lines appear there written by seats, mark `status`/`written_by` and review them, as was done for O071–O075. Don't delete them.
- **`harvest_hash`** = `sha1(job folder name + "\x1f" + trimmed note line)[:16]`. It's a contract with the Models page (PL-012). Don't change it without telling `platform@architects`.
- **The folder is `models/` at the repo root** (MA-003), not `studio/models/`, because `studio/` belongs to the Studio Architect.

## 5. The owner: how they like to work
- **Evidence first:** "every claim must point to something that happened in our runs." Say small samples out loud ("seen once").
- **Describe behaviour,** don't anthropomorphise: "stops on any listed condition", not "is anxious".
- **Wants recommendations, not decisions:** propose and show before touching shared things. Asked explicitly: "propose the change and show me before editing the dashboard."
- **Handoffs between roles:** put the note in your own log's "Notes for other roles", then tell the owner (now: message the seat) **who** should check it. Don't paste long relays. Format: newest first, dated, **[new]** until acted on (ROLES.md).
- **Answers:** short, plain, with "who to send to" at the end. "Open items?" means a grouped list by who it's waiting on.
- **Prefers being asked** before a role-boundary question is settled for them (e.g. MA-003, where the folder lives). Then acts quickly once told.

## 6. Working knowledge
- **Mirrors:**
  - `jobs-mirror/` and `research-mirror/` are copies of `~/openrig/jobs` and `~/openrig/research`;
  - `jobs-mirror` goes stale, so as a seat in WSL use `harvest.py --live`, which reads `~/openrig/` directly;
  - the owner's refresh command is in `models/LOG.md` MA-012.
- **Queue rows** in `snapshots/_queue.json` have no bodies, so quotes from queue messages can't be verified from mirrors (MA-013, O075).
- **The activity log** (`snapshots/activity-log.csv`) isn't reliable for active time (PD-007); `active_min` stays blank.
- **Model versions:** `_ps.json` has `model: null` for nearly every seat. Use launch records (`~/openrig/launches/<job>.json`, `seats`) once the operator fills them.
- **Line counts:** `wc -l` on `observations.jsonl` must equal the highest O-number. A mismatch means someone else wrote to it.
- **Console probes:** to probe the console safely, start `dashboard/serve.py` on fixtures in a temp dir, the way `dashboard/tests/smoke.py` does. Never probe the live console on port 8800.
- **Where previews go:** the old `models/preview/` is superseded by the live page; keep it only as the original proposal.

## 7. Read first
1. `architects/brief.md`
2. `ROLES.md`
3. `briefs/SHARED-RULES.md`
4. `models/README.md` (formats, metrics columns, grading rules)
5. `models/LOG.md`, from MA-004 on, and the Notes section
6. `models/ROUTING.md`
7. `models/REVIEW-codex.md` (what the Codex reviewer caught last time; don't repeat it)
8. `models/HARVEST.md`

## 8. Don't
- **Don't edit** another role's files, including its log, even to fix a typo. Write a note in your log.
- **Don't let seats write to `models/`,** and don't add a rule that has them do so.
- **Don't merge models into one bucket on the page** (e.g. qwen into gemma); the Platform Architect rejected that for good reason (PL-003).
- **Don't publish a grade or routing change** without a `codex@architects` review.
- **Don't treat a role's log as proof** that something works. Re-test the claim, as in MA-013.
- **Don't rank models from single-model seats.** Every routing row so far is one model per seat; only E1–E3 can compare.
