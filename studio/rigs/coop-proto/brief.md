# Co-op prototype sprint brief, v2: "readable together" (2-4 players)

Shared rules first: every seat follows `~/openrig/briefs/SHARED-RULES.md`
(decisions and gates, when to stop, provider-capacity retries, shell
commands, the outside world, run start and end, end-of-run model notes).
This brief adds studio rules on top; where it is stricter, it wins.

## 1. Mission

The first co-op round had good heads but the owner couldn't read what was
going on: what each player is, what the group is trying to do, and what one
friend needs from another. This round rebuilds the same ideas so each one
**feels like a small co-op game**: within seconds every player knows which
one they are and what the group's goal is, the group learns one idea at a
time by doing it, and the moments where friends need each other (or ruin
each other's plans) are visible on screen, not explained in text.

A prototype still answers three questions: do friends cause each other's
funniest moments, does it get deeper, and can one strong player carry the
group? The first two must be yes; the third must be no.

Prototypes are throwaway (production is a clean build with GodotSteam later),
so keep the code simple. Effort goes into what players see: readability,
pacing, feedback.

## 2. Inputs

- `specs/proto-spec-<id>.md`: the previous round's spec, unchanged.
- `inputs/<id>/`: the previous round's build notes, reviews, HOW-TO-PLAY and
  ABOUT for that prototype, plus its old project (`inputs/<id>/old-proto/`),
  which a builder may reuse for netcode and rules.
- `owner-notes.md`: the picks for this round and what the owner said after
  playing the previous one. It outranks everything except the shared rules.
- Step 0 (proto-lead): for each prototype, write `specs/v2-<id>.md`, one
  page: the game in two sentences a stranger understands; the **teaching
  sequence** (section 4) with what each stage teaches and what the group
  must do; **who is who** (how each player and any role is shown); **the
  together moment** of each stage (what one player needs from another, and
  how the screen shows it); the readable look of every object (section 5);
  the owner's notes and exactly how this version answers each one; and the
  carry exploit that must stay closed. The builder builds from v2, not the
  old spec.

## 3. Picks and waves

The picks and their order are at the top of `owner-notes.md`. Wave 1: the
first three → build-a, build-b, build-c. Wave 2: the fourth (if any) → the
first builder free. If anything must give, protect the first two.

## 4. Presentation rules (the core of this round)

Rules 1-7 are the studio's single-player rules; rules 8-10 are for co-op.
They are principles, not a level system.

1. **One new idea at a time.** Each stage introduces at most one new rule or
   object and lets the group use it until it clicks. Stage 1 teaches only the
   core verb and is winnable in under a minute. Later stages combine ideas
   the group already knows. Aim for 4-6 short stages.
2. **The goal is always visible.** The goal bar (`ui.goal`) says what the
   group must do right now in a few words, and the goal is marked in the
   world (`ui.mark`, a ring, a glow). Nobody has to remember instructions.
3. **Things look like what they are** (section 5). No letters or
   abbreviations standing in for objects. Colour means the same thing
   everywhere: danger is always red, the goal is always green, and each
   player keeps one warm colour for the whole game.
4. **Text is the last resort.** Show first: motion, a ghost of the move, the
   object reacting. Words only when showing can't do it, short (budgets in
   `text-budgets.json`), and once (`ui.hint_once`). The splash is a title
   and one sentence. No rule screens.
5. **Clean screen.** Only what matters now. HUD at the edges, small. The
   camera frames every player and the goal; nothing important off screen.
6. **Feedback within a tenth of a second** for every action, visible to
   every player, not just the one who acted. Clearing a stage is celebrated
   for everyone; failing is quick and readable (everyone sees what went
   wrong and who it involved), and the host restarts instantly (R).
7. **The 30-second test.** A new player can say the group's goal in one
   sentence after 30 seconds, and why each thing on screen matters after two
   minutes.
8. **You know which one you are.** Your own character is unmistakable: its
   colour, a ring or marker under it, and a small label if roles differ. If
   players have different roles or abilities, the difference is visible on
   the character (shape, tool, hat), not only in text.
9. **The together moment is on screen.** When one player needs another (hold
   the door, carry the other end, stand on the switch), the world shows it:
   a line between them, a glow on the thing that needs a second player, a
   ghost of where the friend should stand. When a player ruins it for the
   others, everyone sees who and how.
10. **Works at 2 and at 4.** Each stage reads at both counts: nothing that
    only makes sense with four, no screen too crowded at four.

