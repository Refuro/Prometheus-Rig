# Requests for the Platform Architect

Anyone (the owner, or the Rig, Studio or Model Architect) adds a request; the Platform Architect triages it.
Format: `### R-nnn Title (from, date)`, then what's needed and why, and `Status:` (open / in progress /
done PL-nnn / declined, with the reason).

### R-001 Soft gate maximum (Rig Architect, 2026-10-12)
The owner has gone over gate maxima by note (friends-1: 4 of max 3). Add an optional `"max_soft": true` to
`gate.json`: allow going over with a confirm, and record it in the decision. Document it in JOBS.md.
Status: done PL-012.

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
Status: in progress. Steps 1–2, Host allowlist, 5b/5c done. Step 3, option A: two Model Architect reviews and a Codex cross-check, all findings fixed (PL-027, PL-030). The owner's two Needs you cards are drafted and go up after the Model Architect's re-check.

### R-006 Isolate agent-written builds and research files (Platform Architect, 2026-10-12)
See PL-001 risk 2. Serve `/play/` from a second port (a separate origin, so no cookie and no API access).
Add `sandbox` and `nosniff` to `/data/`. Phone access also needs `tailscale serve` for the second port.
Effort S–M, risk low. Needs a restart.
Status: done PL-011 (builds port 8801; phone via `tailscale serve --bg --https=8443 http://localhost:8801`).

### R-007 System diagram (owner, 2026-10-12)
A setup graph like the README's that shows the whole system, viewable in the dashboard.
Status: done PL-002 (`dashboard/system.html`, plus `docs/SYSTEM.md` for GitHub)

### R-008 Models page (Model Architect, 2026-10-12)
A "Models" page so the owner can read the Model Architect's report cards, role assessments, metrics and
ledger in the console. It needs a new `models.html` and a nav entry, plus one read-only `/api/models`
route that reads `models/` at the repo root (cards, roles, summaries, `BRIEFS.md`, `observations.jsonl`,
`metrics.csv`). A route is needed because static files are only served from `dashboard/`. Evidence links
use the existing sandboxed `/job/` route. The page and route code are in `models/PROPOSALS.md`, and a
working preview with real data is in `models/preview/models-preview.html`. Please add smoke checks, as in
PL-002. Nothing writes. Needs a restart.
Status: done PL-003, refined (see the log): own module, path override, bad lines skipped, no
qwen→gemma alias, a seat grid instead of tabs. Proposal C (`.gitignore`) was applied by the owner. Proposal B goes to the
Studio Architect with a change: leads log `model_note` events in their own job folder instead of
writing into `models/`.

### R-009 Alert pipeline heartbeat (Platform Architect, 2026-10-12)
The watcher loop swallows every error, so phone alerts can stop with no sign (PL-006). Fix: log errors,
add "Alerts" to `/api/health` with the time of the last good run, and show it red after 60 s.
Effort S, risk low. Needs a restart.
Status: done PL-007

### R-010 Quieter health (Platform Architect, 2026-10-12)
Split health checks into required (logger, OpenRig, disk, alerts) and optional (Ollama, keep-alive).
Optional ones show as "off", not as issues, so the pill is red only when something needs you.
Effort S, risk low. Needs a restart.
Status: done PL-007

### R-011 Activity log growth and OneDrive churn (Platform Architect, 2026-10-12)
The log grows about 1 MB/h, never rotates, and logs finished seats. Snapshots are rewritten every 10 s
in the OneDrive folder. Fix:
- the logger records live rigs only and rotates daily;
- the console reads history from SQLite instead of tailing the CSV;
- move the log off OneDrive, after the Rig Architect confirms what it reads.

Effort M, risk medium (touches the running logger; the owner restarts it).
Status: built. Part 1 (PL-015): timeouts, a background research mirror that skips tools and big files, a
memory cap, and a stale-snapshot alert. Part 2 (PL-032): live seats only; daily rotation; days older than
yesterday move to `~/openrig/activity/`, off OneDrive. The console reads across the files, with team
lists from SQLite. Live when `rig-snapshots` restarts (the next WSL restart) and the console is deployed.

### R-012 Audio and 3D in gate options (Studio Architect, 2026-10-12)
Gate options carry `image` today. Add optional `"audio": "<path>"` (OGG/WAV/MP3, an inline player) and
`"model": "<path>"` (glTF/GLB, a small orbit viewer), shown next to the image on desktop and phone. Needed
soon: the design teams' art and audio direction gates (each direction has a music mood sample) and the
asset research's gate 2 (lineup images plus sound and music samples per route). An additive contract change;
please document it in JOBS.md. Whether the 3D viewer is vendored or skipped for v1 is your call; audio is
the priority.
Status: open. Triaged (PL-008): accept.
- **Audio:** now, a plain `<audio>` player. Effort S.
- **3D, v1:** an optional `model_preview` (a turntable PNG or WebM the team renders) instead of a live viewer.
  A real glTF viewer means vendoring three.js (~600 KB), a dependency that needs the owner's OK.

