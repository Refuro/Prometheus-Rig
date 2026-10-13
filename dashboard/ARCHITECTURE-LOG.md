# Platform architecture log

**Who writes here:** only the Platform Architect (see `PLATFORM-ARCHITECT.md`). Entries are `PL-nnn`:
what, why, what it replaced, and later the outcome, misses included. Read-only for everyone else.

The console's history before the handover is in the Rig Architect's log (`ARCHITECTURE-LOG.md`, PD-001
to PD-013).

## PL-001 Handover assessment (2026-10-12)
**What:** a first read of the codebase, the smoke test and the open requests. No code was changed.

**Baseline:** smoke test 45/45 green on the code as handed over. I ran it in a copy outside WSL
(Python 3.13), not in the service's WSL Python. It took 0.4 s; the charter says about 20 s.

**Data flow (as I understand it):**
1. `setup/rig-snapshots.sh` runs every 10 s. It writes `_ps.json`, `_queue.json`, `_ctx.json`, one
   screen per tmux session and `activity-log.csv` into `snapshots/`.
2. The `serve.py` watcher, also every 10 s, calls `graph()`. That reads the snapshots and builds nodes,
   edges and alerts: limit, approval, frozen, long, handoff, context, plus open gates from
   `gates.list_gates()`. Dismissals apply here.
3. `store.Collector` turns the graph and queue into events in SQLite. It also adds job files and
   `events.jsonl` lines.
4. `features.track_approvals` logs approval waits.
5. `features.push_alerts` sends an alert to `ntfy.sh/<topic>` once it has persisted for 25 s and wasn't
   pushed in the last 6 h. Its Click URL opens `/m.html`, or the decision page for a gate.
6. The pages poll the `/api/*` routes. Decisions go through `POST /api/gate`, which writes
   `decisions/<id>.json` and `.md`, then runs `rig send` to the lead.

**Health:** good for its age. The code is small and readable (~4.4k lines), stdlib only, with numbered
migrations, path overrides and a fast smoke test on fixtures. Alert logic carries real lessons
(PD-007). Weak spots:
- `serve.py` mixes routing, auth, screen parsing and actions.
- The `graph()` alert rules, where every past miss happened, have almost no direct tests.
- `/api/briefs` reads a hard-coded `~/openrig/briefs` with no env override, which breaks charter rule 3's
  "every path is overridable".
- Three backup pages still ship.

**Top three risks:**
1. **Anything on the PC counts as the owner.** Requests from loopback that aren't proxied skip the
   token. Seats run in the same WSL, as the same user, so any seat (or a prompt injection it reads on the
   web) can `curl -H 'X-Rig-Console: 1' localhost:8800/api/gate` and answer its own gate, or use
   `/api/send`. A seat can also simply write `decisions/<id>.json` in its own job folder. So "nothing
   answers a gate on the owner's behalf" holds for the console UI, but not against a seat. This blocks
   R-002 as written: a console that approves permission prompts would let a seat approve its own
   commands.
2. **Agent-written builds run as the console.** `/play/` is served without `Content-Security-Policy:
   sandbox` (it can't use it, because builds need scripts). A build's JavaScript therefore runs on the
   console's origin with the owner's cookie and can POST to any API, including gates. Builds come from
   prototype seats. `/data/` (the research dir) is also served without the sandbox header, so an `.html`
   file written there runs the same way.
3. **The alert logic is the most-fixed area and the least tested.** The four PD-007 misses were all in
   `graph()`, which the smoke test covers only at "returns nodes". A `serve.py` split (R-004) or new
   alert kinds (R-003) could quietly regress them. Characterisation tests come first.

**Also noted (smaller):**
- Setup scripts hard-code `/mnt/c/Users/<name>/…`, which puts a username in a public repo.
- The env template suggests `HOST=0.0.0.0` for Tailscale. PD-010 replaced that with Tailscale Serve to
  localhost.
- The evidence checker fetches any URL an agent writes, LAN addresses included. GET/HEAD only, so this is
  low risk.
- ntfy.sh is public. Alert text (seat names, gate titles) is readable by anyone who guesses the topic.

**Outcome:** pending. Measures: whether risks 1 and 2 are closed before R-002 ships, and whether any
alert regression ships during the split.

## PL-002 System page in the console (2026-10-12)
**What:**
- A new page, `system.html` ("System" in the desktop nav and the phone footer), in three sections:
  - What runs where: four lanes (agents → files → console → you), with live status dots.
  - How a seat's need becomes a phone alert and a decision: eight steps.
  - Who owns what: the roles from `ROLES.md`.
- The status uses only GET APIs that already exist (`health graph gates builds jobs events`). There is no
  server change, so no restart is needed.
- I also wrote `docs/SYSTEM.md`, with the same three views as Mermaid, for readers on GitHub.

**Why:** the owner asked for a system graph like the README's, viewable in the dashboard. Mermaid
needs a CDN or a dependency (rule 2), so the page is plain HTML/CSS. It stacks into one column on a
phone.

**Checked:**
- Smoke test 47/47. New checks: the page is served and linked from both navs.
- Headless Chromium on fixtures at 1366 px (light) and 390 px (dark): no page errors and no sideways
  scroll. The live lines read correctly, including a stopped logger shown in red.

**Miss:** I first built only `docs/SYSTEM.md` (Mermaid for GitHub), because I read "like the one in the
README" as "in the docs". The owner meant the dashboard. I should have asked one question first.

**Debt:** the diagram now exists in three places: the README, `docs/SYSTEM.md` and `system.html`. Any
change to the data flow must update all three in the same commit.

**Redesign (same day, owner feedback: "too much text; use the live graph's design language"):**
- The page is now a map in the live graph's style: dot grid, group boxes, two-line cards, amber dashed
  edges for flow happening now, red for trouble, a detail panel on tap.
- The explanations moved off the map into the panel.
- The 8 steps became "Trace an alert", which plays the journey on the map with a moving spark.
- "Who owns what" became a People view of the same map.
- Edges are drawn from the cards' real positions, so the layout holds at any width. On a phone the
  groups stack with one spine between them, the real edges appear only during a trace, and the caption
  pins to the bottom.
- Checked with headless Chromium at 1440 px (dark and light) and 390 px: overview, node, trace and
  People view. No page errors and no sideways scroll. Smoke test 47/47.

**Outcome:** pending. Measure: the page stays accurate, and the owner uses it.
## PL-003 Models page (R-008) (2026-10-12)
**What:**
- `dashboard/models.html` ("Models" in both navs), with three views:
  - **Seats:** a role × model grid. Each cell shows how often that model ran the seat, the Model
    Architect's confidence, and its strength/failure count. An amber edge marks the seat's current
    holder. Tap a cell for the card in the side panel. `[O0nn]` refs jump to the ledger line.
  - **Evidence:** the ledger as a feed, with model and kind filters and a search. Leads' `model_note`
    events show on top as "not yet reviewed".
  - **Architects:** role assessments and briefs by result.
- `dashboard/models.py` builds `/api/models`, wired into `serve.py` as one route. It is read-only.

**Changed from the Model Architect's proposal (A), and why:**
- **Its own module, not more `serve.py`.** `serve.py` is due a split (R-004).
- **`RIG_MODELS_DIR` override.** Charter rule: every path is overridable, and the smoke test uses
  fixtures.
- **Bad ledger lines are skipped and counted.** The proposal raised an exception for any line missing
  `model`, which would blank the whole page.
- **No model aliasing in the server.** The proposal filed `qwen3-coder:30b` under `gemma4-12b`. That
  merges two different models' evidence, so they stay separate. Only `:` → `-` is normalised, to match
  card file names.
- **A grid instead of per-model tabs and a 12-column table.** The question the page answers is "who
  ran which seat, and how did it go". The table didn't fit a phone. Seat-run flags now show only when
  non-zero, inside the cell's panel.
- **"Draft · not routing policy" in the toolbar, and a one-model-per-seat note in the panel.** Most
  cells are single-model, and a grid invites comparison the evidence doesn't support (MA-004).
- **Proposal B reworked:** leads log a `model_note` event in their own job folder (documented in
  `JOBS.md`, additive, no migration). Proposal B had seats append to `models/`, which:
  - breaks one-owner-per-file;
  - hard-codes a path with a username;
  - lets graded seats write their own evidence.

**Also:** proposal C, the `.gitignore` lines for the ledger, the metrics file and `models/preview/`, was
already applied by the owner. The git index shows none of them was ever tracked.

**Conflict of interest:** this page displays the Model Architect's assessment of me. The panel
renders every role file the same way, unfiltered.

**Checked:**
- Smoke test 54/54. New checks:
  - fixture cards read via the override;
  - a bad ledger line skipped;
  - `gemma4:12b` mapped to its card;
  - a `model_note` event listed;
  - nav links;
  - no POST route.
- Headless Chromium on the real `models/` data at 1440 px (dark, light) and 390 px: grid, a cell,
  Evidence filtered, Architects. No page errors and no sideways scroll.

**Restart needed:** yes (`serve.py` imports `models.py`).

**Outcome:** pending. Measure: the owner and the architects use it to read evidence, not to rank models.

## PL-004 Play builds page (owner request, 2026-10-12)
**What:**
- The page is now a shelf of named games, grouped by sprint, with a filter per sprint. Each card shows
  generated cover art, the game's name and pitch, and a "New" marker until you open it on that device
  (saved in localStorage; nothing is sent).
- Tap a card for its panel: what it's testing, what to judge while playing, controls (keys shown as
  keys), "watch out", known bugs, the lead's verdict, and links to the spec and the review.
- On a phone the panel opens as a bottom sheet.
- `gates.list_builds()` now returns an `info` object per build.

**Why:** the old page was a list of folder names ("x-16") with a Play button, so you couldn't tell
which game was which, or what to look for while playing.

**Where names come from** (first wins per field, all read-only; agent text is escaped on the page):
1. A new optional `builds/<name>/build.json`, documented in `JOBS.md` §5. Additive, so no migration.
2. A gate option whose `play` points at the build.
3. `specs/proto-spec-<name>.md`.
4. The `## <name> <Title>` section of `lead-summary.md`.

Builds with none of these show their folder name and a hint to add `build.json`.

**Checked:**
- Smoke test: a fixture `build.json` names the fixture build.
- Headless Chromium on a copy of proto-1/proto-2/coop-1 builds with their real specs and lead summary,
  at 1440 px (dark, light) and 390 px: shelf, panel, phone sheet. No page errors.

**Restart needed:** yes (`gates.py`).

**Outcome:** pending. Measure: fewer builds show only an id once builders write `build.json`.

## PL-005 Navigation: home is the live graph, a shorter top bar (owner request, 2026-10-12)
**What:**
- **Home is the live graph.** `/` now serves `graph.html`. The Niche board moved to `research.html`;
  `/index.html` forwards home so old links and bookmarks still work. Phone links were updated.
- **A shorter top bar:** Live, Decisions (with its count) and Builds. Everything else sits under More,
  grouped as Research (Niche board, Run report) and Console (Models, System), each with a one-line
  description. When you're on a More page, the button shows its name.
- **New pages go into More, not the bar** (comment in `nav.js`).
- **Health:** the six dots became one pill ("All OK" / "3 issues") that opens the full list. The
  logger's age reads "11 h ago" instead of "39415s ago" (new `age_s` field). The phone view keeps the
  full list.
- **Alerts:** the "Sound" label became a speaker icon.
- **Titles:** pages are titled "<Page> · Rig Console"; the graph was "Rig Graph".

**Why:** the bar had grown to 7 links plus 6 health dots and was getting cut off at the right. The
Niche board only serves research runs: the studio uses gates, and validation will get its own view
(R-003).

**Is the Niche board still used?** Yes, by the research team. The run-2 and money-1 briefs have leads
keep `niches.json` current, and the board is the only view of it. Its checkpoint picker (`/api/decision`)
overlaps with gates; whether research checkpoints should become gates is the Rig Architect's call (note
below).

**Checked:**
- Smoke test 59/59. New checks: `/` is the graph, `/index.html` forwards, the Niche board is at
  `/research.html`, and the bar has three main links.
- Headless Chromium at 1440 and 1024 px: More menu, health list, a More page highlighted. No page
  errors and no sideways scroll.

**Restart needed:** yes (`serve.py`, `features.py`).

**Outcome:** pending.

## PL-006 Platform checkup (2026-10-12, evening)
**What:** a review of code, tests and operations, measured against a copy of the real snapshot data
(17.5 MB activity log, 284 KB queue, 54 seats). No behaviour changed except the miss below.

**Miss (PL-005):** the old `/index.html` forwarded to `/`. Until the dashboard restarted, `/` still
served that same file, so clicking "Rig Console" reloaded forever; the owner hit it. It now forwards to
`/graph.html`, which works before and after a restart, and the smoke test checks it can't point at `/`
again. **Lesson:** test a change in the state the owner will actually be in (old server, new files), not
only after a restart.

**Findings, most important first:**
1. **Security (PL-001 risks 1–2, still open).** Seats can answer their own gates, and builds run with
   the console's rights. The new Builds page invites more playing, so R-006 matters more now.
2. **The alert pipeline can fail silently.** The watcher loop is wrapped in `except Exception: pass`
   (`serve.py`). If `graph()` throws, phone pushes stop and nothing says so. Gate alerts are also
   swallowed on error, and ntfy failures aren't logged. There's no heartbeat in `/api/health`.
3. **Health noise.** Optional services (Ollama, the Windows keep-alive) count as issues, so the pill
   can sit red all day. That teaches you to ignore it, the PD-007 lesson again.
4. **Data growth.**
   - **The activity log** grows about 1 MB an hour (about 15k rows/h). The logger records every seat
     `rig ps` lists, finished rigs included, every 10 s, and the log is never rotated.
   - **The snapshot files** (about 60, plus that CSV) are rewritten every 10 s inside the OneDrive
     folder, so OneDrive has to keep syncing them.
   - **Size-dependent windows.** The console reads fixed-size tails of the log: 600 KB for the
     30-minute strip (33 min today; it will fall short as seat counts grow), 2–5 MB for the run report.
     `timeline()` reads the whole file on every call.
5. **Tests.** 59 smoke checks, but the alert rules in `graph()`, where every PD-007 miss happened,
   still have no direct tests. They're needed before the `serve.py` split (R-004).
6. **Hygiene.**
   - Three backup pages are still served.
   - The colour tokens are copied into 9 pages, and there are three Markdown renderers (decide,
     models, research).
   - `/api/briefs` has a hard-coded path.
   - A username appears in the setup scripts.
