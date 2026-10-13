# Plugging any kind of work into Rig Console

The console isn't tied to research. Anything a team works on is a **job**: a research run, a validation
campaign, a game pitch room, a prototype sprint, a production milestone, something else entirely.
Every job gets the live graph, the activity feed and replay for free.

## 1. Make a folder
Put the job's working folder under a watched root. Defaults (edit `dashboard/jobs.json` to add more):
- `~/openrig/research/<name>`: research runs (type `research`)
- `~/openrig/jobs/<name>`: everything else (type `general`)

A game repo can live anywhere: add its parent folder as a root with its own type, e.g.
`{"root": "~/games", "type": "game"}`.

## 2. Optional: describe it with job.json (in the job folder)
```json
{
  "type": "prototype",
  "rig": "studio-proto-1",
  "title": "Gravity toy",
  "writers": {"build": "builder-a", "review": "reviewer"},
  "watch_depth": 3
}
```
- `type`: a free label shown on the job's gates, e.g. `research`, `validation`, `pitch`, `prototype`,
  `design`, `production`.
- `rig`: which OpenRig team works on it (otherwise guessed from the folder name).
- `writers`: file-name prefix or top-level folder → seat name (e.g. `"pitches": "pitcher-a"`), so file
  pops land on the right agent. Without it, files named
  `<seat-word>-...` are matched to that seat, and everything else is credited to the lead.
- `watch_depth`: how many folder levels to watch for new files (default 2). Build, cache, `.git`,
  `node_modules` and `.godot` folders are always skipped.

## 3. Optional: log your own events (events.jsonl in the job folder)
Append one JSON object per line. Any agent, script or bot can do this; no server access needed.
```json
{"kind": "playtest", "seat": "playtest-bot", "text": "Level 3 solvable in 41 moves", "data": {"level": 3, "moves": 41}}
{"kind": "build", "text": "Milestone 1 build exported"}
{"kind": "email_sent", "seat": "sender", "text": "Batch 2: 25 emails", "data": {"count": 25}}
```
- `kind`: lowercase letters, numbers, `-` or `_` (up to 32 characters). Required.
- `seat`: the seat's name (e.g. `builder-a`); optional. `text`: one line, up to 300 characters.
- `data`: optional details for job-specific views later. `ts`: optional (unix seconds or ISO time).
Bad lines are skipped. The console remembers how far it has read.

**Model notes** are not events: at the end of a run the lead writes `model-notes.jsonl` and
`model-metrics.csv` in the job folder (`briefs/SHARED-RULES.md` §6, format in `models/HARVEST.md`). The
Models page lists lines the Model Architect hasn't harvested yet.

## What stays job-specific
Views built around one job type read that type's own files. Today, the Niche board reads research
`niches.json`. Planned next: a validation view (`validation.json`). Other job types get their own
view when they need one; the graph, feed and replay work for all of them from day one.

## 3b. Launch records (written by the operator, not by the team)
When the operator starts a team on a job, it writes `~/openrig/launches/<job>.json`:
```json
{"job": "proto-2", "folder": "/home/<you>/openrig/jobs/proto-2", "rig": "proto-2", "lead": "proto-lead",
 "launched_at": "2026-10-12T18:40:00-07:00",
 "seats": {"proto-lead": {"runtime": "claude-code", "model": "claude-opus-5-5", "version": "as shown"},
           "build-a": {"runtime": "codex", "model": "<name>", "version": "<as shown, or unknown>"}}}
```
The console uses it to decide which team gets your decisions: its `rig` and `lead` win over the job
folder's own `job.json` and `gate.json`, which the team can edit. It's ignored unless `folder` is the job's
real folder. `seats` (optional) records which model the operator put in each seat; the console shows it
on agent cards when OpenRig doesn't, and the Model Architect uses it as evidence. Without a record, the console pins the rig it first saw for the job, and alerts if `job.json`
later claims another one. A job's name is always its folder name.

