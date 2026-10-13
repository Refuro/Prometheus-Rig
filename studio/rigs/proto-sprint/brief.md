# Prototype sprint brief, v3: "feels like a game"

Shared rules first: every seat follows `~/openrig/briefs/SHARED-RULES.md`
(decisions and gates, when to stop, provider-capacity retries, shell
commands, the outside world, run start and end, end-of-run model notes).
This brief adds studio rules on top; where it is stricter, it wins.

## 1. Mission

Earlier prototypes proved the ideas but felt robotic: rules dumped all at
once, walls of instructions, letters standing in for things, cluttered
screens. The owner couldn't tell what to do or why. This round, each
prototype must **feel like a small game**: you understand the goal within
seconds, you learn one idea at a time by doing it, everything on screen looks
like what it is, and clearing a stage feels good.

Prototypes are still throwaway (production is a clean build later), so keep
the code simple. Effort goes into the player's experience: readability,
pacing, feedback.

## 2. Inputs

- `specs/proto-spec-<id>.md`: the previous round's spec, unchanged.
- `inputs/<id>/`: the previous round's build notes, reviews and ABOUT for
  that prototype, plus its old project (`inputs/<id>/old-proto/`) which a
  builder may reuse as a starting point.
- `owner-notes.md`: what the owner said after playing the previous round.
  It outranks everything except the shared rules.
- Step 0 (proto-lead): for each prototype, write `specs/v3-<id>.md`, one
  page: the game in two sentences a stranger understands; the **teaching
  sequence** (section 4); what each stage teaches and what the player must
  do; the readable look of every object (section 5); the owner's notes and
  exactly how this version answers each one; and the exploit that must stay
  closed. The builder builds from v3, not the old spec.

## 3. Picks and waves

Wave 1: **x-14 A Bridge Goes Walking** → build-a, **x-19 Shovel the
Sunrise** → build-b, **x-15 Track Eater** → build-c.
Wave 2: **x-18 Three Hard Landings** → the first builder free.
The owner's favourites are x-14 and x-19: if anything must give, protect
those two.

## 4. Presentation rules (the core of this round)

These are principles, not a level system. A sandbox can meet them with
gradual unlocks instead of stages.

1. **One new idea at a time.** Each stage (or unlock) introduces at most one
   new rule or object, lets the player use it until it clicks, then adds the
   next. The first stage teaches only the core verb and is winnable in under
   a minute. Later stages combine ideas the player already knows. Aim for
   5-8 short stages.
2. **The goal is always visible.** The goal bar (`ui.goal`) says what to do
   right now in a few words, and the goal itself is marked in the world
   (`ui.mark`: highlight, arrow, glow). The player never has to remember
   instructions.
3. **Things look like what they are** (section 5). No letters or abbreviations
   standing in for objects. Colour means the same thing everywhere: the
   player-controlled thing is the warmest colour, danger is always red, the
   goal is always green.
4. **Text is the last resort.** Show first: animation, a ghost of the move,
   the object reacting. Words only when showing can't do it, short (budgets
   in `text-budgets.json`), and once (`ui.hint_once`). The splash is a title
   and one sentence, then play starts. No rule screens, no title-card walls.
5. **Clean screen.** Only what matters right now is on screen. HUD at the edges,
   small. Nothing flickers or moves unless it means something.
6. **Feedback for every action within a tenth of a second:** a motion, a
   colour change, a small particle or shake. Clearing a stage is celebrated;
   failing is quick, readable (the player sees what went wrong), and retry is
   instant (R).
7. **The 30-second test.** A new player can say the goal in one sentence after
   30 seconds, and why each thing on screen matters after two minutes.

## 5. Art for prototypes

Readable placeholder art, not final art:
- **Default: SVG silhouettes the builder writes** (`art/*.svg`, rules in
  `art/STYLE.md`: flat shapes, dark outline, fixed palette roles, no text in
  art) plus code-drawn shapes. Godot imports SVG directly.
- **Optional: Codex image generation** (`$imagegen`) for at most 8 key objects
  per prototype that an SVG can't make readable. Flat style in the STYLE.md
  palette, transparent background, saved into `art/`. Log every generated
  image in `ai-content-log.md` (file, prompt summary, date). Image generation
  uses plan limits several times faster than text: don't iterate on images;
  get the SVG version working first.
- Not allowed: downloaded asset packs, fonts or sounds. Built-in Godot
  features (particles, tweens, shaders) are fine. Sound is optional; if
  used, generate it in code.

## 6. Technical rules

- Godot 4 (WSL install), GDScript, statically typed, GL Compatibility.
- Scaffold: `python3 tools/build.py <id> --new` gives a stage framework
  (`main.gd`: splash, stage load, cleared/failed flow, keys R and 1-9),
  `ProtoUI` (goal bar, one-time hints, markers, banner, H for controls),
  `text.json` (every player-facing word lives here), `text-budgets.json`,
  `art/STYLE.md` and an example SVG. Keep the debug keys 1-9 working: the
  owner and the screenshot tool use them.