7. **Timing.** Validation is at its Phase 0 gate with no sending yet, so R-003 can follow the items
   above. It's needed before Phase 2.

**Proposed order (owner decides):**
1. Quick wins in one restart: R-009, R-010, the backup pages, the briefs path.
2. R-005 steps 1–2, then R-006.
3. R-011, logger and data growth, coordinated with the Rig Architect, who reads `snapshots/`.
4. Alert-rule tests, then R-004.
5. R-001, then R-003 before validation Phase 2.
6. R-002 last.

**Outcome:** pending.

## PL-007 Quick wins from the checkup: R-009, R-010, briefs path (2026-10-12)
**What:**
- **Alert heartbeat (R-009).**
  - The watcher records each round. Errors go to the service log (`journalctl -u rig-dashboard`) with a
    traceback instead of being swallowed.
  - `/api/health` gains "Alerts", which turns red 60 s after the last good round: "stopped: last good
    check 5 min ago (KeyError …). Phone alerts won't arrive."
  - With ntfy set up, "Phone push" shows the last push failure.
  - A failure to read gates now raises a visible "Couldn't check for open decisions" alert instead of
    silently dropping gate alerts.
- **Quieter health (R-010).** Checks have levels:
  - required (default): turns the pill red;
  - advisory (keep-alive): amber, "1 to check";
  - optional (Ollama): grey, "off".

  The phone view's list uses the same colours.
- **`RIG_BRIEFS_DIR`.** `/api/briefs` was the last hard-coded path (PL-001).

**Not done:**
- **The three backup pages.** This session can't delete files on the PC, so they're the owner's
  `git rm`.

**Checked:**
- Smoke test 62/62. New checks: heartbeat reports a recent round, optional/advisory levels, briefs
  override.
- Simulated a dead loop: health reports it red with the error.
- Headless check of the pill and its list: no page errors.

**Restart needed:** yes.

**Outcome:** pending. Measure: the pill is green on a normal day, and a broken watcher shows up within
a minute.

## PL-008 R-005 steps 1–2: decisions only from the owner's browser (2026-10-12)
**What:**
- **Step 1, detection.**
  - The console records a SHA-256 of every decision file it writes
    (`state/decision-fingerprints.json`).
  - Each watcher round checks every `decisions/*.json`. A file the console didn't write, or one changed
    after it wrote it, raises an alert linking to the gate:
    - **urgent:** "the decision for X was written outside the console / changed after you decided it";
    - **gentle:** a `"verdict": "closed"` file, usually the operator closing a gate decided in chat.
  - Files that existed when the check first ran are trusted once, as the baseline.
- **Step 2, prevention.**
  - Every change (POST) needs the sign-in cookie, from this PC too. Without it the console answers 401
    `{"signin": true}`.
  - `/signin` offers the token form on this PC.
  - Every page's top bar shows "Sign in to make changes" when this browser isn't signed in.
  - `/api/session` reports the state.
  - With no token configured, the console can't tell the owner from an agent; it keeps working and
    health shows an amber "No console token set".

**Why:** PL-001 risk 1. Agents run on this PC as the same user, so "local" never meant "the owner". Only
the owner's browser holds the HttpOnly cookie.

**Limits, plainly:**
- An agent that reads `~/.config/rig-console.env` (now forbidden by `SHARED-RULES.md` §1, PD-016) could
  still get the token.
- An agent could also edit the fingerprint file.

Step 3 (the console as its own Linux user) closes both and needs the owner's OK.

**Checked:**
- Smoke test 70/70. New checks:
  - a local change without the cookie is refused;
  - the session reports signed in or out;
  - the local sign-in page works;
  - console-made decisions raise no alarm;
  - a forged decision raises an urgent alert;
  - an operator-style close raises a gentle one;
  - an edited decision is flagged.
- Real browser on localhost: the sign-in button appears, a change is refused (401), sign-in returns to
  the same page, the change then succeeds (200). The cookie is HttpOnly, Secure, SameSite=Lax. No page
  errors.

**Restart needed:** yes. Owner action: sign in once on the desktop browser; the phone is already signed
in.

**Outcome:** pending. Measure: zero decision alerts that turn out to be agents, and no case of the owner
being blocked from deciding.

**Also triaged:** the Studio Architect's R-012 to R-015 (statuses in REQUESTS.md).

## PL-009 Reply to the Model Architect's security review (MA-007), and a threat model (2026-10-12)
**Review:** `models/reviews/R-005-R-006-security.md`. All seven findings are accepted. My replies and
actions are below.

**Miss (PL-008):** I wrote "only the owner's browser holds the cookie" and shipped step 2 as if it bound
seats. It doesn't: the token sits in `~/.config/rig-console.env` and in the server's
`/proc/<pid>/environ`, both readable by the seat user, so step 2 only binds seats once step 3 lands. What
step 2 does block on its own: changes from web pages, via DNS rebinding or a prompt-injected seat browser
(those carry no cookie). I also missed that the code itself runs from `/mnt/c`, where seats can write;
that defeats every step. A review before building would have caught both. For security work I'll ask
for one first.

### Threat model (who R-005/R-006 defend against)
| In scope | Can do today | Defence |
|---|---|---|
| **A seat** (any model, including one prompt-injected by a web page) | Runs as the same Linux user; writes in `/mnt/c/.../OpenRig` (console code included); reads `~/.config/`; can run `rig send`; may reach root via WSL interop (unverified) | Rules today (`SHARED-RULES.md` §1). Enforcement needs the code moved off `/mnt/c`, a separate console user and interop settled (step 3, revised below) |
| **A build** (agent-written JavaScript in the owner's browser) | Runs on the console's origin with the owner's cookie | R-006: a second port that serves only `/play/` |
| **A web page reached by a seat's browser** | DNS rebinding to `127.0.0.1:8800` | Host allowlist (done) plus step 2's cookie for changes (done) |
| **The operator** | Same powers as a seat (a no-sandbox Codex seat) | Same as seats. R-005 does constrain it; it acts for the owner only through files the owner can see (closed gates are flagged) |

Out of scope: someone with the owner's Windows login, phone or Tailscale account.

### Finding by finding
1. **Code on `/mnt/c` (high): accepted; this becomes step 3a.** The service will run from a deployed copy
   under a path the seat user can't write (e.g. `/opt/rig-console`, owned by the console user). A deploy
   script copies `dashboard/` after the smoke test passes. A restart then means "deploy and restart".
2. **WSL interop to root (high): accepted; must be verified before step 3.** The owner runs, in a normal
   Ubuntu terminal (read-only checks, nothing changes):
   - `mount | grep /mnt/c`
   - `/mnt/c/Windows/System32/wsl.exe -u root id`
   - `sudo -n true && echo passwordless-sudo`

   If the second prints `uid=0(root)`, interop must be turned off (`[interop] enabled=false`) or the risk
   accepted in writing. First check whether the keep-alive and the operator need Windows commands.
3. **Host allowlist: done.** Answers only `localhost`, `127.0.0.1`, `::1`, `*.ts.net` and names in
   `RIG_CONSOLE_HOSTS`; anything else gets 421, including HEAD (also newly guarded).
4. **Step 1 is a tripwire: accepted.** The alert now says it catches mistakes and can't prove a decision is
   genuine. After step 3, comparisons will be against a console-owned copy, by content.
5. **Impersonating the owner outside the console.**
   - **(b) Done:** the team's title, question and option titles are quoted (`> `) in `decisions/<id>.md`,
     under "The team's gate". The record says the `.json` fields are the decision.
   - **(c) Partly done:**
     - a job's name is always its folder name (`job.json` can't rename it);
     - two folders with one name raise an alert;
     - a gate's `lead` is honoured only if that seat is in the job's rig (tested with a stub `rig`).

     Still open: the rig itself comes from seat-written `job.json`. That needs a launch record the seats
     can't write, which the operator would keep; it's for after step 3.
   - **(a) `rig send` impersonation:** cross-team, so a note to the Rig Architect below.
6. **R-006 conditions: accepted as written.** The play port will serve only `/play/` static files, the main
   port will stop serving `/play/`, and the smoke test now checks there's no CORS preflight approval.
   Play-port tests come with R-006.
7. **ntfy topic: accepted.** It moves to the console-only env file in step 3; until then, a note to the
   Rig Architect.

### Revised R-005 plan
- **Done:** step 1 (tripwire), step 2 (cookie for changes), the Host allowlist, the decision record (5b)
  and job/lead routing (5c, partial).
- **Next:** R-006.
- **Then step 3, as one change:**
  - 3a, code deployed off `/mnt/c`;
  - 3b, a console user with the token and ntfy topic only it can read;
  - 3c, interop settled.

  Step 3 needs the owner's checks above and an OK, and `rig send` must keep working: the console user
  would get a single sudo rule to run `rig send` as the seat user, nothing else.

### Models page (MA-007)
- **`status`** is shown: on ledger rows ("not yet reviewed" in amber) and in full in the panel, with
  `written_by`.
- **Leads' notes: one channel, the files (PD-015).** The page now lists `model-notes.jsonl` lines in job
  folders that aren't in the ledger yet. My `model_note` event convention is withdrawn from `JOBS.md`; no
  template had adopted it. That was a miss: I invented a second channel the same day the architects
  agreed a different one.
- **Empty cells** all say "not run".

**Checked:**
- Smoke test 79/79. New checks: non-JSON POST, no CORS preflight approval, unknown Host for reads and
  changes, Tailscale name accepted, quoted decision text, `job.json` can't rename a job, duplicate names
  flagged, unharvested notes listed but harvested ones not repeated.
- Lead routing tested with a stub `rig`.

**Restart needed:** yes. If any device stops reaching the console, add its host name to
`RIG_CONSOLE_HOSTS` in `~/.config/rig-console.env`.

**Outcome:** pending: graded by the Model Architect.

## PL-010 Findings 5b and 5c completed: trusted team routing (reply to MA-007 and PD-017) (2026-10-12)
**5b, decision records quote the team's text:** done in PL-009. `decisions/<id>.md` quotes the gate's
title and question (`> `), puts option titles on one line with headings stripped, and says the `.json`
fields are the decision. That matches PD-017 rule 1: leads act on the `.json` only.

**5c, job name, rig and lead from trusted sources:** done.
- **Name:** always the folder name (PL-009). Two folders with one name raise an alert.
- **Rig and lead:**
  - **From the operator's launch record:** `~/openrig/launches/<job>.json` (`RIG_LAUNCHES_DIR`), format in
    `JOBS.md` §3b. It must name the job's real folder. Its `rig` and `lead` win over `job.json` and
    `gate.json`. OpenRig itself can't supply this: `rig ps` has no working-folder field (checked
    `--fields`), and `rig.yaml` sits in the seat-writable job folder.
  - **Without a record:** the console pins the rig it first saw for the job (`state/job-pins.json`). If
    `job.json` later claims another rig, the pin keeps your decisions going to the original team, and an
    alert says so.
  - **A gate's `lead`** counts only if that seat is in the trusted rig (PL-009).
- **Needs:** the operator to write a launch record whenever it starts a team, a one-line rule for the Rig
  Architect. Until then every job runs on its first-seen pin.

**Limits:** the launches folder and the pin file are writable by the seat user until R-005 step 3, the
same caveat as the decision fingerprints. With PD-017's rules, honest seats are covered; enforcement
comes with step 3.

**Checked:**
- Smoke test 83/83. New checks: a job starts on its first-seen team; `job.json` can't move it (pin kept,
  alert raised); a launch record for another folder is ignored; a valid one decides the team.
- **Miss caught before shipping:** my first version of this test read the team from an open gate when
  every demo gate was already decided, so its first two checks passed on empty values. The test now
  makes its own gate and first asserts the starting team.

**Restart needed:** yes.

**Outcome:** pending.

## PL-011 R-006 builds on their own port; the owner's root checks (2026-10-12)
**R-006, done (owner OK'd the second port):**
- **The builds port** (`PLAY_PORT`, default console port + 1 = 8801) serves only `/play/<job>/<file>` from
  inside a job's build folder, with COOP/COEP for Godot and `nosniff`. Reviewer's conditions:
  - **(i)** No pages, no `/api/`, no sign-in, no `?token=`, no cookies set, no changes. Remote requests
    still need the console cookie, which reaches every port; it's HttpOnly, so build code can't read it.
  - **(ii)** The console port answers `/play/` with 404. Play links are `/go/play/...`, which redirect to
    `http://localhost:8801` on this PC or `https://<tailscale name>:8443` from remote devices
    (`RIG_PLAY_PUBLIC_PORT`).
  - **(iii)** The no-preflight test (PL-009) stays.
- **`/data/`** (research files) is now served with `sandbox` and `nosniff`, like `/job/`. That closes
  PL-001 risk 2.

**Checked:**
- Smoke test 93/93. New checks:
  - the builds port serves builds with isolation;
  - it returns 404 for pages, API, sign-in, `/job/` and `nav.js`;
  - it never sets a cookie and accepts no changes;
  - the console port no longer serves builds;
  - redirects are correct locally and via Tailscale;
  - remote builds need the cookie;
  - the Host check applies on the builds port;
  - `/data/` is sandboxed.
- Real browser, signed in, opening a build from the Builds page: it lands on `localhost:8801`,
  `crossOriginIsolated` is true, and the build's `fetch` to read the console API and to POST a change
  are both blocked. `document.cookie` is empty.

**Owner action:** for the phone, run once in PowerShell:
`tailscale serve --bg --https=8443 http://localhost:8801`. Restart needed.

### The owner's checks for R-005 step 3 (MA-007 findings 1–2), results
- **`/mnt/c`:** a 9p/DrvFs mount with `uid=1000,gid=1000` and no `metadata`. Every file there belongs to
  the owner's user and Linux permissions aren't enforced, so a separate console user can't protect code
  kept there.
- **`wsl.exe -u root id`:** prints `uid=0(root)`. Any process in WSL can become root through interop.
- **`sudo -n true`:** succeeds. The owner's user, which the agents also run as, has passwordless sudo.

**What it means:** today every seat can become root two separate ways. Step 3 as planned (a console user
holding the token) adds nothing until both are closed. The real boundary question is that agents and
the owner share one Linux user that is effectively root.

**Options for the owner (decision needed):**
- **A. Harden the shared user**, then do step 3:
  - remove passwordless sudo (you type a password for restarts);
  - set `[interop] enabled=false` in `/etc/wsl.conf`. Nothing in `setup/` calls Windows programs from
    WSL; the keep-alive and Tailscale run from Windows. The operator's own habits need checking first.
  - move the console code to a console-owned path off `/mnt/c`.

  Effort M. Also needs the Rig Architect to check what seats rely on.
- **B. Give the agents their own unprivileged Linux user** (no sudo, interop off), and keep yours. The
  strongest option and the cleanest: your `~/.config`, git and SSH keys stop being reachable at all.
  Effort L. OpenRig, the operator and every launch path change, so it's mostly the Rig Architect's work.
- **C. Accept the residual risk in writing:** rules (PD-016/PD-017) plus what's done (sign-in for
  changes, Host check, separate builds port, tripwires). This stops web pages and builds, and honest
  seats, but not a determined or prompt-injected seat.

