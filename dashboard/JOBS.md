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
- `rig`: which OpenRig team works on it (otherwise guessed from the folder name).
- `writers`: file-name prefix → seat name, so file pops land on the right agent. Without it, files named
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

## What stays job-specific
Views built around one job type read that type's own files. Today, the Niche board reads research
`niches.json`. Planned next: a validation view (`validation.json`). Other job types get their own
view when they need one; the graph, feed and replay work for all of them from day one.

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
- `kind`: `choose` (pick options; use `pick` for an exact count, or `min`/`max`) or `approve`
  (approve, or send back with a required note; e.g. pillars doc, art bible, a milestone).
- Option `id`s: letters, numbers, `.`, `_`, `-`. `image`, `file`, `context` and `play` are paths inside
  the job folder; anything outside it is ignored. Images show as cards and can go full screen.
- `lead`: the seat to tell (seat name only). Default: the team's lead.
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

## 5. Playable builds
Put each web build in its own folder with an `index.html`: `<job>/builds/<name>/index.html`
(or set `"builds": "export/web"` in job.json). It shows on the **Play builds** page, and a gate
option with `"play": "builds/<name>"` gets a Play button.
- Godot 4: use the Web export preset. Both threaded and single-threaded exports work; the console sends
  the cross-origin isolation headers threaded builds need. Keep each build under ~100 MB so it loads on a phone.
- The PC must be on and the dashboard running; your phone loads the build over Tailscale.
