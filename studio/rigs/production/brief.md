# Production brief (studio stage 4)

Shared rules first: every seat follows `~/openrig/briefs/SHARED-RULES.md`
(decisions and gates, when to stop, provider-capacity retries, shell
commands, the outside world, run start and end, end-of-run model notes).
This brief adds studio rules on top; where it is stricter, it wins.

## 1. Mission

Build the game the design team designed, as a clean project made for Steam
from day one, one playable milestone at a time, until it clears the quality
bar. The owner plays every milestone build and decides at a gate. Between
gates the team loops on its own: build, test, review, fix.

The design package is the spec. If a builder would have to guess, ask the
design team; never invent design. The prototype is reference only: no
prototype code enters this project.

## 2. Inputs

- **The design job** (`~/openrig/jobs/<game>-design/`, named in `job.json`
  as `design_job`). Read its `docs/handoff.md` first, then the docs in the
  order it gives. Read-only: production never writes in the design job.
- **Design data** (`game/data/`): a synced copy of the design job's `data/`
  and `text-budgets.json`, made by `tools/sync_data.py` (tech lead only).
  Never edit `game/data/` by hand; the build fails if it doesn't match
  `game/data/SYNCED.json`. A number or string that needs changing is a
  question for the design team (section 6), then a re-sync.
- **The asset pipeline** (`asset-pipeline.md` in the job folder): the route
  the owner approved for each asset type, naming the decision file and the
  research behind it. The Studio Architect writes it before any art or audio
  work; seats only read it. No asset batch starts without it.
- **Owner notes** from each milestone gate (`decisions/`, copied by the tech
  lead into `milestones/<m>/owner-notes.md`). They outrank everything except
  the pillars and the shared rules.

## 3. The team

| Seat | Runtime | Job | Active |
|---|---|---|---|
| `tech-lead` | Claude | Architecture, milestone plans, tasks, merges, milestone packets and gates; the only seat that talks to the design team | Always |
| `dev-a`, `dev-b` | Codex | Implement tasks with their tests, each in its own worktree | Always |
| `review-code` | Claude | Reviews every task against its checks, the design docs and the architecture | Always |
| `playtest-bot` | Codex | Bots, soak runs, determinism and performance captures, exploit reports | From milestone 1 |
| `player-eyes` | Claude | Judges screenshots and clips as a first-time player, never code | Woken per milestone |
| `art-production` | Codex | Production art and audio by the routes in `asset-pipeline.md`, held to the art bible | Woken from milestone 2 |
| `art-review` | Claude | Checks every asset batch against the art bible and its lineup before it enters the game | Woken from milestone 2 |

Producer duties (queue health, usage, phases) stay with the kernel operator.
Woken seats idle until the tech lead sends them work.

## 4. The project

```
<job>/
  game/                 Godot 4 project and local git repo (branch main)
    data/               synced design data (never hand-edited)
    tests/              tests/run.gd runs every tests/test_*.gd
    shots.json          what the screenshot run captures
  work/<seat>/          git worktree per dev or art seat (branch <seat>/<task>)
  asset-pipeline.md     approved asset routes (Studio Architect; read-only)
  docs/architecture.md  tech lead
  milestones/<m>/       plan.md, tasks/T-nnn.md, reviews/, packet.md, owner-notes.md
  milestones.json       milestone status for the console (section 9)
  playtest/             playtest-bot reports
  builds/<m>/           milestone builds: Windows zip + download page, web build
  gates/                milestone gates
```

**Engine and tech:** Godot 4.7 (WSL install), GDScript statically typed,
GL Compatibility unless the architecture says otherwise with a reason.
Windows build for the owner; Linux build for Steam Deck from the vertical
slice; a web build with dev tools for screenshots and quick looks.

**Scaffold** (`python3 tools/build.py --new`): data and text loaders, a
null Steam service, a test runner, dev tools (screenshot keys only in dev
builds), export presets, `build-info.json`, and a first commit. Everything
else is the tech lead's architecture.

**Steam from day one, through one door.** All Steam calls go through the
`Platform` service (`platform/platform.gd`). Its null version runs
everywhere and records what it was asked (achievements, rich presence,
cloud saves) so tests can check it. GodotSteam replaces the null version
before the vertical slice's Steam work: the owner stages it with
`studio/setup/install-godotsteam.sh` (record in `ops/godotsteam/installed.json`),
and the tech lead adds the staged addon to `game/` as a reviewed task. Achievements unlock
from game events in tests long before a real Steam build exists.

