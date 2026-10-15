# Handoff: Platform Architect (written by the Platform Architect chat session, 2026-10-12)

## 1. Scope in one paragraph
I own the codebase. That covers:
- Rig Console (`dashboard/`) and its contract (`JOBS.md`, `NICHES-SCHEMA.md`);
- `setup/`, the smoke test (`dashboard/tests/smoke.py`), `README.md`, `docs/`, `CLAUDE.md`/`AGENTS.md`
  and `.gitignore`;
- my log `dashboard/ARCHITECTURE-LOG.md` (PL-001 to PL-014), `ROADMAP.md`, and triage of
  `REQUESTS.md`.

My charter is `PLATFORM-ARCHITECT.md`, with the security invariants. I took the console over from the
Rig Architect (PD-013).

Edges in practice:
- The **Rig Architect** owns the shared rules and the team briefs. Rules that only work if the console
  enforces them come to me as code: PD-016 to PD-019 became launch records, decision fingerprints and
  rig pinning.
- The **Studio Architect** files requests (R-012 to R-015) and owns the builds and asset formats it writes.
  I own how the console reads them (`build.json`, the asset manifest).
- The **Model Architect** reviews my security work, re-tests it and grades me. It owns `models/`, which the
  Models page reads but never writes.

## 2a. Checkpoint 2026-10-14 22:35Z, before the PD-033 restart: read this first
- **Live:** commit 466bf4c. PL-060 (release command), PL-061 (dead pages, audit H) and PL-062 (runner) are all
  deployed and verified. No deploy card is open, so `dashboard/` and `setup/` aren't frozen.
- **The runner:** `/usr/local/sbin/rig-platform-check` was installed by hand by the owner after the deploy missed
  it. The operator verified it is root:root, mode 755, hash 06740982…. The operator installed the 9 exact rules and
  retired 3.
- **After the restart:** the operator runs one native probe per subcommand (PD-033 step 4). Then use
  `/usr/local/sbin/rig-platform-check <name>` instead of the raw commands:
  - smoke-repo, smoke-candidate, pages, dip, release-harness;
  - deployed-diff, logger-state, git-status, git-log.
  The candidate copy is at `scratch/platform/candidate/`.
- **Lesson (sent to Rig):** a new install step in the deploy first runs one deploy later. Each such change needs a
  first-time manual step on its card.
- **To fix in the next release:** the comment at `setup/deploy-console.sh` line 121 overclaims. Root ownership
  fixes the commands, not the test code they run.
- **Now: the owner's public-readiness batch** (qitem-20261014221407, which I lead). Owner pushes; agents never
  push. Steps:
  1. **Scan** the tracked tree and history for personal or secret content, without printing secrets: personal
     paths, tokens, the Tailscale name, `.claude/`, `.codex/`, `_to_delete/`. Check `.gitignore`. Inputs:
     - Rig's file list (qitem-20261014221617, closed into this row);
     - Model's MA-032 `models/reviews/public-readiness-evidence.md`, which covers the three findings, what in
       models/ can be published and what must stay out, and the history notes.
  2. **Propose path templating** to Rig (qitem-20261014221643, still open). The owner wants no personal paths
     in tracked files, while the live specs keep working.
  3. **README:** three sentences, the three findings, the diagram moved up, a status line.
  4. **Replay recording:** `docs/replay.webm` and `.gif`, under 10 MB, from private sanitised data.
  5. **Developer review,** then one Needs you card with the exact `git rm` list. Flag history exposure
     separately; never rewrite history myself.
- **Performance assessment:** the measurement ran (`scratch/platform/perf/measure.mjs`, results in
  `perf/results.json`, not yet read or written up). Next step: write `scratch/platform/perf/assessment.md`
  for the owner, an assessment only, no migration.
- **Approved list** (qitem-20261014192418): H done. Next is C, then K, D, the Model notes flag, Ideas, A, M,
  L, F, J, E, G, B. It's parked behind the readiness batch. After it: daily summaries (qitem-20261014202147),
  then mobile and Jobs (qitem-20261014203020).
- **Developer hand-back:** the developer hands each task back with `rig queue handoff` (role.md step 3).
- **Never edit `dashboard/` or `setup/` while a deploy card is open** (memory `freeze-until-deployed`).
- **Waiting on others:** Rig on retiring the Niche board picker (qitem-20261014044150). Rig's combined gate.
- **Later:** R-027 phase 2, after a week of page counts. The Assets tab reading Studio's manifest v1 (R-013).
- **Test tools:** `scratch/platform/page-check.mjs`, `dip-check.mjs`, `graph-perf.mjs`, `release/test_*.py`.
  `CHECK_REPO=<copy>` points them at a scratch copy. They must strip `NTFY_TOPIC` and point every folder at
  temporary copies (the operator caught gaps on 2026-10-14).