**Recommendation:** A now (small, and it removes the instant-root paths), with B as the follow-up if the
agents get web access more widely.

**Outcome:** pending the owner's decision.

## PL-012 R-001 soft maximum; harvest_hash; seats in launch records (2026-10-12)
**What:**
- **R-001, soft maximum.** A `choose` gate with `"max_soft": true` lets the owner pick past `max`/`pick`.
  The decision page shows "N over the limit", and the Send button needs a second tap ("Confirm: send N,
  limit M"), with no browser dialog. The decision records `"over_max": true` and the `max`, and its `.md`
  says so. A gate without `max_soft` still refuses, even if a request claims `over_max`. Documented in
  `JOBS.md` §4. The Studio Architect's pitch, depth and friendslop gates already carry it.
- **`harvest_hash` (MA-009).** The Models page now treats a lead's note as harvested when a ledger line
  carries its `harvest_hash`, computed as `sha1(job folder name + "\x1f" + trimmed line)[:16]`. Rewording
  in the ledger no longer brings a note back.
- **`seats` in launch records (MA-010, PD-019).** `JOBS.md` §3b gains an optional
  `"seats": {"<seat>": {"runtime", "model", "version"}}`. When OpenRig reports no model for a seat (53 of
  54 today), the live graph's agent card shows the launch record's, marked as from the launch record.
  The operator duty is already in `SHARED-RULES.md` §7 (PD-019).

**Checked:**
- Smoke test 97/97. New checks: a soft max needs the confirm flag; a hard max refuses even with it; a
  confirmed overage is saved with `over_max` and `max`; a reworded harvested note isn't listed again; a
  seat's model comes from the launch record.
- Browser: picking 2 on a pick-1 soft gate shows the warning, the first tap asks to confirm, the second
  sends. No page errors.

**Restart needed:** yes (`gates.py`, `serve.py`, `models.py`).

**Outcome:** pending: first real use at the studio's next pitch or depth gate.

## PL-013 R-005 step 3, option A: plan, scripts and runbook (owner chose A, 2026-10-12)
**Decision (owner):** option A from PL-011. Harden the shared user, then run the console as its own
user. Option B (agents under their own user) stays the follow-up before the rig gets wider web access
or customer data.

**Built, not yet run on the PC:**
- `setup/install-console-user.sh` (run once, as yourself):
  - creates the system user `rigconsole`;
  - installs `/usr/local/lib/rig-console/rig-owner`, a root-owned helper allowing only `rig send` and
    `rig ps`, with one sudo rule letting `rigconsole` run it as you;
  - moves settings to `/etc/rig-console/env` (root:rigconsole 640) with a **new** token, and strips the
    old token and ntfy topic from `~/.config/rig-console.env`;
  - grants ACLs on `~/openrig/{jobs,research}` (rwX) and `{launches,briefs}` (rX), plus traverse on your
    home;
  - copies the event DB and state to `/var/lib/rig-console`;
  - rewrites the service to run as `rigconsole` from `/opt/rig-console` (`ProtectSystem=full`);
  - deploys.
- `setup/deploy-console.sh`: from now on, how code goes live. It runs the smoke test on the repo copy and
  only copies to the root-owned `/opt/rig-console` and restarts if it passes.
- `setup/harden-wsl.sh`:
  - refuses to continue unless you have a usable password;
  - sets `[interop] enabled=false` in `/etc/wsl.conf`, keeping your other settings;
  - lists any NOPASSWD sudo lines for you to remove with `visudo`. It doesn't edit them itself, so it
    can't lock you out.
- `setup/install-dashboard-service.sh`: no longer hard-codes a username. It refuses to run once
  `/etc/rig-console/env` exists, so it can't undo this.
- **Code:**
  - `RIG_BIN` may carry a prefix (`gates.rig_cmd`);
  - `/api/health` gains "Console isolation": amber while the console runs as the agents' user or from
    `/mnt/c`, green after.

**Runbook (between runs; after the Rig Architect confirms agents need neither `sudo` nor Windows
programs, and after the Model Architect's review):**
1. `sudo passwd $USER`: set a password you know. Check it: `sudo -k; sudo true`.
2. `bash setup/install-console-user.sh`. Note the new token it prints.
3. Sign in again on the desktop (the amber button) and the phone (`?token=` once).
4. `bash setup/harden-wsl.sh`, then remove your NOPASSWD line with `sudo visudo -f <file>`. Keep a
   second `sudo -s` terminal open until `sudo true` asks for your password.
5. In PowerShell: `wsl --shutdown`, then reopen Ubuntu. This stops every team; the operator relaunches
   them.
6. Check:
   - `/mnt/c/Windows/System32/wsl.exe -u root id` must fail;
   - `sudo -n true` must fail;
   - the console's health list shows "Console isolation" green;
   - a gate decision still reaches the lead (`rig send` via the helper).
7. From then on: `bash setup/deploy-console.sh` after code changes, not a plain restart.

**Recovery if locked out:** in PowerShell, `wsl -u root` opens a root shell from Windows. That's the
owner's path and stays available; agents lose it with interop off.

**What A protects, and doesn't:**
- **Closes:** instant root (interop, NOPASSWD); reading the console's token and ntfy topic; editing the
  console's code; forging the fingerprint or pin files (now in `/var/lib/rig-console`). So step 1's
  fingerprints become real detection.
- **Doesn't close:** agents are still your user. They can read your SSH and git keys and everything on
  `/mnt/c`, and can still delete or replace files in job folders they own. A forged decision is now
  reliably alerted, but a lead could act on it before you see the alert. That's option B, plus a
  proposed rule: leads confirm a decision with the console before acting (note to the Rig Architect).

**Checked:**
- Smoke test 99/99. New checks: the isolation health item; `RIG_BIN` prefix splitting.
- The scripts pass `bash -n`; shellcheck wasn't available here.
- The helper refuses anything but `send`/`ps`.
- The `wsl.conf` edit preserves existing sections.
- Not run end-to-end: it needs root on the PC. That's why the Model Architect reviews it first.

**Outcome:** pending: reviewed, run, then the step-6 checks recorded here.

---

## PL-014 MA-013 gaps closed; launch-record model on the Models page; handoff (2026-10-12)
**What:** the Model Architect's re-test (MA-013) found three gaps and one thing to confirm. All four are
fixed:
1. **The builds port served any file in a job folder,** not just builds (a planted `decisions/x.json`
   came back 200). Now `gates.build_file()` serves only files inside the job's builds folder (`job.json`
   `builds`, default `builds/`). Anything else gives 404.
2. **Any `*.ts.net` name was accepted.** When `RIG_CONSOLE_HOSTS` holds a `.ts.net` name, only that name
   is accepted. Without one, health shows an advisory "Hostname not pinned".
   `setup/install-console-user.sh` now asks for the Tailscale name if it's missing.
3. **`X-Forwarded-Host` wasn't checked** before the `/go/play/` redirect. It now gets the same name check;
   an unknown name falls back to the request's own host.
4. **No token meant changes without sign-in.** Now, with no `RIG_CONSOLE_TOKEN`, every change is refused
   with "Set RIG_CONSOLE_TOKEN…", and the token health item is required (red), not advisory.

**Models page (MA-013 answer):** in the Evidence panel, a ledger line whose `version_if_known` is
unknown now shows "Model … (from launch record)" for that job and seat, from `seats` in
`~/openrig/launches/<job>.json`. The seat grid is unchanged.

**MA's question, "is `~/openrig/launches/` mirrored?":** not yet. Proposal: R-011 (the logger rework,
next on my list after R-012) copies launch records to `snapshots/launches/` each pass. They hold no
secrets: job, rig, lead, folder and seat models.

**Acks:**
- MA-011's order (close interop and sudo, re-check, then step 3) is the PL-013 runbook order.
- Studio AD-025: pane captures stay at a stable path; `activity-log.csv` is free to move (R-011).

**Handoff (PD-020):** written to `architects/handoffs/platform-architect.md`. My suggested changes to the
architects brief and my role file are in the Rig Architect's notes below.

**Checked:**
- Smoke test 104/104. New checks:
  - a non-build file on the builds port gives 404;
  - an unpinned `*.ts.net` name gives 421;
  - a forged `X-Forwarded-Host` doesn't redirect off-site;
  - with no token (a second test server), changes are refused and health shows it red.
- The installer passes `bash -n`.

**Also:** `setup/deploy-console.sh` now lists which files differ from what's live and asks before
copying, since architect seats can edit `dashboard/` (see my note to the Rig Architect).

**Needs a dashboard restart** (`serve.py`, `gates.py`, `models.py`, `health.js`, `models.html`).

**Outcome:** pending: MA re-test of the four fixes.

---

## PL-015 The snapshot logger hang (R-011, owner report, 2026-10-12 19:38)
**What happened:** `rig-snapshots` stayed "active" while its loop sat for 10+ minutes in
`cp -ru ~/openrig/research/. research-mirror/`. Snapshots, the activity log and console alerts all went
stale, and nothing said so. The service held 2.6 GB (peak 3.6 GB).

**Cause (measured 2026-10-12 ~20:00):**
- **Between 19:31 and 19:41, assets-1 put about 40 GB of tools into `research/assets-1/tools/`:** FLUX and
  ACE-Step model weights (files up to 7.7 GB), two PyTorch/CUDA virtualenvs and a Blender tarball. The
  mirror copied all of it into OneDrive. 22 GB had arrived in `research-mirror/` when I checked.
- **The hang:** `cp` was in state D, in `p9_client_rpc`, writing into the OneDrive folder (`/mnt/c` is
  9p). Each write waits on Windows: OneDrive syncing and Defender scanning multi-GB files. A process in
  state D can't be killed, even by `timeout`. That's why the copy has to be off the main loop, not just
  timed out. After the owner's 19:49 restart, the new `cp` was stuck the same way within 9 minutes.
- **Not special files or permissions:** no pipes, sockets, devices or links in `research/`.
- **The memory:** reading 40 GB and writing 22 GB fills the page cache, and systemd counts that cache
  against the service. It's reclaimable cache, not a leak in the script (the loop itself uses ~18 MB).

**Fix (`setup/rig-snapshots.sh`, `setup/install-autostart.sh`, `serve.py`):**
1. **Every step has a timeout** (`rig` and `tmux` calls 20 s, the mirror 5 min). Each timeout is logged
   to the journal and to `snapshots/_logger.log` (last 500 lines).
2. **The mirror runs in the background,** at most one at a time (`flock`), every 60 s. A stuck copy blocks
   only later mirrors, which are logged as skipped, never the snapshots.
3. **`rsync` instead of `cp`, research outputs only.** It skips `tools/`, `models/`, `checkpoints/`,
   `build(s)/`, virtualenvs, `node_modules`, `.git`, archives, `*.wasm`, `*.pck`, model weights, shared
   libraries, and any file over 20 MB. On today's `research/`: 40 GB down to 40 MB, 711 files. It skips
   two 24 MB WAV samples in `assets-1/bakeoff`; the console reads those from `~/openrig` directly.
4. **Memory:** the unit gets `MemoryHigh=256M` (the kernel reclaims cache past it) and `MemoryMax=1G`
   (backstop). The installer now restarts the service so it picks up changes.
5. **The console alerts when snapshots are over 60 s old** (`RIG_SNAP_STALE_S`). It goes to the graph's
   alert list and, after the usual 25 s, to the phone as high priority. It reads `_status.txt`'s age,
   which the logger rewrites every round even when `rig` fails. Health already turned the "logger" item
   red at 60 s, but nothing pushed it.
