# Design team brief (studio stage 3, then production support)

Shared rules first: every seat follows `~/openrig/briefs/SHARED-RULES.md`
(decisions and gates, when to stop, provider-capacity retries, shell
commands, the outside world, run start and end, end-of-run model notes).
This brief adds studio rules on top; where it is stricter, it wins.

## 1. Mission

Design the **finished, polished game and product** the owner will sell on
Steam, from the winning prototype: what it is and who it's for, how it
feels in hand, how it looks and sounds, how it teaches itself, every screen
and setting, its Steam features, the quality bar it must clear and the scope
that fits that bar. Not a bigger prototype: the 1.0 the owner would be proud
to put a price on.

The output is a **design package production can build without guessing**:
every feel, number and string in `data/`, every behaviour described so a
builder can implement it and a test can check it. The owner judges by
playing what production builds; the design must be precise enough that
"it doesn't feel right" can be traced to a value or a missing behaviour.

Then the team stays on through production to answer design questions, judge
discoveries and protect the pillars, while leaving room for the game to
change when building reveals something better.

The prototype is reference, not a code base: production is a clean build
designed for Steam from day one (GodotSteam).

## 2. Inputs

`inputs/` holds, copied in at launch:
- the pitch card and the proto spec (`proto-spec-<id>.md`);
- the prototype project (`inputs/proto/`, reference only, including its
  physics code and values as a starting point for the feel) and whatever it
  shipped with: ABOUT, HOW-TO-PLAY, builder notes, reviews;