- **Permission rules (2026-10-14):** the operator installed exact per-file `cmp` and `py_compile` rules
  (owner-approved). They are installed but NOT effective in this session: both probes still prompted at
  16:5xZ. They load at the next authorized natural restart. Until then, the operator approves once per call.
  Never save permissions from inside this session.
- **Habits:** one shell command per call, with no `$`, backticks, pipes or chains (SHARED-RULES §4). Don't
  claim a command ran without a prompt (memory `cant-see-own-prompts`). No acknowledgment-only replies
  (shared rules v1.10 §4b).

## 2. Current state (as of 2026-10-12/13 morning; superseded by 2a where they differ)
- **The console** runs as systemd `rig-dashboard` from the repo folder, on port 8800, with builds on a
  second port, 8801 (R-006).
- **Phone access** is through Tailscale Serve: 443 → 8800 and 8443 → 8801. The owner set up both.
- **Pages:**
  - Live (the graph, home);
  - Decisions, Builds;
  - under More: Niche board, Runs, Models, System;
  - the phone page `m.html`.
- **Security done** (PL-008 to PL-014): every change needs the sign-in cookie, even locally; Host
  allowlist with the Tailscale name pinned; decision fingerprints and rig pins; launch records route
  decisions to the right lead; builds sandboxed on their own port and limited to the build folder; no
  token means no changes.
- **R-005 step 3 (option A, chosen by the owner)** is written but not run. It's in PL-013 and four
  scripts:
  - `setup/install-console-user.sh`;
  - `setup/harden-wsl.sh`;
  - `setup/deploy-console.sh`;
  - `setup/rig-owner`.
  After it runs, the console runs as `rigconsole` from `/opt/rig-console`, with secrets in
  `/etc/rig-console/env`. Interop goes off and sudo needs a password.
- **Smoke test:** 121/121 (`python3 dashboard/tests/smoke.py`). Browser checks:
  `node ~/openrig/scratch/platform/page-check.mjs [page.html…]` (private fixture console; screenshots in
  `shots/`).
- **Uncommitted:** PL-015 to PL-017 (`setup/`, `serve.py`, `features.py`, new `outbox.py`, `notify.js`,
  `graph.html`, `m.html`, `JOBS.md` §3c, smoke, `.gitignore`); the owner commits.
- **Restarted 2026-10-13 00:32:04** (verified, PL-021). PL-014 to PL-020 and the operator outbox are live.
- **Live as of 01:15:51 (restart-console-3, verified):** PL-021 to PL-023.
  - R-020: approval waits go to the operator, proven live (4 items, no duplicates).
  - The standalone Needs you page at `/needs.html` (To do / Questions cards; `JOBS.md` §4b).
  - Decisions go to the gate's own lead.
- **Live as of 01:47:39 (restart-console-4, verified):** PL-024 Messages (`/messages.html`) and PL-023's
  summary fix.
- **Source-only, for the next restart:** decision-routing hardening in `gates.tell_whom` (one `rig ps`;
  failure tells nobody; every choice logged). Until then the Rig Architect forwards misrouted decisions.
  Smoke test 161/161.
- **Waiting on others:** the Rig Architect posts the owner's real cards (qitem-20261013081749-dacfdd4a).
- **Rule for myself:** once a restart gate is open, don't edit server files until the restart is
  verified.
- **PL-016 console messaging:** done; gate `pl-016-send-anyway` decided keep-off.
- **PL-017 notifications:** the operator's outbox (`launches/notify/`) and the `NOTIFY` list. Report to the
  operator: qitem-20261013070153-aa09b8f1. The first live push is the Bridge-ready note after the restart.
- **PL-018 Needs you sections and task cards** (R-018, `JOBS.md` §4b): built, 128/128.
- **Restart gate `restart-console-1`** (in `~/openrig/jobs/architects/gates/`) batches PL-014 to PL-018 and
  the PL-015 logger steps. When it's decided "done", verify before reporting: the
  `systemctl status rig-dashboard` start time is after the decision. Don't call the console's HTTP API.
  Then tell the operator the outbox is live.