- **One command builds and checks everything:**
  `python3 tools/build.py <id> --seat <seat>` imports, runs headless, runs the
  smoke test, exports the web build, checks every string in `text.json`
  against its budget (no `[TODO]`, no banned phrases, no long string literals
  in scripts), writes `builds/<id>/build.json` for the Play builds page
  from `build-info.json` (title, pitch and controls default to `auto`, from
  `text.json`; the builder fills `judge` and `bugs`), and screenshots the
  splash and every stage into `protos/<id>/shots/`. Exit 0 is the only evidence it works.
- **Smoke test** (`tests/smoke.gd`) asserts the core rule in code, written
  **before** any tuning. Any tuning change gets an "exploit impact" line in
  the build notes (does it let the player skip the core rule?).

## 7. Done means

1. `build.py <id>` exits 0, with screenshots for every stage.
2. The presentation rules in section 4 hold, as judged by player-eyes from
   the screenshots and by the lead from the code.
3. `ABOUT.md` (for the owner and the gate, not shown in game): what the game
   is, what each stage teaches, what to look for, and any open exploit or
   shortcut.
4. `build-<letter>-notes.md`: built, cut, known bugs, exploit impact of any
   tuning, and the builder's honest answers: is it fun, does it deepen, would
   a stranger understand it?

Time box: one long working session per prototype (about 8 hours of agent
work). Protect the first three stages and the presentation over extra
stages.

## 8. The team

| Seat | Runtime | Job |
|---|---|---|
| `proto-lead` | Claude | Step 0 specs, dispatch, code review, the gate |
| `player-eyes` | Claude | Reviews screenshots and text as a first-time player (section 9) |
| `depth-critic` | Codex | Reviews code for exploits and shortcuts |
| `build-a`, `build-b`, `build-c` | Codex | One prototype at a time each |

## 9. Reviews (per prototype, in this order)

1. **player-eyes** (`reviews/eyes-<id>.md`): looks only at `shots/`,
   `text.json` and `ABOUT.md`, never the code, and answers as a first-time
   player: what do I think the goal is on each screen? What is each object?
   What's cluttered, unreadable or unexplained? Does each stage add exactly
   one idea? Pass or fail per section 4 rule, with the screenshot named.
2. **depth-critic** (`reviews/depth-<id>.md`): exploits and shortcuts per
   stage, severity (blocks the stage / weakens it / cosmetic).
3. **proto-lead** (`reviews/lead-<id>.md`): re-runs `build.py`, reads the
   smoke test and core-rule code, weighs both reviews. Verdict: accept, or
   send back with an exact list. **Up to two send-backs** when a finding
   defeats the prototype's question or breaks a section 4 rule; otherwise
   accept with notes. The lead cannot play; say what couldn't be judged.

## 10. Funnel

1. **Dry run:** a throwaway `dry-run` prototype through scaffold, build
   (including screenshots), player-eyes, critic and lead. Also confirm
   whether `$imagegen` works in a builder seat (one test image, then delete
   it) and record the answer in `lead-dry-run-receipt.md`. Fix anything that
   stops for approval, then delete the dry-run files.
2. **Step 0:** proto-lead writes the v3 specs.
3. **Waves** per section 3. Reviews per section 9.
4. **Gate:** when all are accepted (or honestly failed), write
   `lead-summary.md` and `gate.json`, then stop. Per option: the first
   sentence names any open exploit or shortcut; `image` is the prototype's
   best stage screenshot (`protos/<id>/shots/stage-N.png`); `play` is
   `builds/<id>`; `file` is `protos/<id>/ABOUT.md`.
   ```json
   {"title": "Play round 3 and pick", "question": "Which should go to the design team? Pick one, or two to compare further.",
    "kind": "choose", "min": 1, "max": 2, "lead": "proto-lead", "context": "lead-summary.md",
    "options": [
      {"id": "x-14", "title": "A Bridge Goes Walking", "summary": "Open exploits first. Then: what the stages teach, player-eyes verdict, known bugs.",
       "image": "protos/x-14/shots/stage-3.png", "file": "protos/x-14/ABOUT.md", "play": "builds/x-14"},
      {"id": "none", "title": "None yet: another prototype round", "summary": "Add notes."}]}
   ```
5. **After the decision:** record the owner's choice and notes in
   `lead-decision-notes.md`, write the end-of-run model notes (shared rules
   section 6), then stop.

## 11. Studio rules (in addition to the shared rules)

- Cuts or rankings against a reviewer's finding are labelled "lead
  judgment".
- Open exploits are named first in every gate summary.
- File prefixes: `lead-`, `eyes-`, `depth-`, `build-a-`, `build-b-`,
  `build-c-`.
- Never spend money, create accounts, post, contact anyone, or download
  assets, addons or code.