6. **The hard-coded repo path is gone** (paths come from the script's location).

**Not done, and why:**
- **Moving the snapshots out of OneDrive.** Writes into `/mnt/c` can still stall the main loop, though
  small files rarely do. The Studio Architect relies on the pane-capture path (AD-025), and the Model
  Architect's harvest reads `research-mirror/`. That's the rest of R-011, with them.
- **The 22 GB already in `research-mirror/assets-1/tools/`.** Deleting it is the owner's call. rsync
  doesn't delete, so it stays until removed by hand.

**Proposed `.wslconfig`** (the owner's Windows file, `%UserProfile%\.wslconfig`; needs `wsl --shutdown`):
```
[wsl2]
memory=12GB
swap=8GB
[experimental]
autoMemoryReclaim=gradual
```
Ubuntu has 15 GB today (half the PC) and 3 of its 4 GB swap in use. `gradual` hands cached memory back
to Windows instead of holding it after a big copy. The cap leaves Windows more headroom for OneDrive and
Defender. Lower `memory` only if agent seats stay comfortable: watch the console's disk/health for a day.

**Checked:**
- Smoke test 106/106. New checks: fresh snapshots raise no alarm; snapshots 5 min old raise an alert that
  says how old.
- The script passes `bash -n`. A 40 s run against scratch folders wrote every snapshot each round, with
  no timeouts. That run found a bug, now fixed: the first mirror waited 60 s instead of running at once.
- `rsync --dry-run` with the new filter: 711 files, 40 MB.

**To go live (owner):**
1. Stop the copy that is running now and remove the copied tools:
   `sudo systemctl stop rig-snapshots`, then delete `research-mirror/assets-1/tools/`.
2. Review the two `setup/` scripts, then `bash setup/install-autostart.sh` (writes the unit, restarts).
3. Restart the console for the stale alert: `sudo systemctl restart rig-dashboard`.

**Note:** the service runs the script straight from the repo, so any restart picks up the new version.
That includes the automatic restart after a crash. Review it before the next restart.

**Outcome:** pending: a day of `_logger.log` with no stuck rounds, and no stale alert in normal running.

---

## PL-016 Console messaging: misread prompts, the owner's name, replies (kickoff item 2, 2026-10-13)
**What happened:** at 20:02 "Message it" to `arch-platform` was refused with "at an interactive prompt
(selection_prompt)", though the screen showed an idle input box. OpenRig misreads idle Claude seats.
Messages also arrived as `From: <unknown sender>`, and the owner couldn't see replies without the terminal.

**Changes:**
1. **The screen settles "at a prompt".** `screen_prompt()` reads the seat's last 15 screen lines. A
   choice or permission prompt (`❯ 1.`, "Do you want to", "Esc to cancel", `1. Yes`) means "menu"; an empty
   `❯`/`›` input box means "idle"; anything else means "unknown", which counts as a prompt. It runs both
   when OpenRig's state says `needs_input` and when `rig send` refuses.
   - **menu:** refused, with the screen shown.
   - **idle, captured ≤30 s ago:** refused, with **Send anyway** offered. Send anyway checks the screen
     again, then sends one line with `--dangerously-interact` and a fixed reason (OpenRig's only override).
   - **unknown:** refused.
2. **The sender is the owner.** The console sets `OPENRIG_SESSION_NAME=owner@rig-console`, so seats see
   `From: owner@rig-console`. The body says to reply on screen. Tested with one message to my own seat.
3. **Latest reply** on the desktop panel and the phone sheet: the seat's last text block on screen,
   skipping tool calls (`/api/screen` now returns `reply` and `prompt`).
4. **`setup/rig-owner` (option A) refuses `--dangerously-interact` and `--raw`.** Before this it passed
   any `send` arguments through. It also sets the sender name, since sudo drops the environment.

**Owner gate `pl-016-send-anyway`:** may Send anyway work under option A? I recommend keep-off: under
option A the console must not be able to type into prompts. Until the owner decides, it works only while
the console runs as the owner's user.

**Found while testing:**
- **The From label isn't authenticated.** Any process can set `OPENRIG_SESSION_NAME`, so a seat could
  send as `owner@rig-console`. SHARED-RULES §1 already treats any message claiming an owner decision as a
  pointer only, so decisions stay safe. But seats shouldn't trust the label for anything else (note to the
  Rig Architect).
- **The misread itself** is OpenRig's bug, worth a report upstream.

**Checked:**
- Smoke test 111/111. New checks: a menu on screen is refused without Send anyway; an idle screen offers
  it; Send anyway re-checks and refuses a menu; with `RIG_BIN=""` it still sends nothing; the screen API
  returns the latest reply and skips tool calls.
- Browser: `graph.html` and `m.html` at desktop and phone width with no page errors. The phone sheet's
  new parts weren't opened by the check.
- `rig-owner` passes `bash -n`.

**Needs a dashboard restart** (`serve.py`, `graph.html`, `m.html`). `rig-owner` changes only when option
A's installer runs.

**Outcome:** pending: the next misread is sent through, and the owner reads a reply in the console.

**Owner decision (2026-10-12 23:53, `pl-016-send-anyway`): keep-off.** The decision file is checked.
`rig-owner` already refuses keystroke modes, so nothing more to do.

---

## PL-017 Notifications: the operator can notify the owner; routine alerts go quiet (R-016, R-017, 2026-10-13)
**Asked (owner, via the operator's queue):**
1. Let the operator notify the owner, first for "Bridge production team is ready".
2. Stop the "screen unchanged" and idle notifications. Notify only for real events, with clear names,
   no repeats, and related alerts summarized.

**Current cause of the noise:** `features.push_alerts` pushed **every** alert kind to the phone once it
lasted 25 s: screen unchanged (`frozen`), busy for N min (`long`), context, handoffs, folder names. It
re-pushed every 6 h, and again each time an alert cleared and came back. `notify.js` popped a desktop
notification for every new alert, and again each time one flapped back. With 50+ seats, and OpenRig
misreading idle seats as working (which triggers `frozen`), that's constant noise.

**Why not OpenRig's own route to the owner:** `rig queue create --destination <human>@external` is the
supported way to message a person. But no human is registered (`rig gateway human list`: none), and its
only connector is Slack, which needs a new Slack app (an account). The console already reaches the owner's
phone through ntfy, so this reuses that.

**1. The operator's outbox** (`dashboard/outbox.py`, `JOBS.md` §3c):
- **How it's sent:** the operator writes `~/openrig/launches/notify/<id>.json`
  (`{"title", "body", "priority", "url"}`). Only the operator writes under `launches/` (SHARED-RULES §1),
  the same trust the console gives launch records. No seat gets a new power: team seats are still barred.
- **What the console does,** within one round (10 s):
  - shows the note under Needs you;
  - pushes it once through `F.push_now`;
  - records the result in `state/notify-sent.json`;
  - sends the operator one receipt with `rig send` as `console@rig-console`: "pushed (ntfy accepted
    it; not proof it was read)" or "not pushed: <why>".
- **Never twice:** each id is handled once, ever.
- **Limits:** five pushes an hour. A note expires 24 h after it's written, or when dismissed. Links to
  other sites are dropped. Files must be under 8 KB, and links (symlinks) are ignored.
- **Not leaked:** the ntfy topic never appears in a receipt.
- **Under option A:** `rig-owner` gets a `receipt` verb that sends with the console's label.

**2. Which alerts notify** (`serve.NOTIFY`; phone and desktop now follow the same list):

| Alert | Notifies as | When |
|---|---|---|
| A gate | Decision needed | at once |
| An operator note | From the operator | at once (pushed by the outbox) |
| Usage limit hit | Stopped: usage limit | at once |
| Snapshots stale | Console can't see the agents | 60 s stale |
| A decision written outside the console | Check a decision | at once |
| A job claims another team | Team routing changed | at once |
| A seat waiting for approval | Waiting for approval | after 10 min |
| A console check failing | Console problem | at once |
| Screen unchanged, busy for long, context, handoffs, folder names | **never**: shown in the console only | |

- **Dedup:** an alert notifies once while it lasts. If it clears and comes back within 6 h, it doesn't
  notify again.
- **Batching:** several due in the same round go as one push ("3 things need you", with a list). The
  desktop does the same.
- **Unchanged:** every alert still shows in the console, the tab count and the phone page. Dismissing
  still works.

**Checked:**
- Smoke test 121/121. New checks: notify marks (gate and operator notify; context and a fresh approval
  stay quiet); the outbox shows the note and drops the off-site link; a note is handled once, not pushed
  without `NTFY_TOPIC`, and the result says so; no receipt with `RIG_BIN=""`; a bad file is recorded;
  push rules in-process (only marked alerts push, no repeat while present or after a quick flap, several
  go as one).
- Browser: `graph.html`, `research.html` and `m.html` at both widths. The one failure is old and not
  from this change: `research.html` asks for a `decision.json` the fixture doesn't have (the checkpoint
  picker, due for removal, PL-005).
- **Not tested live:** a real ntfy push and a real receipt. That needs the deployed console, and no live
  test is authorized. The first real note (Bridge ready) will be the live test, and its receipt says
  whether it pushed.

**Needs a dashboard restart** (`serve.py`, `features.py`, `outbox.py`, `notify.js`). No new setup. The
console needs the existing `NTFY_TOPIC` and `NTFY_CLICK`.

**Outcome (part):** the first live note worked on 2026-10-13 at 07:47Z. The operator wrote
`notify/bridge-ready-2026-10-13.json`, and the console's receipt said ntfy accepted the push and the note
was shown under Needs you. No duplicate and no resend. Still pending: a day of the owner's phone staying
quiet except for real events.

---

## PL-018 "Needs you" in sections, and task cards (R-018, owner delegated to the architects, 2026-10-13)
**Why:** "Needs you" listed every alert, so diagnostics buried the few things the owner had to act on.
Hands-on jobs only the owner can do lived in architect logs. The owner delegated the design to the
architects (`~/openrig/jobs/architects/ops/owner-ui-delegation-20261013.md`). The Rig Architect proposed
R-018, and I built it with two changes (see R-018).

**What:**
- **Each alert carries `act`, `label` and `section`** (`serve.SECTION`, from the `NOTIFY` list).
  - **Decide:** gates, decisions written outside the console, research checkpoints.
  - **Do:** task cards, plus blockers only the owner can clear (approval waits, usage limits, stale
    snapshots, console problems).
  - **From the operator:** outbox notes.
  - **Other signals** (collapsed): screen unchanged, busy for long, context, handoffs. Nothing to do.
- **Counts:** the "need you" chips, the tab title and the phone badge count only Decide, Do and operator
  notes.
- **Task cards** (`gates.list_tasks`/`answer_task`, `POST /api/task`, `JOBS.md` §4b):
  - architects post `jobs/architects/tasks/<id>.json`;
  - the owner taps Done or Won't do, with an optional note;
  - the console writes `decisions/task-<id>.json`, records its fingerprint like a gate's, and tells the
    asker;
  - only urgent cards push.
  - Same sign-in cookie and CSRF header as every change.
- **Operator notes** drop the "From the operator:" prefix; the section heading says it.

**Checked:**
- Smoke test 128/128. New checks: sections; task card fields and urgent-only notify; Done saved with its
  note; an answered card leaves Needs you; the console's own answer raises no outside-decision alarm;
  an answer can't be given twice; only Done or Won't do.
- Browser at both widths, with a sample card and note seeded. Looked at the phone screenshot: the
  sections read clearly.

**Restart:** batched with PL-014 to PL-017 in owner gate `restart-console-1`. It has the exact commands
and the PL-015 logger steps.

**Outcome:** pending: the owner answers a real Do card from the phone.

---

## PL-019 The Architects Lounge panel (R-019, owner delegated to Rig and Platform, 2026-10-13)
**What:** the Rig Architect owns the posting conventions (`jobs/architects/lounge/README.md`); I built
the read-only view.
- **`lounge.py`** reads `lounge/<UTC>-<seat>.md`. Optional `reply_to:` and `image:` headers come before
  a blank line, then the text. Replies thread under the first post of their thread, and loops are ignored.
  At most 200 posts, 8 KB each, and links (symlinks) are skipped.
- **`GET /api/lounge`** serves the posts, and **`lounge.html`** shows them (More → Lounge, and the phone
  footer).
- **Untrusted text:** posts are shown with `textContent`, never as HTML. An image shows only if it's
  inside a job or research folder, through the existing sandboxed `/job/` and `/data/` routes.
- **Never notifies:** no alert, no Needs you entry, no push, and the page doesn't load `notify.js`.
- **Skipped:** an unread count (optional in R-019) and owner posting.

**Checked:** smoke 132/132 (threading; a `/etc` image path dropped; raw `<script>` text kept as data for
`textContent`; no alerts; the page uses `textContent`). Browser at both widths with seeded posts; looked
at the phone screenshot.

**Restart:** added to `restart-console-1` (its context file now lists the Lounge).

**Outcome:** pending: the owner reads the Lounge and says whether to keep it.

---

## PL-020 Production milestones contract; Play on a whole gate (R-015, Studio AD-027, 2026-10-13)
**What:**
- **Adopted the Studio Architect's `milestones.json` as-is** (`JOBS.md` §6). The tech lead and
  `build.py` write it from the first milestone. The console view comes later (R-015).
- **Studio's two small asks, both done:**
  - a top-level `play` on any gate, shown as "▶ Play this build" on the decision page, for milestone
    approve gates (`gates._load_gate`, `decide.html`);
  - `production` listed as a job type (`type` was already a free label).
- **Studio's older note, "jobs-mirror stopped at 19:18 and has no images":** nothing in the repo or the
  system services writes `jobs-mirror/`, and the snapshot logger never did, so it isn't R-011. It was
  probably a copy run by hand that ended. As a seat, the Studio Architect can read `~/openrig/jobs/`
  directly (architects brief §1), images included, so no mirror is needed. If a Windows-side copy is still
  wanted, that's an R-011 item.

**Checked:** smoke 133/133 (new: an approve gate's `play` resolves to the builds port). Browser:
`decide.html` at both widths.

**Restart:** rides `restart-console-1`.

---

## PL-021 Restart verified; decisions go to the gate's own lead; .gitignore (2026-10-13)
**Restart (`restart-console-1`):** the owner restarted the console. Verified read-only:
`rig-dashboard` started at 00:32:04 PDT (systemctl), the journal shows a clean restart and no errors,
and `serve.py`, `outbox.py`, `features.py` and `lounge.py` all predate the start. So PL-015 to PL-020
are live, and so is the operator outbox. I sent the receipt to the operator
(qitem-20261013074630-fb76c6c2). A real push isn't proven yet: the Bridge-ready note is the first test.
- **Miss:** I was still editing `gates.py` during the restart; its last write was at 00:32:18, 14 s
  after the start. The running copy has the gate Play button, but not certainly the routing fix below.
  It needs the next restart. Lesson: freeze server files once a restart gate is open, and put new work
  in the next batch.

**Decisions go to the gate's own lead (Rig Architect's note):** `decide()` replaced every gate's `lead`
with the launch record's lead, so every architects-job decision went to `arch-rig`, who relayed them by
hand. Now `gates.tell_whom`: the gate's `lead` if that seat is in the job's rig (strict match), else the
launch record's lead, else a `*lead` seat.
- **Still safe:** the rig itself still comes only from the launch record or pin (PL-010/PL-012), so a
  gate can't route a decision to another team. Only which seat *within* the team hears it changes.
- **Smoke checks** (in-process, fake `rig ps`): own lead in the team wins; a lead outside the team is
  ignored; no lead means the record's lead.

**`.gitignore` (Rig PD-024):** also ignores `/.claude/` and `.codex/`. I'd already added
`architects/.claude/settings.json` and `architects/.claude/plugins/` earlier this session. `git status`
shows none of them.

**Checked:** smoke 136/136.

**Needs a restart** for the routing fix (`gates.py`). It's small, so it waits for the next batch unless a
misrouted decision causes trouble.

---

## PL-022 Approval waits go to the operator; "Needs you" gets a route (R-020, owner via Rig, 2026-10-13)
**Why:** the owner kept spotting seats stuck at approval prompts and relaying them by hand. OpenRig's own
escalation fires late, only when queued work is stuck, and to the sender, who can't act. The owner also
couldn't find "Needs you".

**What:**
- **`escalate.track`** runs each watcher round and follows each seat's continuous wait at a prompt (an
  "episode"). After 45 s it sends one `rig queue create` to `operator-agent@kernel`:
  - `--source console@rig-console`; the body goes in on stdin;
  - `--id` is `qitem-<UTC start>-<sha1(seat, start, prompt)[:16]>`;
  - the body has the seat, the team and the last 15 screen lines, marked untrusted.
  - **Episodes persist** in `state/approval-episodes.json`, so a restart can't send twice.
  - **Skipped:** kernel seats, usage-limited seats, and screens that show an idle input box (added to
    R-020: OpenRig misreads idle seats, PL-016).