- `owner-notes.md`: what the owner said after playing. **It outranks every
  other input.** Where the owner named a must-have (for example "the physics
  will need to be amazing"), the pillars name it too;
- the gate decision with the owner's notes (`decisions/`);
- `presentation-rules.md`: the studio's seven presentation rules, learned
  the hard way over three prototype rounds (rules dumped at once, text
  walls, letters standing in for objects, goals not shown). Onboarding and
  the art direction build on them;
- the web build (`inputs/build/`) and screenshots (`inputs/shots/`). If
  shots are missing, take them: `python3 tools/shoot.py inputs/build
  inputs/shots 3`.
The prototype web build also stays playable on the console's Play builds page.

## 3. The team

| Seat | Runtime | Owns | Always on? |
|---|---|---|---|
| `creative-director` | Claude | Pillars, tone, final call below the owner; the product brief and scope (`docs/product.md`); the quality bar (`docs/quality-bar.md`); the production handoff; routes questions and discoveries; milestone vision checks | Yes |
| `design-systems` | Claude | Core loop, progression, variety, content plan (`docs/design.md`); Steam features (`docs/steam.md`) | Yes |
| `design-feel` | Claude | How it feels in hand: physics, controls, camera, response to every action (`docs/feel.md`, `data/feel/`) | Woken |
| `design-balance` | Codex | Numbers and curves in `data/balance/`, simulations, the cheese register (`docs/balance.md`) | Woken |
| `design-ux` | Claude | Onboarding, every screen and the HUD, settings, save, controller and Steam Deck, accessibility, localization readiness (`docs/ux.md`) | Woken |
| `words-narrative` | Claude | Story recommendation and, if any, structure and voice (`docs/story.md`) | Woken |
| `words-editor` | Codex | Word budgets (`text-budgets.json`), editing all player text down, `tools/check_text.py` green | Woken |
| `art-director` | Codex (image generation) | Art and audio: directions, then the art and audio bible (`docs/art-bible.md`) | Woken |

"Woken" seats stay idle until the creative director sends them work. Keep the
team small in practice: two or three seats active at a time beyond the two
always-on ones.

## 4. Rules for every seat

- **Brevity is a feature.** AI-written game text runs long. Player text must
  pass `tools/check_text.py` (budgets and banned phrases in
  `text-budgets.json`). Design docs are for agents and can be fuller, but each
  has a length cap: pillars one page, every other doc under ~1,500 words.
- **The editor edits; the writer doesn't grade itself.** All player-facing
  text from Claude seats goes through `words-editor` (Codex) before it lands.
- **Cheese policy, not "no cheese".** Exploits are classified bug /
  degenerate / clever (see `templates/pillars.md`). Clever cheese that needs
  insight is part of the fun; defend against degenerate cheese, not against
  smart players.
- **Data-first.** Numbers in `data/balance/`, feel values in `data/feel/`,
  text in `data/text/`, achievements in `data/steam/`, content definitions in
  `data/content/`. Docs point at files; they don't duplicate values.
- **Buildable, not aspirational.** "Satisfying", "juicy" or "polished" are
  not specs. Every quality is written as a behaviour with values and a way
  to check it ("a plank under one walker sags 4-6 cm and settles within
  0.6 s"). If a builder would have to guess, the design isn't done.
- **Polish is designed, not hoped for.** Every player action has a planned
  response (motion, sound, camera, haptics); every screen exists on paper,
  including settings, pause, credits and error states.
- **Decisions live in files.** `docs/decisions.md` gets one line per decision.
  Owner decisions are gates; never ask the owner in chat; never write a
  decision file.
- No existing IP, characters or real people. Shell text follows the shared
  rules (use `--body-file`).

## 5. Stage 3 funnel (vision)

1. **Dry run.** Director sends each seat a tiny task (write one line in a
   scratch file, run `tools/check_text.py` or `tools/inbox.py list`, hand
   back). Fix every permission prompt, then delete the scratch files.
2. **Pillars and product first** (director, from the templates and every
   input): `docs/pillars.md` and the first half of `docs/product.md`
   (audience, comparable games, price, length, platforms). Gate
   `pillars-product.json` (kind `approve`), then **stop and wait**:
   everything after builds on it.
3. **Parallel drafts** (from the templates), after the pillars are approved:
   - design-systems → `docs/design.md`, then `docs/steam.md` and
     `data/steam/achievements.json`
   - design-feel → `docs/feel.md` + `data/feel/*.json`
   - design-balance → `docs/balance.md` + first `data/balance/*.json`
   - design-ux → `docs/ux.md` (onboarding first, then every screen)
   - words-narrative → `docs/story.md` (may recommend no story)
   - words-editor → `text-budgets.json` profile and budgets from the pillars
   - art-director → 3-4 directions in `art/directions/<name>/`: 2-3 images
     each (in-game views, built on prototype screenshots where possible, plus
     one UI mock), and a short rationale covering mood, palette, shapes,
     **the sound and music that go with it** (described, with instruments,
     tempo and texture), and how well the asset pipeline can hold it
     consistent across hundreds of assets. Favour styles that tolerate small
     inconsistencies and avoid frame-by-frame character animation.
4. **Cross-review, once each:** systems ↔ balance, feel ↔ systems,
   feel ↔ ux (camera, input, readability), ux ↔ systems, narrative ↔ editor.
   Short lists in `docs/review-<seat>.md`. The director settles
   disagreements and logs them in `decisions.md`.
5. **Brevity pass:** editor runs over every player-facing string drafted so
   far (`data/text/`, achievement names and descriptions included) until
   `check_text.py` is green.
6. **Quality bar and scope** (director): `docs/quality-bar.md`, then the
   second half of `docs/product.md`: the 1.0 scope and cut list sized so the
   whole game can clear the quality bar, the demo plan, the Steam page and
   trailer needs.
7. **Gates** (in `gates/`), then stop and wait:
   - `art-direction.json`: kind `choose`, pick 1, one option per direction
     with `image` set to its best image, `audio` to its mood sample if one
     exists, and `model_preview` to a turntable for 3D directions; the
     summary names the audio mood.
   - `design.json`: kind `approve`, context `docs/handoff.md` (a one-page
     reading guide to the package). Summary covers: the feel in three
     sentences, scope and price, Steam features, the quality bar headline,
     story recommendation, and the riskiest open question.
8. **After decisions:** apply any send-back notes (one revision round, then
   a new gate id). Art-director writes `docs/art-bible.md` (art and audio)
   for the chosen direction with references in `art/bible/`, including the
   consistency kit and a lineup image the director reviews; design-ux
   updates the UI section to match it. Director finishes `docs/handoff.md`
   for the production tech lead: reading order, what's decided, open
   questions, and **production milestone 1: a feel build** that implements
   `docs/feel.md` with no content beyond a test space, for the owner to
   play and judge against the feel doc's owner checklist. Director confirms
   the stage is done in `decisions.md`, every seat writes its end-of-run
   model notes (shared rules section 6), and the team switches to
   production support.

## 6. Production support (ongoing)

Production runs in its own rig and job (`~/openrig/jobs/<game>-prod/`).
**Data stays here:** design seats keep editing `data/` and the docs in this
job folder, never production's. Production copies `data/` (and
`text-budgets.json`) into its game with its sync tool, and its build fails
if anyone edits that copy. When you change data production needs, say so
in your answer to the tech lead, so it re-syncs. Nobody writes in another
team's folder; production's files (builds, packets, `milestones.json`) can
be read for vision checks.

**Inbox** (`tools/inbox.py`): every design question and discovery becomes a
file in `inbox/`. Builders and the tech lead send them to
`creative-director` through the queue; the director files them. The owner can
add directly: `python3 tools/inbox.py add discovery --title "..." --by owner --text "..."`.

- **Questions:** the director answers or routes to the owning seat; answer in
  the item file, status `answered`. Anything that changes a pillar is
  `escalated` (see below).
- **Discoveries** ("this is fun, look"), the director decides:
  - **adopt**: fits the pillars; becomes a task for the tech lead;
  - **spike**: promising but unproven; a time-boxed experiment on a branch,
    paid from the milestone's exploration budget;
  - **park**: good, not now; stays in the inbox;
  - **reject**: with one line why;
  - **escalate**: great but breaks a pillar. The director writes a gate
    (`gates/amend-<id>.json`, kind `approve`, context = the proposed pillar
    change and the discovery). If approved, pillars change and the changelog
    records it. The game may morph, but only through the owner.
- **Exploration budget:** each production milestone reserves about 10-15% of
  build time for spikes. The director tracks spend in `decisions.md`.

**Feel build (milestone 1):** design-feel reviews it against `docs/feel.md`
(values, acceptance checks) before it goes to the owner; the owner's notes
become changes to `data/feel/`, not to the doc's goals, unless the owner
says the goal itself is wrong.

**Milestone vision check:** when the tech lead finishes a milestone, the
director plays nothing (it can't) but reviews the milestone packet (changes,
screenshots, build path, open exploits) against the pillars and writes
`docs/vision-check-<milestone>.md`: **PASS** or **FAIL** with one paragraph.
FAIL goes back to the tech lead. PASS milestones go to the owner as a gate
from the production rig.

**Text in production:** production's build runs `check_text.py` on its copy
of `data/text` with this job's budgets. The editor owns making it green, here.

**Balance in production:** design-balance keeps the cheese register current
from playtest-bot reports and owner notes, classifies each exploit, and
changes numbers in `data/balance/`, never code.

## 7. Operations

- Runs as a Rig Console job in `~/openrig/jobs/<game>-design/` (`job.json`
  present). Fresh rig named after the folder.
- Before dispatch the operator pre-approves for every seat: `rig queue`
  commands and `python3 tools/*.py` inside the job folder.
- Each game gets its own design job and rig. Two can run at once; woken
  seats idle at no cost.
- File prefixes: docs by name in `docs/`, reviews `docs/review-<seat>.md`,
  helper files `<seat>-*.md`.
- The operator acts only when messaged. The team stays up between
  milestones; woken seats idle at no cost.

## 8. Limits

- Never spend money, create accounts, post publicly or contact anyone.
- Stop at every gate. Other stops and retries: the shared rules.
- Two-exchange disagreement rule: write both positions into `decisions.md`
  and let the director decide; pillar-level disagreements go to the owner as
  a gate.