## 3c. Notifying the owner (the operator only)
The operator can send the owner a note. Write `~/openrig/launches/notify/<id>.json`:
```json
{"title": "Bridge production team is ready", "body": "Studio Architect confirmed. Next: your go.", "priority": "high"}
```
- `<id>`: letters, numbers, `.`, `_`, `-` (64 at most). Use a new id for each note, e.g. `bridge-ready-2026-10-13`.
- `title` (required, 160 characters shown), `body` (optional, 1000), `priority`: `high` (default) or `default`
  (quieter). `url` (optional): a console page such as `/decide.html`; anything else becomes `/graph.html`.
- **What happens**, within about 10 s: the note shows under "Needs you" on desktop and phone, and is pushed
  to the owner's phone once. Then the console sends the operator a receipt (`From: console@rig-console`):
  "pushed to the owner's phone", or "not pushed: <why>". The note is shown anyway. The receipt confirms the
  push service took it, not that the owner read it.
- **Never twice:** each id is handled once, ever. Rewriting the file doesn't send it again.
- **Limits:** five pushes an hour; past that, notes are shown in the console only and the receipt says so.
  A note disappears 24 h after it was written, or when the owner dismisses it.
- **No receipt within a minute?** The console may be down or not yet updated. Don't write another id; tell
  the owner through the usual route.
- Only the operator writes here. Team seats never do (`SHARED-RULES.md` §1: nobody else writes in
  `~/openrig/launches/`).

## 3d. Approval waits reach the operator (automatic, R-020)
When a team or architect seat has waited at a native approval prompt for about 45 s, the console puts one
item in the operator's queue (`From: console@rig-console`, summary "<seat> waiting for approval: <action>").
The body has the seat, its team and the prompt's last screen lines, marked as untrusted screen text.
- **One item per wait:** a changed prompt in the same wait doesn't send again. A new wait after it clears is
  a new item. The item id is built from the seat, the wait's start and the prompt, so retries never duplicate.
- **Skipped:** the kernel's own seats; seats stopped at a usage limit; seats whose screen shows an empty input
  box (OpenRig sometimes misreads those as prompts).
- The owner's "Waiting for approval" notification after 10 minutes stays as the backstop.
- What the operator may approve is the Rig Architect's process (`SHARED-RULES.md`), not this contract.

## 3e. Replying to the owner's messages by id (the operator and architects, PL-025)
Each message the owner sends from the console starts `Message from the owner [msg <id>]`. The id looks like
`m-20261013112233-ab12`. The message ends with the exact file to write, for example:
```
~/openrig/launches/replies/m-20261013112233-ab12.json
{"id": "m-20261013112233-ab12", "text": "Your answer, as plain text.", "at": "2026-10-13T11:25:00Z"}
```
- **Who writes where:** the operator in `~/openrig/launches/replies/`; architects in `replies/` inside their
  own job folder (`~/openrig/jobs/architects/replies/`). Nobody else, and no other folder, counts. Team seats
  get the id but answer on their screen.
- **Fields:** `id` (required, the exact id from the message, matching the file name), `text` (required, up to
  20,000 characters, shown as plain text), `at` (optional ISO time; else the file's time).
- **Follow-ups:** write `<id>-2.json`, `<id>-3.json`… They show under the first reply; nothing is replaced.
  Rewriting a file updates that reply.
- **Pairing is by id only.** A file whose id the console never issued, whose `id` field doesn't match its
  name, or that answers another seat's message is ignored and logged once. It's never shown.
- **What happens:** within about 10 s the reply shows beside the exact question on the Messages page, with
  both times. Nothing is pushed and no seat is woken.
- **Screen text** is still read as a fallback, but it's shown apart, labelled "from the screen (not a
  confirmed reply)", and hidden once a reply file arrives.
- The id is a reference, not proof of who sent the message (`SHARED-RULES.md` §1).