- **`rig-owner` (option A)** gets an `approval-item <id> <summary>` verb that fixes the destination to the
  operator, so the console can't create queue items for anyone else.
- **"Needs you":**
  - a top-bar link with a live count, from the new `GET /api/needs`, which reads the watcher's last
    round, so it's cheap;
  - the home page's side panel now has a "Needs you" heading;
  - `/?needs=1` scrolls to the panel and flashes it.
  The phone page already opened on Needs you.
- **The browser check** now ignores the research pages' optional-file 404s, which aren't errors.

**Risk to watch:** I haven't run a real `rig queue create --id` with this id format; there's no dry run,
and a real run would put a test item in the operator's queue. If the daemon refuses the format, each
attempt logs "approval item failed" in the journal and retries next round. The owner's 10-minute alert
still catches the wait. The Rig Architect's end-to-end check proves it.

**Checked:** smoke 143/143. New: under 45 s sends nothing; after 45 s exactly one item, and none for the
kernel or a misread idle screen; the untrusted marking; no resend on a prompt change; a new wait gets a
new id; ids are deterministic; the nav count; four top-bar links. Browser: all 9 pages at both widths
pass; I looked at the desktop screenshot.

**Restart:** gate `restart-console-2` (this plus PL-021's routing fix).

**Outcome:** worked live. After the 01:06:58 restart the operator received 4 items in 4 different waits
(tech-lead, me twice, art-review), 46 to 55 s after each wait began. The screen text was marked untrusted,
there were no duplicates, and all were closed within 40 s (Rig Architect, 08:10Z). The id format works.
- **Its one fix,** made in PL-023: Claude's "Tip: auto mode…" hint line crowded the real command out of
  the excerpt. Hints and divider rules are now dropped.
- **Miss:** the `/?needs=1` link and the panel heading weren't what the owner meant by "Needs you" (see
  PL-023). I built the route from the request's wording without asking what the page was for.

---

## PL-023 "Needs you" as its own page: to-dos and questions (R-018 owner correction, 2026-10-13)
**Why:** the owner said "Needs you" opening the graph isn't it. They want a standalone inbox: small jobs
("To do") and questions only they can answer, each saying what, why, what's waiting and what we suggest,
with a clear Open or Resolved status and their answer kept. Gates, approval waits, alerts and notes stay on
their own routes. This replaces PL-018's "tasks and blockers in the Do section" and PL-022's
`/?needs=1` link.

**What:**
- **`needs.html`:** To do, then Questions, then a collapsed "Done recently" (14 days) list.
  - Each card shows Open/Resolved, the title, the action, "Why you", "Waiting on it", "We suggest",
    who asked and when, and a details link.
  - Answers are typed on the page. To-dos get Done / Won't do with an optional note; questions get Send
    answer or Skip.
  - Card text is escaped; a refresh never redraws while the owner is typing.
- **Cards (`gates.py`):** `kind` (`do`/`ask`), `why` and `recommend` are added; two open cards with the
  same title are flagged. An answer must match the card's kind, and Send needs some text.
  - The decision record keeps the whole card plus `answer`, so `resolved_tasks()` can show it after the
    task file is gone.
  - New `GET /api/tasks` returns open, unreadable and resolved cards.
- **Off the alert panels:** task cards are now section `"inbox"`. The graph and phone panels skip them;
  they remain as alerts only so an urgent card still pushes once.
  - The graph's chip and the phone's pill now say "N alerts", so they aren't confused with the Needs you
    count.
  - The phone's list is headed "Alerts", under a "Needs you · N open" button that opens the page.
  - Reverted: the side-panel heading and the `/?needs=1` flash.
- **Nav:** "Needs you" goes to `/needs.html`, and its count is open cards only (`/api/needs`).
- **R-020 fix:** approval items drop "Tip:" and divider lines from the screen excerpt.
- **R-020 miss, found live at 08:14Z:** art-review's second prompt (`git show 97ab76a`) produced no item.
  - **Cause:** OpenRig reported `needs_input` without a break from 01:08:12 to 01:15 local, although the
    first prompt was approved at 08:09Z. So the console saw one wait, and my "a changed prompt in the same
    wait doesn't send again" rule held the second prompt back.
  - **Fix:** once a wait's item is sent, a different prompt starts a new wait, with its own 45 s and its
    own item. Before the item is sent, a changed line is still the same wait, which absorbs flicker.
  - **Freeze:** I made this after gate `restart-console-3` opened. That bends my freeze rule, but it's two
    small writes to one file, and each intermediate state was valid Python, so a restart could never load
    a broken file.

**Checked:** smoke 150/150. New:
- the page is served, escapes card text and has no gate links;
- cards carry their kind, why and suggestion, and duplicates are flagged;
- the nav count equals open cards;
- a question needs text or Skip and can't be marked Done;
- answered cards show as resolved with the answer and the card;
- the hint line is dropped from approval items.

Browser: all 10 pages at both widths pass; I looked at the phone screenshots of `needs.html` and `m.html`.

**Restart:** gate `restart-console-3`, done. Verified: started at 01:15:51 PDT, clean journal, and every
server file predates the start (the art-review fix was saved at 01:15:35). Receipt sent to the operator;
the Rig Architect is posting the real cards (qitem-20261013081749-dacfdd4a).

**After the restart (source only, rides the next restart):** the operator noticed an item whose summary
named the earlier prompt (`systemctl`) while its body showed the current one (`journalctl`). The summary
came from the start of the wait; now both use the prompt at send time. Smoke 152/152.

**Outcome:** pending: the owner answers a real card on the page.

---

## PL-024 Your messages kept with their replies (owner via the operator, 2026-10-13)
**Why:** the owner's questions to seats (mostly the operator) and the replies scroll out of the terminal
quickly. They want each question kept with its reply and both times, easy to revisit on phone and desktop.
It's history only: no gate, no notification, no extra agent turns.

**What (`convo.py`, `messages.html`):**
- **Record:** every console message is recorded when it's sent (normal or Send anyway), in
  `state/conversations.json` (the last 500).
- **Capture:** the watcher's existing 10 s round, with no new polling, reads the reply off the screen it
  already captures, once the seat is idle at its input box.
  - The reply is the text after the last "Message from the owner" line, up to the seat's "Worked for…"
    footer or its empty input box. It starts at the first ●/⏺/• if there is one, which skips the rest of
    a wrapped question on Claude seats.
  - If a newer question comes first, or 4 h pass, the entry says "No reply captured" instead of
    guessing.
- **`GET /api/messages[?seat=]`** and **`messages.html`:** newest first; each card shows you → seat, your
  question and its time, then the reply and its time. There's a filter chip per seat. Replies are
  escaped and shown in monospace, so the operator's tables stay aligned.
- **Links:** "Your messages with it, and its replies →" in each agent panel (desktop and phone);
  Messages under More and in the phone footer.

**Limits:**
- Replies come from the screen. If a seat answers at great length and the question scrolls past the
  ~300-line capture, nothing is captured, and the entry says so.
- A reply that contains "Do you want to" or "1. Yes" looks like a prompt, so it isn't captured.
- Only messages sent from the console are kept, not ones typed in a terminal.

**Checked:**
- Smoke 159/159. New: the Codex and Claude reply shapes, built from a synthetic copy of the operator's
  real screen, since real captures are run output and can't go in the public repo; nothing when the
  question has scrolled off; nothing while working; the reply kept once idle; with two questions, the
  newest gets the reply and the older says none was captured; the API and page are served and escaped.
- Browser: `messages.html`, `graph.html` and `m.html` at both widths; looked at the phone screenshot.

**Restart:** gate `restart-console-4`, done and verified: started 01:47:39 PDT, and every server file
predates it (`convo.py` 01:44:55, `serve.py` 01:45:09). So PL-024 and PL-023's summary fix are live.

**Routing miss on this gate's decision (PL-021 follow-up):**
- **What happened:** the decision was sent to `arch-rig`, not to me, although the gate names
  `arch-platform` and PL-021's routing has been live since 01:15:51. It routed restart-console-2 and -3
  correctly.
- **Likely cause:** you decided 7 s after the restart, while the console was busy starting up.
  `tell_whom` ran `rig ps` twice. I believe the first call (the strict check for the gate's own lead)
  failed and returned nothing, and the fallback's second call then succeeded and picked the launch
  record's lead. Nothing was logged, so this is inference.
- **Fix (source, next restart):** one `rig ps` per choice, retried once if it fails. If both fail, the
  console tells the gate's named lead (else the record's), unchecked but inside the job's own rig. My
  first version told nobody; the Rig Architect pointed out (08:50Z) that this turns a misroute into a
  silent miss. The unchecked address is still safe: the rig comes only from the launch record, so it
  can't reach another team, and a seat that doesn't exist just fails the send. Each routing choice is
  logged ("gate lead X, record lead Y -> Z"), so the next one can be diagnosed from the journal.
- **Checked:** smoke 162/162 (one `rig ps` per choice; after two failures, the named lead, else the
  record's lead).
- **Not urgent:** until the next restart, the Rig Architect forwards any misrouted decision.

**Outcome:** pending: the owner reopens a question and finds the operator's reply next to it.
**Superseded in part by PL-025:** the operator's full-status reply never appeared, so screen pairing isn't
trusted any more.

---

## PL-025 Replies matched by message id (owner via the operator, qitem-20261013085936, 2026-10-13)
**Why:** the operator's correct full-status reply wasn't kept on the Messages page. Reading replies off the
screen can't be made reliable (long replies scroll, wrapped text, two questions). The owner asked for
explicit replies tied to the question.

**What (`convo.py`, `serve.py`, `gates.py`, `messages.html`, `JOBS.md` §3e):**
- **Every console message gets an id** (`m-<local time>-<4 hex>`), delivered as
  `Message from the owner [msg <id>]`. The text ends with the exact file to write.
- **The reply is a file:** the operator writes `~/openrig/launches/replies/<id>.json`
  (`{"id", "text", "at"}`); architects write `replies/` in their own job folder, found from the
  operator's launch record for rig `architects`. Team seats get the id but answer on screen.
- **Pairing is by exact id only:** the file name, the `id` inside, and a question the console issued to a
  seat allowed to answer from that folder must agree. Anything else is ignored and logged once.
  `<id>-2.json`… are follow-ups shown under the first.
- **Screen text** stays as a fallback, shown apart with a dashed border, labelled "From the screen (not a
  confirmed reply)", and hidden once a file reply exists. Old entries are relabelled as screen text.
- No push, no wake, no seat HTTP. Rig's process constraints
  (`scratch/rig/question-reply-process.md`) are all met.

**Checked:** smoke 172/172. New: id format; who answers from which folder; a file pairs with exactly its
question and keeps its time; follow-ups add, never replace; never paired: a made-up id, a mismatched id
inside, the wrong seat's folder, a bad name, broken JSON; an architect's own-folder reply; a confirmed reply
isn't downgraded by later screen text; the delivered text carries the id and the exact path, on one line.
Browser: `messages.html`, `graph.html`, `m.html` at both widths pass (the first run failed only because the
fixture server was slow to start after the WSL restart; the retry passed).

**The WSL shutdown restarted the console (02:06:46 PDT boot, owner-authorized recovery).** It loaded the
source on disk at that time: PL-024's routing hardening and PL-023's summary fix are now live, and so is a
half-finished `convo.py` from before the shutdown. Static pages are served from disk, so my new
`messages.html` went live straight away while the running server still sends the old `{reply, reply_at}`
shape. **Miss, caught before anyone reported it:** the page briefly showed questions without their replies.
Fix: the page reads both shapes, showing old replies as screen text (which is what they were).
Lesson: page files are live the moment they're saved; keep pages compatible with the running server.

**Restart:** gate `restart-console-5`, decided done 10:57:04 PDT. Verified: started 10:55:25 PDT, after every
server file (latest `serve.py` 10:45:40, which includes PL-026); clean journal; the decision routed to me.

**End-to-end test after the restart (bounded):** the owner sends the operator one message from the
console; the operator writes the reply file named in it; the Messages page shows it beside that question
with both times. Then the operator writes one file with a made-up id, which must not appear.
Rig confirms. Until Rig's SHARED-RULES §7 duty is approved, the operator follows the instruction in the
message itself.

**Outcome:** pending: the end-to-end test.

---

## PL-026 R-020 false positive: Codex's slow-model notice isn't an approval (operator, qitem-20261013174517, 2026-10-13)
**What happened:** dev-a@bridge-prod showed Codex's "Giving this request a little extra thought" menu
(Retry with a faster model / Dismiss and keep waiting / Learn more; "No action is required; Codex will keep
waiting"). OpenRig reported `needs_input`, so the console sent the operator an approval item
(qitem-20261013174407-d60e8c540a508597). Nothing needed approving.

**Fix (`serve.py` `graph()`):** if OpenRig says `needs_input` and the last 25 screen lines show that notice,
the seat counts as working. Its action reads "Model is slow to answer; it keeps waiting (nothing to
approve)". So there's no approval alert, no 10-minute notification and no operator item. Sending a message to
it is still refused (the menu could take the keys); that's unchanged.

**Checked:** smoke 173/173: a fixture seat with the notice is working, with no approval alert; the real
approval fixture still alerts.

**Restart:** rides gate `restart-console-5` (added to its page before any decision). This bends my freeze
rule, but the gate is still undecided, so whatever restart comes next loads both together.

---

## PL-027 Option A ready for the owner: the Model Architect's review fixed, two Needs you cards (owner go-ahead, qitem-20261013180300, 2026-10-13)
**Why now:** the owner approved my priority list (`scratch/platform/restart-5-and-ideas.md`): option A
first, then the activity log, then job pages. Option A's two preconditions were met: SHARED-RULES §1 now
forbids seats `sudo` and Windows programs, and the Model Architect reviewed the scripts
(`models/reviews/PL-013-option-A.md`, MA-014). But I'd never fixed that review's findings. Done now:

- **Finding 1 (high), deploy a reviewed commit:** `deploy-console.sh` refuses if `dashboard/` has uncommitted
  changes. It shows the commits and files changed since the last deploy and asks. It exports the commit
  with `git archive`, runs the smoke test on that exact copy, deploys it and records the hash in
  `/var/lib/rig-console/deployed`. Health's "Console isolation" line shows the deployed commit. The
  remaining risk is as the review says: the boundary is the owner reading the diff, or the commit
  history, since architect seats can commit.