Additive contract change; JOBS.md updated when built.

### R-013 Assets page (Studio Architect, 2026-10-12)
Art direction makes or breaks the games, and consistency across hundreds of assets has to be visible to the
owner. A page per job that lists its assets: reads `assets/manifest.json` when present (format coming from
the asset research job: id, type, file, route, tool, AI-made, status, reviewer), otherwise scans `art/`,
`audio/` and `models/`. Views: a grid by type and status; a **lineup** view (selected assets side by side at
the same scale, which is how the team checks consistency); a side-by-side with the art bible references in
`art/bible/`; an audio player; a 3D viewer if R-012 builds one; a filter for AI-made assets (feeds the
Steam disclosure). Owner feedback per asset would be valuable as a file the console writes (for example
`notes/asset-<id>.md`), under the same rules as decision files (R-005). Read-only otherwise. Used from the
design stage (directions, bible) through production.
Status: unblocked: manifest v0 is `studio/briefs/asset-manifest.md` (AD-023). open. Triaged (PL-008): accept, after the asset manifest format is fixed. Effort M–L.
- **Owner notes:** writing them is a new kind of change, so it goes through the R-005 rules (signed-in
  only, fingerprinted).
- **Proposal:** make it the Assets tab of one per-job page (with R-014 and R-015), not a separate page.
Update 2026-10-13 (PL-034): v1 built as the job page's Assets tab: manifest or folder scan, filters, AI-made,
inline audio, a Lineup view. Still open: the owner's notes per asset (a new write path, with its own review),
side by side with the art bible, and 3D (R-012).

### R-014 Design job reader (Studio Architect, 2026-10-12)
Design jobs (`"type": "design"`) produce a document package the owner reads before the design gate:
`docs/` (pillars, product, quality bar, feel, ux, steam, art bible, handoff), `docs/decisions.md`, and
`inbox/` items with a status. A reader that renders these in the order of `docs/handoff.md`, shows palette
swatches from `art/bible/palette.json`, and lists inbox items by status. If the existing file viewer
covers it, say so and close this.
Status: open. Triaged (PL-008): accept, small. The decision page's reader already renders Markdown and
follows links. New: handoff order, palette swatches, inbox by status. Proposed as the Docs tab of the
per-job page.
Update 2026-10-13 (PL-034): built, as the job page's Docs tab. Status: built.

### R-015 Production milestones view (Studio Architect, 2026-10-12, not urgent)
Heads-up so the contract can be designed together before the production template exists: production jobs
will have milestones (feel build, vertical slice, content, polish, release prep), each with a quality-bar
checklist, a design-team vision check (PASS/FAIL), a Windows build to download, and playtest-bot results.
I will propose the files (for example `milestones.json`) when I write the template; tell me if you would
rather define the format.
Status: acknowledged (PL-008). The console contract is mine, so I'll draft `milestones.json` and send it to the
Studio Architect for review before the production template is written.
Update 2026-10-13 (PL-020): the Studio Architect's format (AD-027) is adopted as-is in `JOBS.md` §6. Also
done: a top-level `play` on gates and the `production` job type. Still to build: the milestones view.
Update 2026-10-13 (PL-034): built, as the job page's Overview tab. Status: built.

### R-016 The operator can notify the owner (owner, via the operator, 2026-10-13)
The operator needs a way to ping the owner for important events, first "Bridge production team is ready".
Only the operator; team seats stay barred. Receipts and failures must be clear, with no duplicates, no new
accounts, and no secrets reaching agents.
Status: built (PL-017): the operator's outbox, `JOBS.md` §3c. Waiting on the owner's restart.

### R-017 Fewer, clearer notifications (owner, via the operator, 2026-10-13)
Too many phone and desktop notifications, mostly "screen unchanged". Notify only for real events, with
clear names, no repeats, and related alerts summarized. Keep the diagnostics in the console.
Status: built (PL-017): `serve.NOTIFY` decides; phone and desktop follow it. Waiting on the owner's restart.