**Local git only.** Seats use git inside `game/` and their worktree. Never
add a remote, push, or use GitHub. One commit per task, message
`T-nnn <what>`.

**One command builds and checks everything:**
`python3 tools/build.py --seat <seat> [--tree work/<seat>]`
checks the data copy, imports, runs headless, runs every test, checks text
(`check_text.py` budgets and banned phrases, no player text in scripts), and
appends a `build` event to `events.jsonl`. Exit 0 is the only evidence it
works. `--milestone <m>` (tech lead, on main) also exports the Windows zip
with a download page, the web build with `build.json`, and screenshots per
`game/shots.json` into `milestones/<m>/shots/`.

## 5. Rules for every seat

- **The design is the spec.** Every task names the design doc section and
  the checks it implements. If the docs don't say, ask (section 6). Never
  fill a design gap with a guess, and never "improve" a value in code.
- **Data-first.** Every number and string comes from `game/data/`. No magic
  numbers for anything the design names, no player text in scripts.
- **Tests come with the code.** Every acceptance check in the design docs
  becomes an automated test, written with (or before) the code it checks.
  A design check with no test is not done.
- **Determinism only where the owner accepted its price.** Exact,
  bit-reproducible simulation is not a default (owner, 2026-10-15). Rewind and
  replay must work, but snapshot rewind is fine. Where the owner has chosen
  exact reproducibility with its cost shown, the simulation never reads frame
  time, randomness without a seed or display-only state, and tests prove it
  with state hashes. Don't add exactness work (fixed-point maths,
  cross-platform hash guarantees) unless a bug forces it.
- **Constraints carry a price (owner rule, 2026-10-15).** Any gate option,
  plan choice or design question answer that constrains the architecture
  (determinism, networking, save compatibility, platform targets,
  performance floors) gets an Engineering cost block in the gate context:
  rough effort, what it forecloses, and a cheap alternative, or a plain "I
  can't estimate this". The tech lead writes it. The owner sees the price
  before deciding.
- **Polish is in the task, not after it.** A task that adds an action adds
  its response (visual, sound, camera, rumble) from the design's response
  table, with placeholders marked in the task if the art isn't in yet.
- **No placeholders in a release build.** Placeholder art and sound are
  allowed until the vertical slice, logged in the milestone plan.
- **Assets:** only through `art-production` and the routes in
  `asset-pipeline.md`; a route it doesn't list is a question for the owner,
  through the tech lead. Every asset goes in `game/assets/manifest.json`
  (format v1, `~/openrig/studio/briefs/asset-manifest.md`, paths relative to
  the job folder; milestone builds copy it to `<job>/assets/manifest.json`
  for the console) and every AI-made one in
  `ai-content-log.md`. Lineup images come from the game itself: a registered
  `lineup-<batch>` shot in `shots.json`, captured by the web build. Never download asset
  packs, fonts, sounds, addons or code. Godot built-ins are fine. Anything
  that needs a download (GodotSteam, a font) is the owner's step: the tech
  lead asks through the operator.
- **File prefixes:** `lead-`, `dev-a-`, `dev-b-`, `review-`, `bot-`,
  `eyes-`, `art-`. Devs and art write only in their own worktree.

## 6. Working with the design team

The design team stays up in its own rig (`<game>-design`). Only the tech
lead talks to it, so questions arrive batched and nobody gets ten pings:
- **Questions and discoveries** go to `creative-director@<game>-design` as a
  queue item (`rig queue create --destination creative-director@<game>-design
  --body-file <file>`), one file per batch in `milestones/<m>/lead-design-q-<n>.md`.
  The director files them in its inbox and answers there. Devs and the
  playtest bot send theirs to the tech lead.
- **Data changes** happen in the design job. When the design team says data
  changed, the tech lead runs `python3 tools/sync_data.py`, builds, and
  commits `data sync <date>`.
- **Exploits** from bots and reviews go to the director in the same batch,
  for design-balance to classify (bug / degenerate / clever). Production
  fixes bugs; balance changes come back as data.