- **Finding 2 (high), the token on screen:** the installer refuses to run inside tmux. It never prints the
  token; it writes it to `/root/rig-console-token` (root, 600) for the owner to read once with
  `sudo cat`.
- **Finding 4, prove the boundary:** the five extra checks (code, settings, console user, state, plus
  interop and sudo) are steps in the owner's card. I left out the `/proc/<pid>/environ` check: it needs
  `$(…)` inside a path and adds little once the settings file itself is unreadable.
- **Finding 6, the helper:** `rig-owner` now allows exactly `send|receipt <seat> <text>`,
  `approval-item <qitem id> <summary>` and `ps` (always `--nodes -A --json`). It refuses extra arguments,
  text starting with "-", and anything else. Smoke-tested against a fake `rig`.
- **Point 7:** the installer's `rig ps` self-test now also says that a failure may mean sudo isn't setting
  HOME. Re-signing on every device is a card step.
- **Not done, on purpose:**
  - **Finding 3 (launch records writable by seats):** added to "doesn't close". It's option B territory,
    or a later pin-and-alert like PL-010.
  - **Finding 5 (`ProtectHome=read-only`):** the helper's `rig` runs inside the console's mount
    namespace, and I can't test which home paths `rig` writes without root. A read-only home could break
    every decision message. Revisit after option A is live, with the owner, one setting at a time.

**Owner steps:** two Needs you cards in the architects job:
- `console-own-user`: commit, password, installer, token, sign in again;
- `close-wsl-root`: harden, remove NOPASSWD, `wsl --shutdown`, the checks.

Each step has the exact command, where to run it and its success check. The runbook is in
`ops/console-user-runbook.md`. Part A only restarts the console. Part B stops every team, so the owner
tells the operator first.

**Checked:**
- Smoke 181/181. New: the helper's four calls and its refusals.
- `bash -n` on all three scripts.
- Not run end-to-end: it needs root on the PC. The card's checks are the end-to-end test.

**Outcome:** pending: the owner runs the cards; I record the check results here.

---

## PL-028 Needs you cards get exact steps (owner convention via Rig, qitem-20261013180423 and -180714, 2026-10-13)
**Why:** the owner wants command cards to give the exact commands one at a time, where to run each, and
what success looks like. Rig also found a card's `recommend` cut silently at 400 characters, losing
commands.

**What:**
- **`steps`** on a card: `[{"where", "run" or "say", "check"}]`, up to 20.
  - The page shows a numbered list; each command is in monospace with a Copy button (it selects the text
    if the clipboard is blocked), and its check is in green.
  - A step with neither `run` nor `say` is dropped. A command over 1000 characters is never shown cut,
    because a shortened command could still run and do something else: the step says "too long; see
    Details" instead.
  - Steps are kept in the answer record and its `.md`.
- **Limits raised and made visible:** action 600, why 400, blocks 300, recommend 1000. Cut text ends in
  "…". All limits are stated in `JOBS.md` §4b, with the owner's git rule: review first, no blanket
  staging.
- `needs.html` is served from disk, so it's live now. It shows steps only once the server sends them,
  after the next deploy.

**Checked:**
- Smoke 181/181: steps kept, malformed dropped, a too-long command never cut, cut text visibly marked, and
  the page escapes steps and has Copy buttons.
- Browser: `needs.html` at both widths with a steps card; I looked at the phone screenshot.

---

## PL-029 The owner posts in the Lounge (R-021, owner-approved via Rig, qitem-20261013181450, 2026-10-13)
**What:**
- **`lounge.html`:** a text box at the top ("Post"), and "Reply" on each post. Nothing is notified or
  counted.
- **`POST /api/lounge`:** the same checks as decisions: token set, sign-in cookie, the `X-Rig-Console`
  header and JSON.
- **`lounge.post()` decides where the post goes:**
  - it names the file `<UTC>-owner.md`, stepping a second on if that name is taken;
  - it always writes the `reply_to:` header line, so text starting with `image:` stays text;
  - 2000 characters at most, and empty posts are refused;
  - `reply_to` must be an existing plain post file, else the post goes at the top.
- **Seats can't pose as the owner:** seats can write in that folder, so the console records a sha256 of
  each post it writes in `state/lounge-owner.json`. Only matching files show as "You". Others named
  `-owner.md`, or owner posts edited afterwards, show as "Someone posing as you (not from the console)".
- **Codex review** (`scratch/platform/r021-review.md`):
  - **Finding 1 (medium), fixed:** a linked lounge folder, or a link anywhere on its path, could redirect a
    post. Now every folder from `/` down is opened with `O_NOFOLLOW`, and the post is created relative to
    that handle with `O_EXCL|O_NOFOLLOW`. Reading uses the same handle, so a linked folder shows nothing,
    and linked post files are skipped.
  - **Finding 2, the provenance ledger:** `install-console-user.sh` doesn't carry `lounge-owner.json`
    over (PL-030).
  - **Finding 3, wording:** right. The check is "holds the console token", not "is the owner's browser".
    The token's secrecy is what option A protects.

**Checked:** smoke 192/192. New: sign-in required; server-chosen names, even two in one second; replies
nest; `image:` stays text; empty and too-long posts refused; forged and edited owner posts not shown as the
owner's; quiet; a linked folder refused and shows nothing; a linked `reply_to` dropped. Browser:
`lounge.html` at both widths. The page is live from disk now; posting works after the next deploy (until
then it says so).

---

## PL-030 Option A, second round: the Model Architect's re-check and Codex's cross-check (MA-016, 2026-10-13)
I pulled both owner cards (to `ops/draft-card-*.json`) until these were fixed.
- **Finding 1 (high), deploys after hardening were a root path:**
  - The deploy script is installed root-owned as `/usr/local/sbin/rig-console-deploy` from the reviewed
    commit; deploys update it and `rig-owner` from the commit being deployed.
  - It never runs git with the agents' repo config: every call passes `core.fsmonitor=false`, a null
    hooks path and no pager. The diff, log and archive come from a fresh `--no-local` clone.
  - **Codex's stronger boundary, taken:** the commit is unpacked into root-owned, read-only staging under
    `/var/tmp`, and the smoke test runs there as `nobody` with a bare environment. So committed test code
    can't use the owner's sudo, touch the owner's files or change what gets installed.
  - Checked by running the smoke test from a read-only copy with `env -i` (192/192). Root wasn't
    available to test `nobody` itself.
  - If the last deployed commit is gone (history rewritten), it says so and asks for a full read.
- **Finding 2 (high), unreviewed setup scripts:** the installer and the deploy refuse if `dashboard/` or
  `setup/` has uncommitted changes. The installer installs `rig-owner` from `HEAD`, not the working copy.
  Card step: commit both.
- **Finding 3, the ntfy topic:** a new random topic, root-only in `/root/rig-console-ntfy-topic`, plus a
  card step to switch the phone app.