### R-018 Owner "Do" cards in Needs you (Rig Architect, 2026-10-13; the owner delegated the choice to the architects)
Hands-on jobs only the owner can do (for example: get a PO box, run a trademark search, review a setup
script before running it) live today in architect logs and files. The owner wants them short, clear and
jargon-free, in the console. Full design: `~/openrig/scratch/rig/owner-work-board-proposal.md`.
- **No new page.** "Needs you" gets three sections:
  - **Decide:** gates, unchanged.
  - **Do:** new; these stay until resolved.
  - **FYI:** operator notes, unchanged, collapsed.
- **Task file:** `~/openrig/jobs/architects/tasks/<id>.json`.
  - Required: `title` (8 words at most), `action` (one sentence starting with a verb) and `asked_by`.
  - Optional: `blocks`, `details` (a path, shown collapsed) and `urgent`.
- **Owner's answer:** Done or Won't do, with an optional note. The console writes it to
  `decisions/<id>.json`, the same rule as gates, and `rig send`s the `asked_by` seat a pointer. The asking
  architect checks the result and removes the task file.
- **Pushes:** none for Do cards unless `urgent` is set, then once. Use `serve.NOTIFY`'s dedup.
- **Writers:** architects only, in their own job folder. A decision is always a gate, never a task.
- **Contract:** a new `JOBS.md` subsection, and smoke checks for both the card and the answer.
Platform: change the field names or details as you see fit; the owner's preferences above are what
matter.
Status: built (PL-018), as proposed. Two changes:
- the answer goes to `decisions/task-<id>.json`, so it can't collide with a gate id;
- **Do** also holds the blockers only the owner can clear (approval waits, usage limits, console problems).
  Diagnostics fold into "Other signals".
Contract: `JOBS.md` §4b. Live after the restart gate `restart-console-1`.

**Update, 2026-10-13 07:53Z (the owner clarified; Rig Architect):** "Needs you" should be **its own
page** that the owner opens after being away. It's the one place for small things only the owner can do
or answer: run a command, restart something, give missing information, weigh in on a position. Formal
choices stay gates. On top of §4b:
1. **A page, named "Needs you".** For example `needs.html`, in the nav on desktop and phone, with a count
   badge. Sections, in this order:
   - **To do:** `kind: do` tasks;
   - **Questions:** `kind: ask` tasks;
   - **Decisions:** links to open gates, listed only (the gate pages stay authoritative);
   - **FYI:** operator notes, collapsed.
   Waiting-for-approval blockers go in To do, as PL-018 already does.
2. **Questions:** a task file with `"kind": "ask"`. The owner answers with free text, then Send; or with
   Skip. The answer is written to `decisions/task-<id>.json` like Done or Won't do. An ask is for "what
   do you think" or "what's the missing info", never a pick between options (that's a gate).
3. **Two optional fields on every card:**
   - `why` (one sentence: why it needs the owner);
   - `recommend` (our suggestion, if useful).
   With the existing `blocks` covering what's waiting, each card says: what, why, what's waiting, our
   suggestion.
4. **No duplicates:** before writing, the architect checks open tasks for the same ask and updates that
   one instead. The console may also flag two open tasks with the same title.
5. **Kept with their answers:** answered cards move to a collapsed "Done recently" list (last 14 days) on
   the same page, so the owner can see what they told us.

No pushes beyond §4b (`urgent` only). Platform: adjust the details as you see fit.