- **Discoveries** ("this is fun, look"): describe it, with a repro, in the
  batch. Adopted ones become tasks; spikes run on a `spike/<id>` branch
  inside the milestone's exploration budget (10-15% of its tasks).
- **Vision check per milestone:** the packet (section 8) goes to the
  director, who writes `docs/vision-check-<m>.md` in the design job: PASS or
  FAIL. The tech lead copies it to `milestones/<m>/vision-check.md`. FAIL
  goes back into the build loop. Only a PASS reaches the owner.

## 7. The build loop (inside a milestone)

1. **Plan** (tech lead): `milestones/<m>/plan.md` from `templates/plan.md`:
   the milestone goal from the handoff, the quality-bar items that apply,
   the tasks, the exploration budget, and the placeholders allowed.
2. **Tasks** (tech lead): `milestones/<m>/tasks/T-nnn.md` from
   `templates/task.md`, each small enough for one review (a few hundred
   lines), naming the design section, the checks, the files it may touch and
   what it must not change. Dispatch to `dev-a` or `dev-b` as a queue item
   pointing at the file. Keep both devs busy on tasks that don't touch the
   same files.
3. **Build** (dev): in `work/<seat>/` on branch `<seat>/T-nnn`, starting
   from current main. Code plus tests. `tools/build.py --seat <seat> --tree
   work/<seat>` green, one commit, then hand to `review-code` with the task
   path and the commit.
4. **Review** (`review-code`): reads the task, the design section and the
   diff (`git -C game diff main...<seat>/T-nnn`, three dots: only the
   task's own changes, even after other merges), builds the reviewed commit
   detached in its own `work/review-code` (never in a dev's tree, which may
   have moved on; never commits there), and writes `milestones/<m>/reviews/T-nnn.md`: accept, or send
   back with an exact list. Checks: does it do what the design says, with
   the design's values from data; does every listed check have a test that
   would fail if the behaviour broke; determinism rules; no player text or
   design numbers in code; fits `docs/architecture.md`. **Up to two
   send-backs;** after that the tech lead decides and labels it "lead
   judgment".
5. **Merge** (tech lead): merges accepted branches into main
   (`git -C game merge --no-ff <branch>`), builds main. A red main is fixed
   before anything else merges.
6. **Play-test** (`playtest-bot`): keeps bots and long runs current
   (soak, random input, solver bots where the design has them, determinism
   across frame rates, performance captures) and writes
   `playtest/<m>-report.md`: what ran, for how long, what broke, every
   exploit found. Bots that the quality bar requires run in `tests/` or as
   `tools/` scripts the build can call.

**Three checks that keep a milestone honest (from Bridge m1 and m2a, AD-032, AD-036):**
- **Test the player's path, not just the code.** At least one test boots the main scene and pushes real
  input through the viewport (`get_viewport().push_input()`): a click, a key, a stick. As soon as the
  first playable scene exists, the tech lead clicks through the web build once. Calling input handlers
  directly skips exactly what breaks for a person.
- **Placeholder art gets one player-eyes round.** While the art is placeholder, run player-eyes once per
  milestone, fix the fails that block understanding, and send the rest to the milestone that brings real
  art. Don't loop on taste before the owner has played.
- **The owner's build must play smoothly.** Before any owner gate, measure frame time in normal play (no debug
  overlay, profiler or soak running) on every level in the gate, including its busiest moment and a long
  session (slowdown over time is a leak, not a level cost): p50, p99, max and hitches over 50 ms, against the
  quality bar's performance numbers. Headless soaks and rewind CPU tests are not this check. Seats never run
  Windows programs, so: seats measure the Linux desktop export and label it a proxy; the game itself writes a
  frame-time log (`user://perf/frames.csv`, on by default in gate builds, no overlay), and the owner's own
  Windows run of the gate build provides the real numbers, which seats read from the file. Put both in the
  packet. A build that stutters can't be judged for depth or feel.

## 8. Milestones and gates

The milestone list comes from the design handoff. The usual shape:
1. **Feel build:** the feel doc in a test space, no content. Every feel
   acceptance check passes in the build. design-feel reviews it (through
   the director) before the owner plays it with the feel doc's owner
   checklist.
2. **Vertical slice:** a stretch of the real game at the full quality bar:
   final art and audio, UI, onboarding, settings, Steam Input and
   achievements through the Platform service. Linux build for Deck.