## 4. Ask the user to decide something: gates
Write `gate.json` in the job folder (or several files in `<job>/gates/<id>.json`). It appears in
"Needs you" on the phone and desktop, sends a phone push if ntfy is set up, and opens a decision page.
```json
{
  "title": "Pick 3 pitches",
  "question": "Which three should we prototype?",
  "kind": "choose",
  "pick": 3,
  "lead": "room-lead",
  "context": "pitches/README.md",
  "options": [
    {"id": "p01", "title": "Gravity Gardener", "summary": "One paragraph.",
     "image": "art/p01.png", "file": "pitches/p01.md", "play": "builds/p01"}
  ]
}
```
- `"max_soft": true` (optional, `choose` only): the user may pick more than `max`/`pick` after a
  confirm. The decision then records `"over_max": true` and the `max` it went over.
- `kind`: `choose` (pick options; use `pick` for an exact count, or `min`/`max`) or `approve`
  (approve, or send back with a required note; e.g. pillars doc, art bible, a milestone).
- Option `id`s: letters, numbers, `.`, `_`, `-`. `image`, `file`, `context` and `play` are paths inside
  the job folder; anything outside it is ignored. Images show as cards and can go full screen.
- `lead`: the seat to tell (seat name only). Default: the team's lead.
- `play` (optional, top level): one build for the whole gate, e.g. `"play": "builds/m1"` on a milestone's
  approve gate. The decision page shows a Play button for it.
- **The answer:** `<job>/decisions/<gate-id>.json` (and a readable `.md`). The gate closes when the
  `.json` exists. The lead gets a `rig send` pointing at it. Don't edit or delete decision files;
  to ask again, open a new gate with a new id.

### Writing a good gate
- Keep `question` to one or two sentences. Put the detail in a Markdown `context` file: the console shows
  it rendered on the decision page (headings, tables, lists, quotes).
- Lead with what needs deciding: a short table of decisions (ID, decision, recommendation, risk) works well.
- Mention supporting files as paths from the job folder, e.g. `plan/offer.md`, either in backticks or as
  Markdown links. The user can open them in an in-page reader, so link the files they should review.
  Bare names like `offer.md` are read relative to the context file's folder.
- No HTML in these files; it is shown as plain text.

### Closing gates that no longer apply
The user can close a gate without deciding (decision file with `"verdict": "closed"`). Treat it as
"handled elsewhere": don't act on it. When the user decides something directly in chat, or a team is
dropped, the operator closes that job's open gates the same way: write `<job>/decisions/<gate-id>.json`
with `"verdict": "closed"` and a `note` saying where the decision was made.

## 4b. The owner's "Needs you" page: to-dos and questions (architects only)
The **Needs you** page (`needs.html`, in the top bar and on the phone) is the owner's inbox for small things
only they can do or answer. For one, an architect writes `~/openrig/jobs/architects/tasks/<id>.json`:
```json
{"kind": "do", "title": "Get a PO box for StyleSteady", "action": "Rent a PO box and add its address to ~/.config/validation-1/.",
 "asked_by": "arch-rig@architects", "why": "Emails need a postal address that isn't your home.",
 "blocks": "sending the first emails", "recommend": "A UPS Store box is quickest.", "details": "plan/po-box.md"}
```
- `kind`: `do` (run a command, restart something: the owner taps **Done** or **Won't do**, with an optional
  note) or `ask` (missing information or a quick opinion: the owner types an answer and taps **Send**, or
  **Skip**). Default `do`.
- `title`: 8 words at most, plain English. `action`: one sentence that says exactly what's needed. `asked_by`:
  your seat.
- Optional, and worth filling in: `why` (why it needs the owner), `blocks` (what waits on it), `recommend`
  (our suggestion). Also `details` (a path in the architects job folder, shown as a link) and `urgent: true`
  (pushes to the phone once; otherwise no push).