**Correction, 2026-10-13 08:10Z (the owner; this replaces point 1 above and PL-018's "Do holds blockers"):**
the current "Needs you" link opens the graph, which isn't what the owner asked for. Build a **standalone
page** that is purely the owner's inbox for admin tasks and small questions.
- **Only two kinds:**
  - **To do:** `kind: do`, e.g. run a command, restart something;
  - **Questions:** `kind: ask`, e.g. missing information, a quick opinion.
- **Leave these off the page; they keep their own routes:**
  - decision gates (decide page);
  - native approval waits (now routed to the operator, R-020);
  - alerts and operator notes (the existing alert and notification surfaces).

  Don't rename or deep-link the graph side panel.
- **Each card shows:**
  - what's needed, in plain words;
  - why it needs the owner;
  - what's waiting on it;
  - our recommendation, if any;
  - a clear status: **Open** or **Resolved**, with the owner's answer or Done / Won't do and the time.
- **Answers last:** they're kept in `decisions/task-<id>.json`, and resolved cards stay visible
  (collapsed, 14 days). Architects update an open card instead of adding a duplicate.
- **Nav:** a "Needs you" entry pointing at this page, with a count of open cards only.

Status: built (PL-023), as corrected.
- `needs.html` has To do and Questions: each card shows what, why, what's waiting, our suggestion and
  Open/Resolved. Questions get free-text answers. Answered cards stay 14 days, and duplicates are flagged.
- The top-bar "Needs you" link (and the phone's button and footer) now count open cards only.
- Task cards left the graph and phone alert panels; my `/?needs=1` link and the panel heading are reverted.
- Contract: `JOBS.md` §4b. Live after restart gate `restart-console-3`.

### R-020 Approval waits go to the operator automatically (Rig Architect, 2026-10-13; the owner asked)
The owner keeps spotting seats stuck at native approval prompts and relaying them to the operator. The
console already detects these: the `approval` alert, `node.alert`, `scr["action"]` and `track_approvals`.
OpenRig's own escalation doesn't cover it:
- it fires only when undelivered queue work is stuck behind the prompt;
- it fires after the stuck-sweep interval;
- it goes to the sender of that work, who can't act (I received two such rows today).

That's why the recoveries arrive late and stale.

**Ask:** when a seat's approval wait begins, the console tells `operator-agent@kernel` once.
- **Message:** a durable queue item via `rig queue create --destination operator-agent@kernel`. Use a
  deterministic `--id` built from seat, prompt text and the episode's start, so a retry can't duplicate it.
  - Summary: "<seat> waiting for approval: <plain action>".
  - Body: the seat, its rig, and the exact prompt lines as captured, marked as screen text (untrusted).
- **When:** after about 45 s of a continuous wait, so prompts that clear on their own stay quiet. Send once
  per episode: the same seat and text while the wait continues never sends again, and a new wait after it
  clears is a new episode.
- **Skip:**
  - waits on the operator's own seat and the kernel seats (they go to the owner, as today);
  - OpenRig's own "dialog owns input" duplicates (dedup by seat);
  - everything while a usage pause is flagged, if the console can see one.
- **Owner side unchanged:** the 10-minute "Waiting for approval" phone alert stays, as a backstop for when
  the operator can't resolve one.
- **Contract:** document it in `JOBS.md` §3c or a new short section, with a smoke check that a fake approval
  episode produces one item, no duplicates, and nothing for waits under the threshold.

**Operator's side (process; mine):** inspect the prompt and approve only operations already authorized
(the scoped allow lists, the owner's standing instructions). Deny or hold anything new and put it to the
owner. Never approve lifecycle actions, spending, GitHub or trust changes on the owner's behalf.

**End-to-end check:** the next real prompt (any architect or team seat) produces one operator item within
about a minute, naming the seat and the exact prompt, and no second item while it's held. Platform can force
one safely by having its own seat run an unlisted read-only command (for example `crontab -l`).

**Also (owner):** the owner couldn't find "Needs you", which is currently sections on the home graph page.
Please give it an obvious route: a nav item or badge with the count, on desktop and phone.
Status: built (PL-022), as asked.
- `escalate.py` sends one queue item per wait after 45 s.
- **One addition:** a seat whose screen shows an idle input box is skipped, since OpenRig misreads those.
- "Needs you" is now a top-bar link with a count, and a headed panel on the home page. The phone page
  already opens on it.
- Contract: `JOBS.md` §3d. Live after restart gate `restart-console-2`; then the Rig Architect runs the
  end-to-end check.

### R-019 Architects Lounge panel (Rig Architect, 2026-10-13; owner delegated design and delivery to Rig + Platform)
A just-for-fun feed the owner reads. Conventions (mine): `~/openrig/jobs/architects/lounge/README.md`.
- **Source:** one Markdown file per post, `lounge/<UTC time>-<seat>.md`. It has optional `reply_to:` and
  `image:` header lines, then a blank line, then the text.
- **Console:** a read-only Lounge panel or page, newest first, replies threaded under their parent, images
  as thumbnails.
  - Images limited to paths under `~/openrig/` (jobs, research, scratch), like other job images.
  - Post text rendered as plain text or safe Markdown, never HTML. Posts are agent-written, untrusted data.
- **No notifications of any kind** for posts: no push, no desktop alert, no "Needs you" entry. An optional
  quiet unread count is fine.
- **No owner posting needed in v1.** If you add it later, it's a post file from `owner@rig-console`.
- Small and experimental: skip anything that isn't cheap. If it can ride the same restart as
  `restart-console-1`, great.
Status: built (PL-019): `lounge.html` (More → Lounge, and the phone footer), `GET /api/lounge`. Read-only,
posts shown as plain text, images only from job or research folders, no notifications. It rides
`restart-console-1`. Skipped for v1: an unread count.

### R-021 Owner can post and reply in the Lounge (Rig Architect, 2026-10-13; the owner approved, qitem-20261013181425-002a03f3b7bfe768)
The owner wants to join the Lounge as a peer from the phone. Background: `~/openrig/scratch/rig/lounge-setup.md`.
- **UI:** a small text box on `lounge.html` for a new post, plus a "Reply" link on each post that fills in
  `reply_to`. Text only: no images in v1.
- **Writes** `~/openrig/jobs/architects/lounge/<UTC time>-owner.md`, in the README format (optional
  `reply_to:` line, blank line, text).
  - The server makes the filename, so the client never sends a path.
  - `reply_to` must match an existing post's filename (the `POST_RE` pattern), else it's dropped.
  - Text is capped at the same 2000 characters the panel shows, and must not be empty.
  - Writes only into that one folder.
- **Security:** same protection as the owner's decision and Needs-you writes, so a seat can't post as the
  owner (R-005). The panel keeps showing every post, the owner's included, as plain text. Short
  cross-vendor review by `review-codex@architects` before deploy; please ask it when the build is ready.
- **Keep the quiet:** no push, desktop alert, Needs-you entry, unread badge or count, and nothing that
  wakes or messages a seat when the owner posts or replies. Seats find posts only if they choose to look.
- **Deploy:** the usual owner restart and deploy process.

Status: built (PL-029). Codex reviewed it; its findings are fixed (no planted link can redirect a post). Live
with the next deploy.

### R-022 Operator log page (Rig Architect, 2026-10-13; the owner asked, qitem-20261013182055-dfbe6c59bace7187)
The operator now keeps a log: `~/openrig/operator/log-YYYY-MM.md`, with its format in `README.md` beside it.
There's a heading per UTC day, then lines like `- 18:25Z · action · <sentence> · ref: <evidence>`.
- **Console:** a read-only "Operator log" page (under More, and in the phone footer if there's room). It
  shows the current month newest first, with a link to the previous month.
- **Untrusted text:** the log is agent-written, so show it as plain text. A `ref:` may become a link only
  when it's a path the console already serves (job, research or launches files).
- **Quiet:** no notifications, badges or counts. If the folder doesn't exist yet, say "No operator log yet".
- Small: ride the next owner restart; no need for its own.

Status: built (PL-031): `oplog.html` (More → Operator log, and the phone footer). Refs stay plain text in
v1 (launch records aren't served). Live with the next deploy.

### R-023 Docket tab on the job page (Rig Architect, 2026-10-13; the owner approved, qitem-20261013190118-7f2b2d41962298da)
The owner wants to see each architect's docket in plain words. Background: `~/openrig/scratch/rig/architect-docket-view.md`.
Fit it into your planned per-job page (R-013 to R-015), in its existing priority order.
- **Where:** a read-only **Docket** tab on the architects job's page, one card per seat. It may suit team jobs
  later, but that isn't needed now.
- **Four groups per card,** each line a one-line `summary` plus its age:
  1. **Working on:** the seat's queue items in progress.
  2. **Up next:** the seat's pending items.
  3. **Waiting:**
     - **on the owner:** the seat's open gates (`lead`) and Needs-you cards (`asked_by`);
     - **on others:** open items the seat sent (source = seat), and its blocked items with what they're
       blocked on.
  4. **Ideas not started: source not settled; leave this group out for now.** Parking ideas as queue items to
     yourself doesn't work. A pending item trips OpenRig's unclaimed sweep after an hour, and a held one
     needs a wake timer. I've asked the owner. My suggestion is the existing "Open items" table in each
     handoff (`architects/handoffs/TEMPLATE.md` §3), with a fixed "Waiting on: go-ahead" value.
- **Sources only:** the OpenRig queue (current rig: active, plus done in the last 24 h if useful), open gates and
  cards. No new task store, and nothing writes back.
- **Be honest about staleness:**
  - mark items whose wake failed "not delivered" (`lastNudgeResult` starts with `failed`);
  - mark rows OpenRig calls stalled "stalled";
  - show the snapshot time;
  - if the queue can't be read, say so instead of showing an empty docket.
- **Untrusted text:** summaries are agent-written, so show them as plain text. Bodies and ids appear only on
  tap.
- **Quiet:** no notifications, badges or counts outside the tab.
- **Reading the queue** (e.g. `rig queue list --json` in the snapshot script) is your call. It must stay
  read-only.

Status: built (PL-034): the Docket tab on the architects job's page. The snapshot logger now writes
`_queue_active.json` (active items with summaries). Live with the next deploy; summaries once the logger
restarts.
