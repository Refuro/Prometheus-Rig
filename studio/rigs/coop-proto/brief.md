# Co-op prototype sprint brief (2-4 players, Windows builds)

## 1. Mission

Turn each chosen co-op pitch into a small online prototype for 2-4 friends
that shows **three beats** (early, middle, late), export it for Windows, and
put every build in front of me through a Rig Console gate. I play each one
with 2-3 friends over Tailscale, then pick.

A prototype answers three questions: do friends cause each other's funniest
moments, does it get deeper, and can one strong player carry the group? The
first two must be yes; the third must be no.

Prototypes are throwaway. The real game is built from scratch later (with
Steam integration and a proper architecture from the start), so never spend
effort making prototype code reusable. It's a question, not a demo. Grey boxes, no menus, no art, no
sound unless sound is the mechanic, no save system, no polish. A toy that
answers its question in two ugly minutes beats a pretty one that doesn't.

## 2. Inputs

- `specs/proto-spec-<id>.md`: one page per prototype, written by the
  friendslop room (roles, the three beats, the carry exploit to close, the
  netcode plan). The spec is the contract. The original pitch cards are in the
  pitch-room job folder if a builder needs the "why".
- Waves of three: proto-lead assigns specs to build-a, build-b, build-c in
  the order of the gate decision. A builder takes its next spec only after
  its current toy is accepted.

## 3. Technical rules