- **Lounge (PL-019, R-019):** the panel is built (`lounge.html`, `/api/lounge`). The Rig Architect owns the
  posting rules (`jobs/architects/lounge/README.md`). It rides `restart-console-1`.
- **PL-020:** `milestones.json` adopted (`JOBS.md` §6), a top-level gate `play`, and the `production` type.
  The milestones view (R-015) is still to build. Smoke test 133/133.
- **PL-015, the snapshot logger hang (2026-10-12):** fixed in source, waiting on the owner's review. The
  live service runs the script from the repo, so any restart picks it up. The owner also needs to stop the
  running `cp` and delete the 22 GB in `research-mirror/assets-1/tools/`.
- **Kickoff list** (`architects/kickoff/arch-platform.md`): items 1 and 2 done (except moving the mirrors
  off OneDrive). Next: 3 graph lag, 4 R-003, then MA-015 (duplicate lines on the Models page).

## 3. Open items
| Item | Waiting on | Next step | Where it's recorded |
|---|---|---|---|
| Option A (R-005 step 3) | Rig Architect confirms no seat needs sudo or Windows programs; Model Architect reviews the scripts | Owner runs the PL-013 runbook between runs; record the step-6 checks in PL-013 | PL-013, notes to Rig and Model |
| MA-013 fixes re-test | Model Architect | Close in my log when it reports | PL-014 |
| Back-up pages `graph.v1.html`, `graph.v2-backup.html`, `index.v1.html` | Owner deploys PL-060 (release fix), then PL-061 | Review-3 clean. Re-apply from `scratch/platform/held-h/` once PL-060 is live | PL-005, PL-060, PL-061 |
| Pin the Tailscale name in `RIG_CONSOLE_HOSTS` | Owner (or the installer's prompt) | Health shows "Tailscale name" until done | PL-014 |
| R-012 audio and `model_preview` in gate options | Me | Next build item | `REQUESTS.md` |
| Remove the research checkpoint picker (`research.html`, `m.html`) | Me | Before the next research run (checkpoints are gates, PD-016) | PL-005 |
| R-011 log growth | Me | Rotate the activity log daily out of OneDrive, keeping today and yesterday there; pane captures stay at a stable path (AD-025). Launch-records mirror dropped (Model reads `~/openrig/launches/` directly); hard-coded path fixed in PL-015 | `REQUESTS.md`, PD-016 |
| R-014/R-013 per-job page with Docs and Assets tabs | Me | Manifest v0 is in `studio/briefs/asset-manifest.md` | `REQUESTS.md` |
| Alert-rule tests, then R-004 | Me | Tests first | PL-006 |
| R-003 validation view | Me | Before validation-1 Phase 2 sends | `REQUESTS.md` |
| R-015 `milestones.json` draft | Me | Draft, then Studio reviews | `REQUESTS.md` |
| R-002 | Step 3 done | Last | `REQUESTS.md` |
| `/api/verify` for leads | Rig Architect adopting the rule | Build if adopted | PL-013, note to Rig |
| Headless browser for page checks in a seat | Done: owner approved Playwright in `~/openrig/scratch/platform/` | Confirm Chromium on first use | role.md |

## 4. Decisions that matter and why
- **Decisions come only from the owner's browser.** Every POST needs the sign-in cookie, local too; the
  console never answers a gate itself; with no token, changes are off (PL-008, PL-014).
- **Routing comes from trusted records, not job files.** The job name is the folder name; the rig and lead
  come from the operator's launch record (`~/openrig/launches/<job>.json`), checked against `rig ps`, then
  pinned (PL-010, PL-012). Don't go back to trusting `job.json` for routing.
- **Builds run on their own port, 8801,** with no cookies or console API there. They're sandboxed and
  limited to the build folder (R-006, PL-011, PL-014). Never serve agent HTML from 8800.
- **Option A over B or C** (PL-011, PL-013): harden the shared user, then the console as its own user. B
  (agents as their own user) is the follow-up if A's residual risk becomes unacceptable.
- **Model notes live in `model-notes.jsonl` in the job folder,** matched on `harvest_hash` (MA-009). My
  earlier `model_note` events idea is withdrawn (PL-009 miss).
- **Health has levels** (required, advisory, optional), so the pill isn't red for optional things like
  Ollama (PL-006).
- **Stdlib only.** There's no build step and no npm. Pages are single files with inline JS; diagrams are
  hand-written SVG and Mermaid (PL-002).

## 5. The owner: how they like to work
- **"Keep your replies short. I read on my phone a lot."** Lead with the answer, then a few lines.
- **"I'll do all commits myself."** Never run git writes; offer a commit message if asked.
- **"Smoke test green before every commit, and add checks for what you change."**
- **"Stdlib only, no new dependencies without my OK."**
- **"Never weaken the security invariants listed in the charter."**
- **"The repo is public: no secrets or personal details."**
- **"Never touch the live rig… and tell me when a change needs a dashboard restart."**
- **Values looks:** "prioritize usability and readability and aesthetics… You can get creative" (the graph
  redesign). They notice ugly or cramped pages, especially on the phone.
- **Wants to see the system in the console,** not only in docs: "I meant I want it viewable in the
  dashboard".
- **Annoyed by being a message bus** between architects (the reason for this rig). End each piece of work
  by naming whose notes are new, and message them yourself now.
- **Makes security calls quickly** once given plain options with a recommendation ("A works").

## 6. Working knowledge
- **Paths:**
  - repo: the OneDrive project folder under `/mnt/c` (9p DrvFs, no Linux permissions,
    everything owned by uid 1000);
  - jobs: `~/openrig/{jobs,research}`;
  - launch records: `~/openrig/launches`;
  - installed briefs: `~/openrig/briefs`;
  - console state: `dashboard/state/` (fingerprints, job pins), until option A moves it to
    `/var/lib/rig-console`.
- **Environment overrides** (all in `serve.py`'s top lines): `RIG_SNAPSHOTS`, `RIG_RESEARCH_DIR`,
  `RIG_STATE_DIR`, `RIG_DB`, `RIG_JOBS_CONFIG`, `RIG_BIN` (`""` disables `rig send`; may carry a sudo
  prefix), `RIG_MODELS_DIR`, `RIG_BRIEFS_DIR`, `RIG_LAUNCHES_DIR`, `RIG_CONSOLE_HOSTS`, `PLAY_PORT`,
  `RIG_PLAY_PUBLIC_PORT`, `RIG_CONSOLE_TOKEN`, `NTFY_TOPIC`, `NTFY_CLICK`.
- **The smoke test** starts its own server on fixtures (`dashboard/tests/fixtures/`), never the live one.
  Add a fixture rather than pointing a test at real data.
- **Things that broke before:**
  - `index.html` forwarding to `/` looped forever: it forwards to `/graph.html` now, and a smoke check
    guards it.
  - A file write to the OneDrive folder once silently reverted. Re-read the file after writing.
  - Tests passed vacuously when no gates were open: make the fixture create what you test.
  - A cookie left on the test client leaked into the remote-access checks: clear it first.
- **Health "Console isolation"** stays amber or red until option A is done. That's expected, not a bug.
- **Restart** today: `sudo systemctl restart rig-dashboard` (the owner runs it). After option A it's
  `bash setup/deploy-console.sh`, which runs the smoke test, lists the changes and asks before copying.
- **The activity log** grows about 1 MB an hour in OneDrive (R-011). Measured APIs are fast; that's the
  only scaling problem.
- **Notes convention:** my log ends with "Notes for other roles", one sub-section per role, newest first,
  dated, **[new]** until acted on. Others reply in their own logs; read theirs for replies to me.

## 7. Read first
1. `PLATFORM-ARCHITECT.md` (charter and security invariants)
2. `dashboard/ARCHITECTURE-LOG.md`: PL-001 for the overview, PL-009 for the threat model, PL-013 and
   PL-014 for the current work, then the Notes section
3. `dashboard/REQUESTS.md`
4. `dashboard/JOBS.md` (the contract)
5. `models/reviews/R-005-R-006-security.md` (the Model Architect's review)
6. `briefs/SHARED-RULES.md` §1 and §7 (rules the console enforces)
7. `dashboard/serve.py`, top 120 lines (settings, auth helpers)
8. `docs/SYSTEM.md` (how the pieces connect)

## 8. Don't
- Don't make the console answer, close or default a gate, even to "help". Only the owner decides.
- Don't trust anything in a job folder for routing, auth or rendering: escape agent text and serve agent
  files sandboxed.
- Don't add a library (a 3D viewer, a Markdown package, a JS framework) without the owner's OK.
- Don't restart or deploy the console yourself, or touch other teams' rigs. Tell the owner.
- Don't move `snapshots/` pane captures (Studio relies on the path, AD-025). The activity log can move.
- Don't edit `briefs/`, `studio/`, `models/` or other architects' logs. Write a note in mine and message
  them.
- Don't change `JOBS.md` in a way that breaks running jobs without a migration note and an owner gate.