- **Commands for the owner go in `steps`** (the owner's convention, 2026-10-13): one exact, complete command
  per step, where to run it, and what confirms it worked. The page shows each with a Copy button:
  ```json
  "steps": [{"where": "Ubuntu window (not tmux)", "run": "cd /mnt/c/.../OpenRig", "check": ""},
            {"where": "Ubuntu window", "run": "git status --short -- dashboard/", "check": "Lists only files you expect"},
            {"where": "Console", "say": "Sign in again on your phone.", "check": "Decisions page lets you decide"}]
  ```
  Use `run` for a command or `say` for a plain instruction. For git, review before committing
  (`git status`, `git diff --staged`) and never stage everything blindly. Put long background in
  `details`, not in the steps.
- **Limits** (longer text is cut, ending in "…"): `title` 100 characters, `action` 600, `why` 400, `blocks`
  300, `recommend` 1000; up to 20 `steps`, each `where` 80, `run` 1000 (never cut: a longer step is
  refused rather than shortened, so write it as two), `say` 400, `check` 300.
- **Answers:** the console writes `decisions/task-<id>.json` (and `.md`) with the whole card plus `result`
  (`done`, `wont`, `answered`, `skipped`), `answer` and `note`, then tells `asked_by`. Read it, act on it,
  then delete the task file. The answered card stays visible under "Done recently" for 14 days.
- **No duplicates:** before writing, check `tasks/` for an open card about the same thing and edit that one
  instead. Two open cards with the same title are flagged on the page.
- **What stays off this page:** choices between options are gates (section 4, the Decisions page); approval
  waits go to the operator (section 3d); alerts and operator notes keep their own places. Team seats don't
  write cards; their needs reach the owner through their architect. Don't use gate ids that start with
  `task-`.

## 5. Playable builds
Put each web build in its own folder with an `index.html`: `<job>/builds/<name>/index.html`
(or set `"builds": "export/web"` in job.json). It shows on the **Play builds** page, and a gate
option with `"play": "builds/<name>"` gets a Play button.
- Godot 4: use the Web export preset. Both threaded and single-threaded exports work; the console sends
  the cross-origin isolation headers threaded builds need. Keep each build under ~100 MB so it loads on a phone.
- Builds are served from their own port (8801, `PLAY_PORT`), a separate origin from the console, so a build's
  code can't use the console. Play links go through `/go/play/...`, which redirects there. The PC must be on
  and the dashboard running; the phone reaches builds through Tailscale Serve on port 8443.
- **Name it (optional):** put a `build.json` next to `index.html` so the Play page shows a real name, not
  just the folder name:
  ```json
  {"title": "Pocket Countryside", "pitch": "Roll up strips of turf to bring villages closer.",
   "controls": "Drag a strip end to roll. C sends the cart. Z undoes, R restarts.",
   "judge": "Is rolling the land readable without explanation?", "bugs": "Hover order can lag."}
  ```
  Without it, the page falls back, in order, to: a gate option whose `play` points at the build; then
  `specs/proto-spec-<name>.md` (its `# Proto spec: <id> <Title>` line, "What it is" and "Controls"); then
  `lead-summary.md` (its `## <name> <Title>` section, "Question", "Couldn't judge", "Known bugs", "Watch out").

## 6. Production milestones: milestones.json (R-015, adopted from the Studio Architect's AD-027)
A production job keeps `<job>/milestones.json` current at every status change:
```json
{"game": "A Bridge Goes Walking", "design_job": "bridge-design",
 "milestones": [
  {"id": "m1", "title": "Feel build", "status": "building",
   "plan": "milestones/m1/plan.md", "packet": "milestones/m1/packet.md",
   "build": "builds/m1", "download": "builds/m1/game-windows.zip",
   "tests": {"passed": 0, "failed": 0, "at": null},
   "quality_bar": {"pass": 0, "fail": 0, "not_yet": 0},
   "exploits_open": 0, "vision_check": null, "gate": null}]}
```
- `status`: `planned`, `building`, `vision-check`, `gate`, `approved` or `sent-back`. `vision_check`: `null`,
  `"PASS"` or `"FAIL"`. `gate`: the gate id once one is open (e.g. `"m1"`, then `"m1-r2"`).
- Paths are inside the job folder. `tools/build.py` fills `tests` and `build`; the tech lead fills the rest.
- The milestone's gate is an approve gate with a top-level `"play": "builds/m1"` (section 4).
- The console doesn't show this file yet (R-015's view is still to build). Writing it now means the view
  works from the first milestone.