- **Engine:** Godot 4 (the version installed in WSL), GDScript, statically
  typed. Renderer GL Compatibility (runs on friends' older PCs too).
- **Start every prototype with the scaffold:**
  `python3 tools/build.py <id> --new` creates `protos/<id>/` with a
  `main.gd` that already hosts and joins over ENet (port 24565, up to 4
  players), a Host / Join-by-address menu, Windows and Linux export presets,
  and `ProtoUI` (title card + hints). Don't hand-edit `export_presets.cfg`.
- **Networking pattern: host-authoritative.** Clients send *inputs* to the
  host (`submit_input`); the host simulates everything (`_simulate`) and
  broadcasts *state* every physics tick (`receive_state`); clients only draw
  it. Extend `_simulate`, `_state_snapshot` and `_apply_snapshot` with the
  game. Keep synced state small (positions, a few flags, discrete events);
  no client-side physics that affects gameplay. If the spec's netcode plan
  needs something else, say so in the notes before building it.
- **Sync test:** the game's important objects must appear in the report
  (`_write_report` state) so `tools/net_test.py` can compare them across
  peers, not just player positions. Bots (`--bot`) must exercise the core
  verb (e.g. trigger the handoff or the swap), not only walk.
- **Build and verify with one command:**
  `python3 tools/build.py <id> --seat <seat>` imports, runs headless, runs
  `tests/smoke.gd`, runs `tools/net_test.py` (headless host + 2 bot clients
  on one machine must end in the same state), exports a Windows build to
  `builds/<id>/<id>-windows.zip` with a download page
  `builds/<id>/index.html`, logs to `protos/<id>/build-log.txt`, and
  appends a `build` event to `events.jsonl`. It fails while `ABOUT.txt` has
  `[TODO]` lines. **Exit 0 is the only evidence a build works.** While
  iterating, `--no-net --no-export` is faster; hand-backs need the full run.
  Before hand-back also run `python3 tools/net_test.py <id> --clients 3`.
- **Smoke test required:** `protos/<id>/tests/smoke.gd` (extends
  `SceneTree`) checks the core rule in code. Quit 0 on pass, 1 on fail.
- No addons (GodotSteam comes in production, not here), no downloaded assets,
  no voice chat in the prototype (friends use Discord; the spec says how the
  game would use proximity voice later). Keyboard + mouse; controller is a
  bonus. Primitive meshes and flat colours for everything visible; each
  player a distinct colour.

## 4. Done means

The owner was confused by earlier prototypes: they explained controls but
not the game. Every prototype must explain itself.

For each prototype, all of:
1. `python3 tools/build.py <id>` exits 0 (net test included),
   `builds/<id>/<id>-windows.zip` and its download page exist, and
   `tools/net_test.py <id> --clients 3` passes.
2. **Title card:** `protos/<id>/ABOUT.txt` shows on launch (ProtoUI): the
   title, what the game is in a sentence or two, how you win and lose, what
   **every** interactable object does, and the controls. H reopens it.
3. **Contextual hints:** whenever the player picks up, touches or unlocks
   something new, `ui.hint("...")` says what it's for ("Drop the cheese near
   the elephant to lure it"). No object without a purpose on screen.
4. **Three beats:** on the host, keys `1`, `2`, `3` jump everyone to the
   spec's early, middle and late beat. Each beat is a small hand-made level or situation; the late
   beat must show something a first-minute player couldn't do yet. The
   title card says the beats exist.
5. **The spec's carry exploit is closed:** one strong player can't solve a
   beat while the others watch (the spec names how). If it can't be closed,
   say so in the notes.
5b. **Works at 2 players and at 4.** Note in the build notes how each beat
   changes with player count.
6. A restart key (`R`).
7. `protos/<id>/HOW-TO-PLAY.md`: starts with **what the game is** (one
   sentence), then the goal, then controls. Max 5 lines. The gate links it.
8. `protos/<id>/build-<letter>-notes.md`: built, cut, known bugs, what's
   synced, and the builder's honest answers: does the rule make friends
   cause each other's chaos, and does it deepen across the beats?

Time box: **one working session per prototype** (about 6 hours of agent
work; networking and three beats take longer than a single-player toy). If the core rule isn't working by then, stop, make whatever works
playable, and say so in the notes. A failed question is a valid answer.

## 5. How the team works

- **proto-lead (Claude):** dispatches specs, reviews, writes the gate. Does
  not build. Keep messages short; Claude usage is the scarce budget.
- **depth-critic (Codex):** reviews each accepted-for-review toy's code
  for exploits before the lead's verdict (see below). Does not build.
- **build-a, build-b, build-c (Codex):** one prototype at a time each. Work
  only inside `protos/<your-id>/`, plus `builds/<your-id>/` via the build
  tool. Never touch another builder's folders.

Exploit review (depth-critic, per toy, written to `reviews/depth-<id>.md`,
before the lead's review): read the code and the spec like a lazy, clever
group, and like the one expert friend who wants to do everything. List every
way to skip or trivialize each beat, every way one player can carry the
rest, and any gameplay that's simulated on a client instead of the host (e.g. "you can place
surfaces anywhere, so beat 3 is a staircase"), and whether the spec's named
exploit is really closed. Severity per item: blocks the beat / weakens it /
cosmetic. The lead sends blocking items back to the builder.

Review (lead, per toy, written to `reviews/lead-<id>.md`):
- Does `build.py` pass? (Run it yourself; don't trust the hand-back.)
- Read the smoke test and the code that implements the core rule. Does the
  toy actually implement the spec's rule, or a safer neighbour of it?
- Is anything out of scope creeping in (menus, art, extra modes)?
- Does ABOUT.txt explain the game, including Host/Join, to a stranger? Does every object get a hint?
- Does the net test cover the game's real state, and do the bots use the core verb?
- Do the three beats actually escalate, or are they the same beat with more stuff?
- Are the critic's blocking exploits fixed?
- Verdict: **Accept**, or **Send back once** with an exact list. After one
  send-back, accept with notes; don't loop.
The lead cannot play the build. Say what you couldn't judge.

## 6. Funnel

1. **Dry run.** Lead scaffolds a throwaway `protos/dry-run/` with
   `build.py dry-run --new`, a builder claims it, fills `ABOUT.txt`, adds one
   moving square and a trivial `tests/smoke.gd`,
   runs `build.py dry-run --seat <seat>` green, hands back; lead re-runs it.
   Confirm no step stops for approval (including the net test, which
   launches several Godot processes) and that `builds/dry-run/` shows on the
   console's Play builds page. Depth-critic writes a one-line
   `reviews/depth-dry-run.md`. Fix any prompt first, then delete the dry-run
   files.
2. **Waves.** Dispatch up to three specs at once. Each hand-back goes to
   depth-critic first, then the lead's review. As a builder's toy is
   accepted, dispatch its next spec.
3. **Playtest note.** As each toy is accepted, append one line to
   `events.jsonl` (`{"kind": "playtest-ready", "seat": "proto-lead", "text": "<id> ready for a friends session"}`),
   so the owner can line up a session; the owner's session notes, if any,
   arrive through the gate.
4. **Gate.** When every spec is accepted (or honestly failed), write
   `lead-summary.md` and `gate.json`, then **stop and wait**. Never ask for
   the decision in chat and never write a decision file.

Gate format (see `~/openrig/dashboard/JOBS.md` section 4):
```json
{
  "title": "Play the prototypes and pick",
  "question": "Which prototype should become the game? Pick one, or two to compare further.",
  "kind": "choose", "min": 1, "max": 2,
  "lead": "proto-lead",
  "context": "lead-summary.md",
  "options": [
    {"id": "x-04", "title": "Working Title", "summary": "One paragraph: what the game is, the friends moment to look for, how the three beats escalate at 2 vs 4 players, the critic's remaining carry exploits, known bugs.", "file": "protos/x-04/HOW-TO-PLAY.md", "play": "builds/x-04"},
    {"id": "none", "title": "None of these: back to the pitch room", "summary": "Add notes on what felt closest to fun."}
  ]
}
```
`lead-summary.md`: one short section per prototype (question, builder's
answer, lead's verdict, couldn't-judge list, known bugs), under 800 words.

5. **After the decision** (`decisions/<gate-id>.json` plus a `rig send`):
   write the owner's choice and notes into `lead-decision-notes.md`, then
   stop. Stage 3 is a separate rig.

## 7. Operations

- Run from `~/openrig/jobs/proto-N/` (a Rig Console job; `job.json`
  present; rig name = folder name). Fresh rig. Don't reuse pitch-room seats.
- Before dispatch, the operator pre-approves for every seat: `rig queue`
  commands and `python3 tools/build.py` inside the job folder. Lifecycle
  commands still ask.
- File prefixes: `lead-`, `depth-`, `build-a-`, `build-b-`, `build-c-`.
- No `$`, backticks or pipes in shell text. Use `--body-file` for free text.
- The lead parks its goal row on the rows it dispatches.
- The net test runs several headless Godot instances on a free local port
  per run, so builders can test in parallel.
- Optional: append progress events to `events.jsonl`
  (e.g. `{"kind": "review", "seat": "proto-lead", "text": "b-06 accepted"}`).
- The operator does not monitor the run; it acts only when messaged.

## 8. Limits and stop rules

- Never: spend money, create accounts, post publicly, contact anyone, or
  download assets, addons or code from the web.
- Stop and wait at the gate.
- If usage-limit warnings appear: stop, save progress (every toy should
  have a green build by then), report.
- If lead and builder disagree twice on the same point: write both
  positions into the review file and let the owner decide via the gate.