## 5. Art for prototypes

Readable placeholder art, not final art:
- **Default: simple 3D shapes and SVG icons the builder makes** (rules in
  `art/STYLE.md`: flat unshaded colours, fixed palette roles, no text in
  art). Players are capsules with a distinct silhouette part (hat, tool,
  backpack) per role.
- **Optional: Codex image generation** (`$imagegen`) for at most 8 images
  per prototype that a shape or SVG can't make readable (an icon, a sign, a
  texture for a key object). Flat style in the STYLE.md palette, transparent
  background, saved into `art/`. Log every image in `ai-content-log.md`
  (file, prompt summary, date). Image generation spends plan limits several
  times faster than text: don't iterate on images; get the plain version
  working first.
- Not allowed: downloaded asset packs, fonts or sounds. Built-in Godot
  features (particles, tweens, shaders) are fine. Sound optional; if used,
  generate it in code.

## 6. Technical rules

- **Engine:** Godot 4 (WSL install), GDScript, statically typed, GL
  Compatibility (runs on friends' older PCs).
- **Scaffold:** `python3 tools/build.py <id> --new` gives a networked stage
  framework (`main.gd`): Host / Join-by-address menu over ENet (port 24565,
  up to 4 players), splash, `load_stage` on the host and `_show_stage` on
  every peer, cleared flow, host keys R and 1-9; `ProtoUI` (goal bar,
  one-time hints, markers, banner, H for controls); `text.json` (every
  player-facing word lives here); `text-budgets.json`; `art/STYLE.md`; and
  Windows, Linux and Web export presets. Set `STAGE_COUNT` to your number of
  stages. Don't hand-edit `export_presets.cfg`. Keep host keys 1-9 working:
  the owner and the screenshot tool use them.
- **Host-authoritative.** Clients send inputs (`submit_input`); the host
  simulates everything (`_simulate`) and broadcasts state every physics tick
  (`receive_state`); clients only draw it. Keep synced state small. If the
  spec's netcode plan needs something else, say so in the notes first.
- **Preview mode (for screenshots).** The web export, or `--preview`, runs
  offline with bot players instead of a network. `_bot_dir` drives the bots:
  make them stand where the stage's together moment happens, so each
  screenshot shows the moment, not three capsules in a corner. The preview
  is for screenshots and a quick look only; the real game is the Windows
  build.
- **Sync test:** the game's important objects go in the report
  (`_write_report` state) so `tools/net_test.py` compares them across peers.
  Bots (`--bot`) must use the core verb, not only walk.
- **One command builds and checks everything:**
  `python3 tools/build.py <id> --seat <seat>` imports, runs headless, runs
  `tests/smoke.gd`, runs the sync test (headless host + 2 bot clients must
  end in the same state), exports the Windows zip with its download page to
  `builds/<id>/`, checks every string in `text.json` against its budget (no
  `[TODO]`, no banned phrases, no long string literals in scripts), writes
  `builds/<id>/build.json` for the Play builds page from `build-info.json`
  (title, pitch and controls default to `auto`, from `text.json`; the
  builder fills `judge` and `bugs`), exports the preview to
  `builds/<id>-preview/` and screenshots the splash and every
  stage into `protos/<id>/shots/`. Exit 0 is the only evidence it works.
  While iterating, `--no-net --no-export` is faster; hand-backs need the full
  run, then `python3 tools/net_test.py <id> --clients 3`.
- **Smoke test** (`tests/smoke.gd`) asserts the core rule in code, written
  before any tuning. Any tuning change gets an "exploit impact" line in the
  build notes.
- No addons (GodotSteam comes in production), no voice chat (friends use
  Discord). Keyboard and mouse; controller is a bonus.

## 7. Done means

1. `build.py <id>` exits 0 (sync test and screenshots included) and
   `net_test.py <id> --clients 3` passes.
2. The presentation rules in section 4 hold, as judged by player-eyes from
   the screenshots and by the lead from the code.
3. The spec's carry exploit is closed: one strong player can't solve a stage
   while the others watch. If it can't be closed, say so.
4. `ABOUT.md` (for the owner and the gate, not shown in game): what the game
   is, what each stage teaches, the friends moment to look for, how it
   changes at 2 vs 4 players, and any open exploit or carry strategy.
5. `build-<letter>-notes.md`: built, cut, known bugs, what's synced, exploit
   impact of any tuning, and honest answers: do friends cause each other's
   chaos, does it deepen, would a stranger understand it?

Time box: one long working session per prototype (about 8 hours of agent
work). Protect the first three stages and the presentation over extra
stages.

## 8. The team

| Seat | Runtime | Job |
|---|---|---|
| `proto-lead` | Claude | Step 0 specs, dispatch, code review, the gate |
| `player-eyes` | Claude | Reviews screenshots and text as a first-time player (section 9) |
| `depth-critic` | Codex | Reviews code for exploits, carry strategies and client-side gameplay |
| `build-a`, `build-b`, `build-c` | Codex | One prototype at a time each |

## 9. Reviews (per prototype, in this order)

1. **player-eyes** (`reviews/eyes-<id>.md`): looks only at `shots/`,
   `text.json` and `ABOUT.md`, never the code, and answers as a first-time
   player in a group: which one am I? What do we think the goal is on each
   screen? What is each object? Where do we need each other? What's
   cluttered, unreadable or unexplained? Pass or fail per section 4 rule,
   naming the screenshot.
2. **depth-critic** (`reviews/depth-<id>.md`): per stage, every way to skip
   or trivialize it, every way one player can carry the rest, any gameplay
   decided on a client, synced state the net test doesn't cover. Severity:
   blocks the stage / weakens it / cosmetic.
3. **proto-lead** (`reviews/lead-<id>.md`): re-runs `build.py`, reads the
   smoke test, the net report and the core-rule code (host-authoritative?),
   looks at the screenshots, weighs both reviews. Verdict: accept, or send
   back with an exact list. **Up to two send-backs** when a finding defeats
   the prototype's question or breaks a section 4 rule; otherwise accept
   with notes. Say what couldn't be judged (only the owner and friends can
   play it).