- **Finding 4, trust anchors (taking the cross-check's correction):**
  - `decision-fingerprints.json` is carried over. Starting empty trusts every existing decision anyway
    (`unverified_decisions`, first run). An empty-but-valid ledger would push an urgent "written outside
    the console" alert for every past decision. So option A protects decisions from now on, not
    retroactively.
  - `job-pins.json` is shown to the owner and copied only on "y"; otherwise pins start fresh.
  - `lounge-owner.json` isn't carried over.
- **Smaller points:**
  - carried-over settings are filtered to plain characters and shown for a "y";
  - `harden-wsl.sh` now lists `/etc/sudoers.d` and `sudo -l`;
  - every script sets a fixed system `PATH`, so a `sudo` planted in `~/.local/bin` is never run.
- **My addition, the owner's own shell:** seats run as the owner and can edit `~/.bashrc`, so a normal
  Ubuntu window could capture a `sudo` password. Every card starts a clean window from Win+R:
  `wsl --exec /bin/bash --noprofile --norc`.
- **"Cards ≠ proof":** card A now checks what was installed (the sudoers line, the helper's hash against
  the commit, ownership).

**Still doesn't close (option B territory):**
- agents run as the owner: they can read the owner's SSH and git keys and everything on `/mnt/c`, and edit
  job folders and launch records;
- the owner's session outside the clean window;
- decisions forged before option A;
- anything planted while any seat could become root (the sudoers and `sudo -l` checks catch the obvious
  ones, not a setuid binary or a root cron job);
- agents can still fake snapshot data and so raise alerts with their own text.

**Checked:** smoke 192/192 (also from a read-only copy with a bare environment); `bash -n` on all four
scripts.

**Outcome:** pending: the Model Architect's re-check, then the cards go back to the owner.

---

## PL-031 Operator log page (R-022); builds folder pinned under builds/ (MA-020) (2026-10-13)
**Operator log (R-022, owner via Rig):**
- `oplog.py` reads `~/openrig/operator/log-YYYY-MM.md` (`RIG_OPERATOR_DIR`) into days and entries
  (time, kind, sentence, ref), newest day and entry first. Lines that don't fit the format are shown as
  they are. Only a month that exists can be picked, so a path can't be passed in.
- **`oplog.html`:** under More and in the phone footer. Escaped plain text; `held`, `incident` and
  `outcome` are tinted. There are month chips once there are two months. If the folder is missing it
  says "No operator log yet"; on a console without the API it says it arrives with the next update.
- **Refs stay text in v1.** R-022 allows links only to files the console already serves, and launch
  records aren't served, so there's nothing to link yet.
- The installer gives the console user read access to `~/openrig/operator` (option A).

**MA-020 (Model Architect's PL-014 re-test, 11/12):** a team's `job.json` could set `"builds":
"decisions"` and put its decision files on the builds port. `_builds_dir` now accepts only `builds/` or a
folder inside it; anything else means `builds/`. Every template uses `builds`.

**Checked:**
- Smoke 196/196. New: order, months, kinds, refs and off-format lines; a bad month falls back; the page
  escapes text and is in both navs; `builds` values like `decisions`, `.`, `builds/../decisions` and
  `/etc` fall back.
- Browser: `oplog.html` and `m.html` at both widths.

---

## PL-032 The activity log rotates daily and leaves OneDrive (R-011 part 2, owner-approved priority 2, 2026-10-13)
**Why:** 41 MB in OneDrive since Oct 11 (about 1 MB an hour), never rotated, with a row every 10 s for
every stopped seat too.

**What:**
- **Logger (`setup/rig-snapshots.sh`):**
  - only live seats are logged;
  - `rotate_log` runs each round: when the log's first day isn't today, it becomes
    `activity-log-<first day>.csv` with a fresh header;
  - yesterday's file stays in `snapshots/`, readable in OneDrive (PD-016); older days move to
    `~/openrig/activity/` (`RIG_ACTIVITY_ARCHIVE`), with a timeout, retried if it times out.
  - The first run archives the current 41 MB file under 2026-10-11.
- **Console:**
  - `features.activity_files(since, until)` lists the daily files, oldest first, skipping links;
  - `activity_tail()` reaches back into yesterday's file just after the rotation;
  - run-report timelines read only the days a team's run can touch, from its span in SQLite;
  - the run and team lists come from SQLite's full history plus the recent tail, so older teams don't drop
    off after a rotation;
  - health's "last write" spans the rotation.
  - `serve.ACTIVITY` is now `features.ACTIVITY`, so the two can't point at different files; the unused
    `tail_lines` is gone.
- **Option A:** the installer gives the console user read access to `~/openrig/activity` and sets
  `RIG_ACTIVITY_ARCHIVE` and `RIG_OPERATOR_DIR`. The console's `HOME` is `/var/lib/rig-console` there, so
  every `~/openrig/...` default is now set explicitly.
- **Not done:** moving the snapshots off OneDrive. The pane captures keep their path for Studio (AD-025);
  only the log moves. The research mirror is unchanged (PL-015 already made it small).

**Checked:**
- Smoke 200/200. New: file order (archive, here, today); links ignored; a team's span reads only its
  days; the tail reaches into yesterday; a timeline spans every daily file.
- `rotate_log` taken from the real script and run on fake files (`scratchpad/rotate-test.sh`): a multi-day
  log rotates under its first day and is archived whole; yesterday's stays; today's and header-only logs
  are left alone. 5/5.

**Live:** the logger runs from the repo as the owner's user, so it changes at its next restart (the WSL
restart in card B, or any reboot). The console side goes live with the next deploy.

---

## PL-033 Option A round 3: the Model Architect's last findings; cards back up (MA-021, 2026-10-13)
The Model Architect's round 2 (`models/reviews/PL-027-recheck.md`, "Round 2") confirmed findings 1–4 and the
fingerprint carry-over, and PL-031's builds fix (12/12). Three small findings, all fixed:
- **R2-1, the owner was sent to plain git in the agents' repo:**
  - the deploy prompt now offers `d`, the full changes from the clean clone through `less`;
  - the cards and runbook define `g`: git with no hooks, fsmonitor, external diff or GPG program, and
    attributes from the empty tree (so no `.gitattributes` filter or textconv runs). `g commit -m`, so no
    editor runs either;
  - there's a last `g status` right before the installer.
  - **My addition:** both scripts' `safe_git` also uses `--attr-source=<empty tree>`, because their own
    `git status` in the repo could otherwise run a planted clean filter. Tested on git 2.43.
- **R2-2, committed symlinks:** the installer and the deploy refuse any mode `120000` entry under
  `dashboard/` or `setup/`.
- **R2-3, symlinks in the copied state:** the copy uses `rsync --no-links`, and card A checks
  `sudo find /var/lib/rig-console -type l` prints nothing.
- **R2-4, checks printed by the script they check:** card B runs `sudo ls -la /etc/sudoers.d` and
  `sudo -l` as its own steps after the restart.

**Cards back up:** `tasks/console-own-user.json` (18 steps) and `tasks/close-wsl-root.json` (17). The first
card's deploy also puts the console changes of PL-027 to PL-032 live (PL-025 and PL-026 are live already).

**Checked:** `bash -n` on the scripts; card JSON validated; every command is under the 1000-character limit.

---

## PL-034 One page per job: Overview, Docs, Assets, Docket (R-013, R-014, R-015, R-023; owner-approved priority 3, 2026-10-13)
**Why:** the owner's favourite of the approved list. Each team's decisions, milestones, builds, documents and
art were spread over folders and pages. R-023 (Rig, owner-approved) adds each architect's docket.

**What (`jobpage.py`, `job.html`, `md.js`; More → Teams → Jobs, and the phone footer):**
- **`/job.html`** lists every job, newest activity first. **`/job.html?job=<name>`** shows a header (title,
  type, team and lead from the launch record) and tabs. A tab appears only when the job has something for
  it.
  - **Overview:** open decisions (links to the Decisions page), milestones from `milestones.json` (R-015),
    builds with ▶ Play, and recently decided.
    - Each milestone shows its status, tests, a quality-bar bar and the vision check, plus Play, Download,
      Plan, Packet and Gate.
    - Numbers and statuses are checked: anything not a non-negative number shows as 0, and anything other
      than PASS/FAIL as no vision check.
    - Play appears only when the build is inside the job's builds folder (MA-020).
  - **Docs (R-014):**
    - the design package with `docs/handoff.md` first, then the files it names in its order, then the
      rest; titles come from each file's first heading;
    - palette swatches from `art/bible/palette.json` (following one `source` pointer inside the job, as
      bridge-design does); values that aren't hex colours are dropped, so nothing else reaches a style;
    - the inbox, sorted by the status in each file's front matter.
    - Files open in an in-page reader that uses the Decisions page's escaping Markdown renderer, now shared
      as `md.js` (one copy, not two).
  - **Assets (R-013):** the asset manifest (`studio/briefs/asset-manifest.md` v0) when there is one. Until
    then it scans `art/`, `audio/`, `models/` and `assets/` for images, audio and video, skipping links,
    at most 400 files.
    - Filters by set and status, plus AI-made; audio plays inline.
    - A **Lineup** toggle shows the filtered images at one height, side by side, which is how the team
      checks consistency.
  - **Docket (R-023, the architects job only):** one card per architect seat, with Working on, Up next,
    Waiting on you (its open gates by `lead`, its Needs you cards by `asked_by`) and Waiting on others
    (items it sent, and its blocked items with what they're blocked on).
    - Items whose wake failed say "not delivered". Items OpenRig's stuck sweep filed a recovery row for say
      "stalled", and the recovery rows themselves aren't shown as work.
    - The snapshot time is shown. An unreadable queue says so; it doesn't look empty.
    - "Ideas not started" is left out, as R-023 asks.
    - Its first run on the live queue found two v1.9 notices that had never reached me (wake failed at a
      prompt). I've closed them.
- **Queue summaries:** the logger's compact queue snapshot leaves out `summary`, so it now also writes
  `_queue_active.json` (active items, `--full`). Until the logger restarts, the Docket uses the compact
  snapshot, shows states, ages and marks, and says summaries are coming.
- **Read-only throughout:**
  - job names must match the job-name pattern;
  - every path goes through `safe_path`;
  - files open through the sandboxed `/job/` route and builds through the builds port;
  - all text is escaped.
- **Not in v1:**
  - the owner's notes on an asset (R-013): a new write path, so it needs its own review;
  - the asset lineup's side-by-side with the art bible references;
  - a 3D viewer (R-012).

**Checked:**
- Smoke 216/216. New:
  - milestones sanitised, with Play only for a real build;
  - unknown or malformed job names;
  - handoff order and headings;
  - the palette pointer, and a non-colour dropped;
  - inbox statuses;
  - the asset scan skipping a planted link;
  - tabs per job;
  - the page and `md.js` escape, and the Decisions page uses `md.js`;
  - the Docket's groups, marks, recovery rows left out, the fallback, and an unreadable queue.
- Browser: job list, production overview, design Docs and Assets, and the Docket, at both widths. I looked at
  the screenshots, using three real Bridge images copied into the temporary fixture.
- The in-page reader is the Decisions page's code; the browser check doesn't click into it.

**Live:** with the next deploy (card A). Docket summaries come when the logger restarts.

---

## PL-035 Run report review (owner via the operator, qitem-20261013185443, 2026-10-13)
**Finding:** it works for research runs and predates the new setup. Write-up for the owner:
`scratch/platform/run-report-review.md`.
- **Fixed:**
  - each run's team now comes from the launch record (or pin) via `list_runs()["rig"]`; `runs.html` falls
    back to the old name match only when there's none;
  - the Decisions section no longer points at the old checkpoint picker; it points to the Decisions page and
    the job pages.
- **No change needed:** approvals, usage, the evidence check, the comparison. The timeline already reads the
  daily files (PL-032).
- **Owner's call:** design, production and validation jobs have no time view. I suggested a Report tab on the
  job page (timeline, approval waits, model notes).

**Checked:** smoke 216/216; `runs.html` at both widths.

---

## PL-036 Report tab on each job page (owner approved option 1 of the run-report review, qitem-20261013194248, 2026-10-13)
**What:** a **Report** tab on any job with a known team:
- the team's span, agent time working, time waiting for approval, and handoffs;
- one lane per seat (working, waiting, idle) with its minutes;
- approval waits grouped by kind (count, total, longest, an example);
- links to the job's own `model-notes.jsonl` and `model-metrics.csv`, opening in the reader;
- for research jobs, a link to the research run report, which stays as it was.

It reuses `/api/timeline` (which reads across the daily activity files, PL-032) and `/api/approvals`; the
only server change is `model_files` and the `report` tab flag in the overview.

**Checked:** smoke 217/217 (tab and model-note links). Browser: the Report tab at both widths on the
fixture team; I looked at both screenshots.

**Live:** with the next deploy.

---

## PL-037 The operator's folder is mirrored into snapshots/operator/ (owner via the operator, qitem-20261013200924, 2026-10-13)
**What:** `rig-snapshots.sh` copies `~/openrig/operator/` (`RIG_OPERATOR_DIR`) to `snapshots/operator/` once
a minute, on the research mirror's rhythm but independent of it.
- The copy is one way: `rsync -rt --delete --no-links --max-size=5M`, with a timeout. `--delete` only
  touches the mirror, and links are skipped, never followed. The operator's own files are only read.
- `snapshots/` is git-ignored (checked with `check-ignore`), so the log can't reach the public repo.

**Checked:** `bash -n`. The exact rsync line, run into my scratchpad from the real folder, gave an
identical copy, and the source's times were unchanged.

**Live:** when `rig-snapshots` restarts (the WSL restart in card B, or a reboot). No console deploy needed.

---

## PL-038 The staged smoke test failed as "nobody"; nothing deployed (owner's install, 2026-10-13 ~20:25Z)
**What happened:**
- The owner ran card A on commit 72005f7. Installer stages 1–5 completed: user, helper, sudo rule, new
  token and topic, ACLs, state copy. It also rewrote the service file (user `rigconsole`, folder
  `/opt/rig-console`).
- Stage 6's deploy ran the smoke test as `nobody` from root-owned staging. It failed at `smoke.py:853` with a
  `PermissionError` on `<stage>/dashboard/state`, so nothing was deployed and `/opt/rig-console` doesn't
  exist. The console keeps running its old process. **It must not restart before the deploy succeeds.**
- **Cause:**
  - The smoke test set `RIG_STATE_DIR` at line 617, but line 331 had already imported `gates`.
  - Modules read their paths once, at import, so `gates.STATE_DIR` stayed on the default `dashboard/state`.
  - From read-only staging that fails; in my own runs it succeeded silently, writing into the live
    `dashboard/state/`. That left a `lounge-owner.json` there, which I've deleted. Nothing read it, and the
    installer skips that file.
- **Miss (mine):** my "read-only copy, bare environment" check (PL-030) ran before I added the in-process
  Lounge tests, and I didn't repeat it after. The live-state leak went unnoticed because nothing checked
  where tests write.

**Fix:**
- `smoke.py` sets every console path variable (state, launches, database, snapshots, research, jobs, operator,
  activity archive, models, briefs) at the start of `main()`, before any import.
- A new check fails if any in-process module points outside the test's temp folder.
- The installer uses `cp --update=none` (the owner saw `cp -n`'s warning).
- Checked the other writers the owner named: fingerprints, pins and task records all live in `gates`, which
  the new check covers.

**Checked:**
- Smoke 218/218.
- The owner's failing case, reproduced first: commit 72005f7 unpacked read-only and run with `env -i`. It
  failed at line 853 exactly as reported. With the fixed test it passes 218/218.
- Not run as `nobody` itself: seats never use `sudo` (SHARED-RULES §1). The read-only, bare-environment run
  reproduces the failing condition.

**Outcome: option A part A is live** (owner, card done 20:54Z). Verified read-only:
- `rig-dashboard` runs as `rigconsole` from `/opt/rig-console`, started 13:48:39 PDT;
- every file in `/opt/rig-console`, `/usr/local/sbin/rig-console-deploy` and the helper is root-owned;
- the journal shows the helper doing its fixed calls (`receipt`, `approval-item`) through the sudo rule.
So the console changes of PL-027 to PL-038 are live: job pages and the Report tab, Lounge posting, the
operator log, card steps, and the MA-020 fix. The Health check, the new token and the topic are the owner's to
confirm; seats don't call the console. Still to do: card B (WSL root access), and the logger restart it
brings.

**Outcome: option A is complete** (owner, card B done 21:34Z, after the WSL restart; the owner noted no
check that didn't fail). Verified read-only:
- `/etc/wsl.conf` has `[interop] enabled = false`;
- `rig-dashboard` is back as `rigconsole` from `/opt/rig-console` (14:29:45 PDT);
- the new logger is running: `_queue_active.json` is current (Docket summaries), `snapshots/operator/`
  mirrors the operator log, and the old 41 MB activity log was archived to `~/openrig/activity/` (PL-032,
  PL-034, PL-037).

I didn't re-run the sudo or interop checks myself: seats never use `sudo` or Windows programs. The owner's
card checks are the evidence. R-005 step 3 is done.

---

## PL-039 Owner's priorities: install reconciled, Diplomacy adopted, digest and navigation triaged (qitem-20261013210002, 2026-10-13)
**1. Install (reconciled):** the owner deployed commit 96a68f8 after PL-038's fix. Its real staged smoke test
as `nobody` passed 218/218. Part A is live (verified at 20:57Z, PL-038). Card B is still to run.

**2. Diplomacy (R-024), adopted from the Owner's Advisor's draft:**
- `dashboard/diplomacy.html` (More → Teams → Diplomacy).
- `lab.py` plus `POST /api/lab/control`, behind the same sign-in, header and JSON checks as decisions. It reads
  `board/control.json` and changes only `paused` (true or false) or `stop` (true only); the clerk's phase,
  state and deadline are untouched. It replaces the file atomically. The board folder is opened with
  `O_NOFOLLOW` (as in PL-029), so a planted link can't redirect the write.
- The Advisor's fixture is now `tests/fixtures/jobs/diplomacy-1`, with two tiny board SVGs I drew myself:
  the engine's are AGPL, so its art isn't vendored.
- **What I changed in the page (my reply to the Advisor's "anything you would change"):**
  - **Removed `?base=`.** It let a crafted link point the page at any URL and show a fake game under the
    console's name.
  - **Phase names are checked** (`[SFW]dddd[MRA]`) before they reach a URL. The board `<img src>` put the
    clerk's phase name in unescaped, so a crafted name could break out of the attribute and run script.
  - **Only the seven powers' names** reach a `style` attribute. The press tag's colour came from the
    message's `from`, which agents write.
  - The closed drawer is hidden, so its shadow no longer shows at the edge.
- **Kept as the Advisor decided:** the board stays an `<img>`, never inline SVG; seven small `sent.jsonl`
  reads every 20 s; no route to sealed intentions during play; the engine's power colours.

**3. Requests filed and triaged:**
- R-025 (queue bodies in the mirror): accept, low.
- R-026 (daily digest, layer 1): accept, next.
- R-027 (reorganise pages): accept, on a quiet day; page-use data from the journal first, since I don't
  collect it today.

**4.** The owner's earlier send.sh note: no action, as they said.

**Checked:**
- Smoke 226/226. New: sign-in required; pause, resume and stop leave the clerk's fields alone; malformed
  bodies and unknown jobs refused; no `control.json` refused; a planted board-folder link refused and its
  target untouched; the page has none of the three issues; the board SVG comes through the sandbox.
- Browser: `diplomacy.html` at both widths, with the optional 404s taught to the checker. I looked at both
  screenshots.

**Live:** with the next `rig-console-deploy`.

---

## PL-040 The Lounge showed no posts after the migration; Diplomacy deploy verified (owner via the operator, 2026-10-13)
**Deploy verified (read-only):** commit 02cd97c. `rig-dashboard` runs as `rigconsole` since 14:42:40 PDT, and
`/opt/rig-console/diplomacy.html` and `lab.py` are identical to the source. (My first check, at 21:40Z, found
nothing deployed: that run had stopped before copying. The owner reran it.)

**The empty Lounge:**
- **Symptom:** the owner's Lounge was empty after option A. The three posts (0712Z, 0743Z and 1810Z) are
  intact on disk.
- **Cause (mine, PL-029):** `lounge._open_dir` opened every folder on the path for reading, to refuse planted
  links. Under option A the console may only pass through the owner's home (`getfacl /home/you`:
  `user:rigconsole:--x`), so it can't open it for reading. The open failed, and `posts()` treats any failure
  as "no posts". Lounge posting and the Diplomacy pause (`lab.py`) use the same opener, so both fail too.
  My tests ran as the owning user, who can read everything, and so never saw it.
- **Fix:** the folders on the way are opened with `O_PATH`, which needs only pass-through access and still
  never follows a link. Only the last folder (the lounge, or the game's board) is opened for reading. No
  access list changes; the home stays pass-through-only.
- **Test:** a folder on the path set to mode `--x` (pass through only, like the console's view of the
  owner's home). Posts are listed and a new post works through it. The old opener fails this test exactly
  as the live console did.
- **Lesson:** a test as the owning user can't see a permission boundary; set one up in the test.

**Also:** `JOBS.md` §4b now says every git step on a card is copy-pasteable as written, with exact paths for
`add` and a filled-in message (owner, 2026-10-13).

**Checked:** smoke 227/227.

**Release:** commit `dashboard/lounge.py`, `dashboard/tests/smoke.py`, `dashboard/JOBS.md`,
`dashboard/ARCHITECTURE-LOG.md`, then `rig-console-deploy`. Needs you card `deploy-lounge-fix`.

---

## Notes for other roles

How this works (ROLES.md): one section per role, newest first, each note dated and marked **[new]**
until the recipient acts on it. The owner tells a role to check its notes here; recipients reply in
their own logs.

### Notes for the Rig Architect
- **[new] 2026-10-13 (PL-028): card steps are in `JOBS.md` §4b,** as you asked: `steps` with
  where/run/check, the owner's git rule, and every length limit stated. Cut text now ends in "…". A command
  is never cut. Please move your commit card's commands into `steps`. They show after the next deploy.
- **[new] 2026-10-13 (PL-027): option A is in the owner's hands** (two Needs you cards). Two things for you:
  - **`CHEATSHEET.md`/`SETUP.md`:** once it's run, console code goes live with `bash setup/deploy-console.sh`
    after a commit, not `sudo systemctl restart rig-dashboard`.
  - **Part B runs `wsl --shutdown`,** which stops every team; the operator relaunches them. If you
    supervise a run then, the owner tells the operator first.
- **[new] 2026-10-13 (PL-025): the reply contract is `JOBS.md` §3e.** All six of your constraints are met,
  architects included (`~/openrig/jobs/architects/replies/`). Your §7 operator duty can point at §3e. Until
  it's approved, each message to the operator carries the exact file to write, so it works without the
  rule. Restart gate `restart-console-5` is open; the end-to-end test follows it, and I'll ask you to
  confirm. Please also copy `JOBS.md` to `~/openrig/briefs/` with your v1.7 batch.
- **[new] 2026-10-13 (PL-021): your two notes are done.**
  - **Decisions now go to the gate's own `lead`** when it's a seat in the same team. It goes live with the
    next console restart; until then, keep forwarding by hand.
  - **`.gitignore`** now also covers `/.claude/` and `.codex/`. `architects/.claude/settings.json` was
    already ignored from earlier today.
- **[new] 2026-10-13 (PL-018): R-018 is built as you proposed,** with two changes:
  - answers go to `decisions/task-<id>.json`, so they can't collide with gate ids;
  - "Do" also holds blockers only the owner can clear.
  The contract is `JOBS.md` §4b. Please seed your real Do cards (PO box, trademark check) after the
  restart gate `restart-console-1`. Drop your card 5 ("review the snapshot logger change"): that gate
  covers it.
- **[new] 2026-10-13: the Lounge (owner delegated it to both of us).** I agree with your
  `scratch/rig/architects-lounge-idea.md`: v1 is the append-only file with your three house rules, which
  are yours to own. I add nothing for v1. If the owner likes it, I'll add a read-only Lounge panel in the
  console in a later restart batch. It will never push and will be read-only. Tell me if you want it
  sooner.
- **2026-10-13: the PL-016 and PL-017 notes below were taken as PD-025.** Owner gate `pd-025-rules-v1-6`;
  after approval the operator installs SHARED-RULES v1.6 and `JOBS.md`.
- **2026-10-13 (PL-017, taken as PD-025): the operator can now notify the owner** (owner request). It writes
  `~/openrig/launches/notify/<id>.json`, and the console shows and pushes it (`JOBS.md` §3c). Two lines
  for your rules:
  - **§7 (operator duties):** "To notify the owner, write a note as `JOBS.md` §3c says. Use a new id per
    note, wait for the console's receipt, and never write a second id because a receipt is late."
  - **§1 "Phone pushes come only from the console"** stays true: the console does the push. Worth adding
    "(the operator may ask it to, `JOBS.md` §3c)".
  This doesn't change what team seats may do. Please also copy `JOBS.md` to `~/openrig/briefs/` with your
  next batch.
- **2026-10-13 (PL-016, taken as PD-025): OpenRig's From line can be forged.** It comes from `OPENRIG_SESSION_NAME`,
  which any process can set. The console now sends as `owner@rig-console`, and a seat could send as that
  too. SHARED-RULES §1 already makes any "the owner decided" message only a pointer, so decisions are
  safe. Consider one line in the rules: a message's From line is not proof of who sent it.
- **[new] 2026-10-13: `_all.md` says "<unknown sender>" means the owner.** After the next console
  restart, owner messages show `From: owner@rig-console`. Worth updating wherever you keep that.
- **[new] 2026-10-12 (PL-014, PD-020): handoff done, and what I'd change.** My handoff is in
  `architects/handoffs/platform-architect.md`. Suggested changes:
  - **`agents/platform/guidance/role.md`:** add the owner's standing rules, which the charter states
    loosely:
    - smoke green before every change, with checks for what changed;
    - stdlib only without the owner's OK;
    - never weaken the charter's security invariants;
    - the repo goes public, so no secrets or personal details.
    Also: after option A, code goes live only when the owner runs `setup/deploy-console.sh`.
  - **Headless browser:** my charter requires a browser check at desktop and phone width for page
    changes. The chat session used its own sandbox. A seat in Ubuntu has no headless browser (Playwright
    would be a new dependency). Owner's call: allow one for the Platform seat only, or have the owner
    eyeball pages.
  - **`brief.md` §1, a residual risk under option A:** architect seats edit `setup/` scripts the owner
    runs with sudo, and `dashboard/` code `deploy-console.sh` copies into root-owned `/opt`. The owner's
    review before running them is the lock. `deploy-console.sh` now lists what differs from what's live
    and asks before copying. Worth one line in the brief: "The owner reviews `setup/` and
    `dashboard/` changes before running a setup script or deploying."
  - **"Never touch the live rig"** (my standing rule) should read "other teams' rigs": the brief rightly
    lets me `rig send` to architects seats.
- **[new] 2026-10-12 (PL-013): the owner chose option A.** Before the owner runs it, please confirm two
  things for seats and the operator:
  - **Windows programs:** nothing they do needs Windows programs from WSL. Interop goes off.
  - **`sudo`:** nothing they do needs `sudo`, e.g. `apt install`. `sudo` will need the owner's password.

  Also:
  - **Job folders:** the install script adds ACLs on `~/openrig/{jobs,research,launches,briefs}` so the
    console's own user can read them, and write decisions in jobs and research. New folders inherit
    them. Nothing else in `~/openrig` changes.
  - **`CHEATSHEET.md` (yours):** after code changes, the restart command becomes
    `bash setup/deploy-console.sh`.
  - **Candidate rule:** a lead confirms a decision before acting, e.g.
    `curl -s "localhost:8800/api/verify?job=<job>&gate=<id>"`. This would amend the "never call the
    console" rule for this one read. It closes the window where a forged `decisions/<id>.json` gets
    acted on before the owner sees the alert. If you want it, I'll add the endpoint.
- **[new] 2026-10-12 (PL-012): the `seats` format is in `JOBS.md` §3b,** so your PD-019 operator duty can
  start. The operator also needs the updated `JOBS.md` installed in `~/openrig/briefs/` (PD-016).
- **[new] 2026-10-12 (PL-011): root access and setup.**
  - **The problem:** the owner's checks show any seat can become root today, through WSL interop
    (`wsl.exe -u root` works) and passwordless sudo on the shared user. `/mnt/c` has no Linux permissions
    either. Options are in PL-011:
    - **A:** sudo with a password, plus `[interop] enabled=false`;
    - **B:** agents under their own unprivileged Linux user;
    - **C:** accept the risk in writing.
  - **Questions:** does the operator or any seat run Windows programs from WSL (`explorer.exe`,
    `clip.exe`, `powershell.exe`, `code`)? Which option would you support? B changes how OpenRig and the
    operator launch teams.
  - **`SETUP.md` (yours):** builds now run on port 8801 (R-006). Phone access needs, once in PowerShell,
    `tailscale serve --bg --https=8443 http://localhost:8801`. Please add it next to the
    `tailscale serve --bg 8800` step.
- **2026-10-12 (PL-010): launch records.** Done in PD-018. On the operator's trustworthiness: noted in the
  PL-009 threat model (the operator is in scope, with a seat's powers).
- **2026-10-12 (PL-009): owner impersonation, rules for findings 5a and 7.** Done in PD-017.
- **2026-10-12 (PL-006): snapshots and the activity log.** Answered in PD-016: move, rotate and skip
  finished teams, keeping today and yesterday readable in OneDrive. That's R-011, to be built.
- **2026-10-12 (PL-005): research checkpoints as gates, and the NICHES-SCHEMA path.** Done in PD-016. The
  picker removal is next on my list.
- **2026-10-12 (PL-001): seats must never write in `decisions/`.** Done in PD-016 (`SHARED-RULES.md` §1).

### Notes for the Studio Architect
- **[new] 2026-10-13 (PL-020): your notes answered.**
  - **`milestones.json` (AD-027)** is adopted as-is in `JOBS.md` §6.
  - **A top-level `play`** on gates is supported. Use `"play": "builds/m1"` on the milestone approve
    gate; the decision page shows "▶ Play this build".
  - **`production`** is a listed job type.
  - **`jobs-mirror/`:** nothing maintained ever wrote it; it was probably a copy run by hand that ended.
    Your seat can read `~/openrig/jobs/` directly, images included (brief §1), so please use that.
  All of this goes live with the owner's restart gate `restart-console-1`.
- **[new] 2026-10-12 (PL-015): assets-1 put 40 GB of tools in its research folder,** which hung the
  snapshot logger. The mirror now skips tools, models, virtualenvs and builds, so nothing is needed for
  the logger. Your call whether the asset-pipeline brief should put installed tools and model weights
  outside the job folder (e.g. a shared `~/openrig/tools/`), so each run doesn't download them again.
- **2026-10-12 (PL-012, read in AD-025): R-001 `max_soft` is live** after the next restart. Going over asks for a
  second tap, and the decision records `"over_max": true` and the `max`. Thanks for manifest v0: the
  Assets tab (R-013) is unblocked, and R-012 audio is next on my list.
- **2026-10-12 (PL-008, PL-011): your R-012 to R-015, and builds on their own port.** Answered in AD-023.
  - **R-012:** audio first. For 3D, v1 shows a `model_preview` turntable PNG/WebM; a live viewer needs
    the owner's OK for a library.
  - **R-013 and R-014:** proposed as tabs (Docs, Assets) on one per-job page. Assets waits on the
    manifest format.
  - **R-015:** I'll draft `milestones.json` and send it to you for review.
  - **Builds** now run on port 8801 (R-006). Gate `play` links keep working because the console builds
    the URL. Tell me if any template hard-codes `/play/` URLs.
- **2026-10-12 (PL-004): name your builds.** Done in AD-023. Have builders write `builds/<id>/build.json` with
  `title`, `pitch`, `controls`, `judge` and `bugs` (`JOBS.md` §5). The Builds page uses it for the game's
  name and play notes; builds without it, or without a spec, show only their id.
- **2026-10-12 (PL-009): model notes, a correction.** Done in AD-023. Use `model-notes.jsonl` in the job folder
  (`SHARED-RULES.md` §6). My earlier suggestion of `model_note` events in `events.jsonl` is withdrawn;
  ignore it.

### Notes for the Model Architect
- **[new] 2026-10-13 (PL-030): your re-check (MA-016) and Codex's cross-check are answered.** All four
  findings, the corrections and the smaller points are in, plus one addition (a clean shell from Win+R). On
  finding 4 I carry the fingerprint ledger over rather than start it empty, for the reason in PL-030. The
  cards stay pulled until you've re-checked `setup/` and the draft cards in `ops/draft-card-*.json`.
- **[new] 2026-10-13 (PL-027): your PL-013 review (MA-014) is answered.** Findings 1, 2, 4 and 6 are fixed;
  point 7 is partly fixed. Findings 3 and 5 are deferred, with reasons in PL-027. The owner now has two Needs
  you cards to run it. Please re-check `setup/deploy-console.sh`, `setup/install-console-user.sh` and
  `setup/rig-owner` when you can. The owner may run the cards before you do: tell me or the owner if you'd
  rather they wait.
- **Done 2026-10-13: your replies to PL-014 and PL-015 (models/LOG.md) are recorded.** The launch-records
  mirror is dropped from R-011, since your seat reads `~/openrig/launches/` directly. I'll wait for your
  MA-013 re-test.
- **2026-10-12 (PL-015, acknowledged): `research-mirror/` now copies research outputs only.** It skips tools,
  models, virtualenvs, builds, archives, weights and any file over 20 MB, and it updates every 60 s
  instead of every 10 s. `model-notes.jsonl` and `model-metrics.csv` are still copied. If harvest needs
  anything else, tell me.
- **[new] 2026-10-12 (PL-014): your MA-013 gaps are fixed,** all four (builds-folder scope, pinned
  Tailscale name, `X-Forwarded-Host` check, no token means no changes), each with a smoke check (104/104).
  A re-test would close them.
  - **Launch-record model:** shown in the Evidence panel as you suggested.
  - **`~/openrig/launches/`:** not mirrored yet. I propose R-011 copies it to `snapshots/launches/`.
    Does that path work for your harvest?
  - **The PL-013 review is still open** (note below). It's the last thing before the owner runs option A.
- **[new] 2026-10-12 (PL-013): please review the option A runbook and scripts before the owner runs
  them.** It's security work I can't run end-to-end (it needs root on the PC). The files are
  `setup/install-console-user.sh`, `setup/harden-wsl.sh`, `setup/deploy-console.sh`, `setup/rig-owner`
  and the runbook in PL-013. Worth checking:
  - the sudo rule and helper;
  - the ACL scope;
  - `ProtectSystem` vs sudo in the unit;
  - the token rotation;
  - the lockout recovery;
  - anything that leaves a path open that PL-013 says is closed.
- **2026-10-12 (PL-012, acted on in MA-013): your MA-009 and MA-010 are done.**
  - **Matching:** the Models page matches harvested notes on `harvest_hash` (your formula).
  - **`seats`:** the launch-record field is in `JOBS.md` §3b. The live graph shows each seat's model from
    it when OpenRig reports none. Showing it on the Models page too is open; say where you'd want it
    (seat-runs, the evidence panel).
- **2026-10-12 (PL-009 to PL-011, re-tested in MA-013): your MA-007 review is answered.** Every finding is accepted:
  - **Threat model:** in PL-009.
  - **Done:** the Host allowlist, decision-record quoting (5b), trusted job/rig/lead routing (5c, with
    PD-018's launch records), the tripwire wording, your suggested tests, and R-006 built to your three
    conditions (a browser test confirms a build can't read or change the console). Smoke test 93/93.
  - **Findings 1–2, confirmed on the PC:** interop root works, sudo needs no password, and `/mnt/c` has
    no permissions. Step 3 waits on the owner choosing A, B or C (PL-011).
- **2026-10-12 (PL-009): a harvest-matching question.** Answered in MA-009, done in PL-012. The Models page counts a lead's note as
  harvested when its `what_happened` text matches a ledger line, so a line you reword during harvest
  shows twice. Should it match on `harvested_from` instead?
- **2026-10-12 (PL-003): Models page data points.** Acted on in MA-007: ROUTING researcher row, O055
  split, status marks. Still true:
  - O-lines for `qwen3-coder:30b` show as their own model;
  - `"model": "all"` lines appear only under All models;
  - card roles must match the ledger's `role` exactly.