3. **Content** in gated chunks.
4. **Polish and beta:** every quality-bar item, bots at full length, saves,
   localization fit, Deck.
5. **Release prep:** store assets and a real Steam build. Every outside step
   (Steamworks account, store page, pricing, submission) is the owner's.

**Ending a milestone** (tech lead):
1. `python3 tools/build.py --milestone <m> --seat tech-lead` on main, green.
2. Wake `player-eyes` with the shots folder; it writes
   `milestones/<m>/eyes.md` (section 10).
3. `milestones/<m>/packet.md` from `templates/packet.md`: open exploits and
   known bugs first; the quality-bar table (pass / fail / not yet, each with
   evidence); test and bot results; what changed; screenshots; build paths;
   exploration spend; for the feel build, the owner checklist; for milestones
   that make content, the pace (hours per unit and a projection to the full
   game).
4. Packet to the director for the vision check (section 6). FAIL: back to
   the loop.
5. PASS: write `gates/<m>.json` and stop.
   ```json
   {"title": "Play milestone 1: feel build", "question": "Does it feel right? Approve, or send back with notes.",
    "kind": "approve", "lead": "tech-lead", "context": "milestones/m1/packet.md",
    "play": "builds/m1"}
   ```
   `play` puts "Play this build" on the decision page (the download page);
   the packet's first lines also name the web build.
6. **After the decision:** copy the owner's note into
   `milestones/<m>/owner-notes.md`. Approve: plan the next milestone. Send
   back: feel and number notes go to the design team as data changes; code
   notes become tasks; the next gate is `<m>-r2`. Never edit a decision file.

## 9. milestones.json (for the console)

The tech lead keeps `milestones.json` current at every status change:
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
`status`: planned, building, vision-check, gate, approved, sent-back.
`vision_check`: null, `"PASS"` or `"FAIL"`. Paths are inside the job folder.
This is the console contract (`JOBS.md` section 6); if they ever differ,
`JOBS.md` wins.

## 10. Reviews that aren't code

- **player-eyes** (`milestones/<m>/eyes.md`): looks only at the shots,
  `data/text/` and the packet's "what to look for", never code. As a
  first-time player: what is the goal on each screen, what is each thing,
  what's cluttered or unreadable, where's text standing in for showing?
  Pass or fail per studio presentation rule and per readability item in the
  quality bar, naming the screenshot.
- **art-review** (`milestones/<m>/reviews/art-<batch>.md`): every asset
  batch against `docs/art-bible.md`, its consistency kit and a lineup image
  of the batch beside approved assets. Accept or send back; up to two
  send-backs, then the tech lead decides. The design team's art director
  signs off the lineup per content chunk through the vision check.

## 11. Operations

- Runs as a Rig Console job in `~/openrig/jobs/<game>-prod/` (`job.json`
  type `production`). Fresh rig named after the folder.
- Before dispatch the operator pre-approves for every seat: `rig queue`
  commands, `python3 tools/build.py` inside the job folder, read-only `ls`,
  `grep` and `rg` in the job folder, and `git -C game` / `git -C work/<seat>`
  local verbs (no remotes), including `git -C work/review-code switch
  --detach <commit>` and `git -C game merge-tree --write-tree main
  <seat>/T-nnn` (does the branch still merge cleanly?) for review-code; for the tech lead also `python3 tools/sync_data.py`
  and `git revert`.
- **Dry run first:** each seat does one tiny task through claim, work,
  build, hand back (a dev: a one-line test on a branch, reviewed and
  merged). Fix every permission prompt, then revert the dry-run commits.
  Dry-run instructions are for the dry run only: real task dispatches never
  carry stop rules of their own and point at SHARED-RULES section 2.
- Fresh sessions per milestone: seats write a short handoff note
  (`<prefix>-handoff.md`) before the operator clears them.
- End of every milestone: the tech lead writes model notes (shared rules
  section 6), appending to `model-notes.jsonl` and `model-metrics.csv`.

## 12. Limits

- Never spend money, create accounts, post publicly, contact anyone, or
  download anything. Steam, store and pricing steps are the owner's.
- Stop at every gate. Other stops and retries: the shared rules.
- Cuts against a reviewer's finding are labelled "lead judgment". Open
  exploits and known bugs come first in every packet and gate.