## 10. Funnel

1. **Dry run:** a throwaway `dry-run` prototype through scaffold, full build
   (sync test and screenshots), player-eyes, critic and lead. Also confirm
   whether `$imagegen` works in a builder seat (one test image, then delete
   it) and record the answer in `lead-dry-run-receipt.md`. Fix anything that
   stops for approval, then delete the dry-run files.
2. **Step 0:** proto-lead writes the v2 specs.
3. **Waves** per section 3. Reviews per section 9. As each prototype is
   accepted, append to `events.jsonl`:
   `{"kind": "playtest-ready", "seat": "proto-lead", "text": "<id> ready for a friends session"}`.
4. **Gate:** when all are accepted (or honestly failed), write
   `lead-summary.md` (one short section per prototype, under 800 words) and
   `gate.json`, then stop. Per option: the first sentence names any open
   exploit or carry strategy; `image` is the best stage screenshot; `play`
   is `builds/<id>`; `file` is `protos/<id>/ABOUT.md`.
   ```json
   {"title": "Play co-op round 2 with friends and pick", "question": "Which should go to the design team? Pick one, or two to compare further.",
    "kind": "choose", "min": 1, "max": 2, "lead": "proto-lead", "context": "lead-summary.md",
    "options": [
      {"id": "x-19", "title": "Borrow My Door", "summary": "Open exploits and carry strategies first. Then: what the stages teach, the friends moment, 2 vs 4 players, player-eyes verdict, known bugs.",
       "image": "protos/x-19/shots/stage-2.png", "file": "protos/x-19/ABOUT.md", "play": "builds/x-19"},
      {"id": "none", "title": "None yet: another co-op round", "summary": "Add notes."}]}
   ```
5. **After the decision:** record the owner's choice and notes in
   `lead-decision-notes.md`, write the end-of-run model notes (shared rules
   section 6), then stop.

## 11. Studio rules (in addition to the shared rules)

- Run from `~/openrig/jobs/coop-N/` (a Rig Console job, rig name = folder
  name). Before dispatch the operator pre-approves for every seat: `rig
  queue` commands, `python3 tools/build.py` and `python3 tools/net_test.py`
  inside the job folder.
- Builders work only inside `protos/<id>/` and `builds/<id>*` via the build
  tool. Never touch another builder's folders.
- Cuts or rankings against a reviewer's finding are labelled "lead
  judgment". Open exploits are named first in every gate summary.
- File prefixes: `lead-`, `eyes-`, `depth-`, `build-a-`, `build-b-`,
  `build-c-`.
- Never spend money, create accounts, post, contact anyone, or download
  assets, addons or code.
