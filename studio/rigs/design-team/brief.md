# Design team brief (studio stage 3, then production support)

## 1. Mission

Turn the winning prototype into a game design the owner signs off: pillars,
tone, art direction, systems and progression, balance, story (only if it
earns its place), onboarding, and word budgets for every piece of player text.
Then stay on through production as the team that answers design questions,
judges discoveries, and protects the pillars, while leaving room for the game
to change when building reveals something better.

The prototype is reference, not a code base: production is a clean build
designed for Steam from day one. Design everything in data (`data/`) so
builders implement systems and designers own the values.

## 2. Inputs

`inputs/` holds, copied in at launch:
- the winning pitch card and its proto spec;
- the prototype's `ABOUT.txt`, `HOW-TO-PLAY.md`, builder notes and reviews;
- the prototype gate decision with the owner's notes (`decisions/`);
- screenshots of the prototype if any (`inputs/shots/`).
The prototype web build stays playable on the console's Play builds page.

## 3. The team

| Seat | Runtime | Owns | Always on? |
|---|---|---|---|
| `creative-director` | Claude | Pillars, tone, final call below the owner; routes questions and discoveries; milestone vision checks | Yes |
| `design-systems` | Claude | Core loop, progression map, variety engine, content plan (`docs/design.md`) | Yes |
| `design-balance` | Codex | Numbers and curves in `data/balance/`, simulations, the cheese register (`docs/balance.md`) | Woken |
| `design-onboarding` | Claude | First-10-minutes teaching plan, every object explaining itself (`docs/onboarding.md`) | Woken |
| `words-narrative` | Claude | Story recommendation and, if any, structure and voice (`docs/story.md`) | Woken |
| `words-editor` | Codex | Word budgets (`text-budgets.json`), editing all player text down, `tools/check_text.py` green | Woken |
| `art-director` | Codex (image generation) | Visual directions, then the art bible (`docs/art-bible.md`) | Woken |

"Woken" seats stay idle until the creative director sends them work. Keep the
team small in practice: one or two seats active at a time beyond the two
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
- **Data-first.** Numbers in `data/balance/`, text in `data/text/`, content
  definitions in `data/content/`. Docs point at files; they don't duplicate
  values.
- **Decisions live in files.** `docs/decisions.md` gets one line per decision.
  Owner decisions are gates; never ask the owner in chat; never write a
  decision file.
- No existing IP, characters or real people. No `$`, backticks or pipes in
  shell text; use `--body-file`.

## 5. Stage 3 funnel (vision)

1. **Dry run.** Director sends each seat a tiny task (write one line in a
   scratch file, run `tools/check_text.py` or `tools/inbox.py list`, hand
   back). Fix every permission prompt, then delete the scratch files.
2. **Pillars first.** Creative director drafts `docs/pillars.md` from the
   inputs (template in `templates/`). Everyone else reads it before starting.
3. **Parallel drafts** (from the templates):
   - design-systems → `docs/design.md`
   - design-balance → `docs/balance.md` + first `data/balance/*.json`
   - design-onboarding → `docs/onboarding.md`
   - words-narrative → `docs/story.md` (may recommend no story)
   - words-editor → `text-budgets.json` profile and budgets from the pillars
   - art-director → 3-4 visual directions, each 2-3 images painted over or
     inspired by prototype screenshots, in `art/directions/<name>/`, plus a
     one-paragraph rationale each. Styles that tolerate small inconsistencies
     and avoid frame-by-frame character animation are favoured.
4. **Cross-review, once each:** systems ↔ balance, onboarding ↔ systems,
   narrative ↔ editor. Reviews are short lists in `docs/review-<seat>.md`.
   The director settles disagreements and logs them in `decisions.md`.
5. **Brevity pass:** editor runs over every player-facing string drafted so
   far (`data/text/`) until `check_text.py` is green.
6. **Gates** (in `gates/`), then stop and wait:
   - `pillars.json`: kind `approve`, context `docs/pillars.md`.
   - `art-direction.json`: kind `choose`, pick 1, one option per direction
     with `image` set to its best image.
   - `design.json`: kind `approve`, context `docs/design.md` (summary
     mentions balance, onboarding and story recommendations).
7. **After decisions:** apply any send-back notes (one revision round, then
   a new gate id), then art-director writes `docs/art-bible.md` for the
   chosen direction with reference images in `art/bible/`. Director confirms
   the stage is done in `decisions.md` and the team switches to production
   support (section 6).

## 6. Production support (ongoing)

Production runs in its own rig and repo. The tech lead records the repo path
in `links.md` here. From then on, data edits happen in `<repo>/data/`, and
docs stay here.

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

**Milestone vision check:** when the tech lead finishes a milestone, the
director plays nothing (it can't) but reviews the milestone packet (changes,
screenshots, build path, open exploits) against the pillars and writes
`docs/vision-check-<milestone>.md`: **PASS** or **FAIL** with one paragraph.
FAIL goes back to the tech lead. PASS milestones go to the owner as a gate
from the production rig.

**Text in production:** `tools/check_text.py --root <repo>/data/text` is a
required production build step. The editor owns making it green.

**Balance in production:** design-balance keeps the cheese register current
from playtest-bot reports and owner notes, classifies each exploit, and
changes numbers in `data/balance/`, never code.

## 7. Operations

- Runs as a Rig Console job in `~/openrig/jobs/<game>-design/` (`job.json`
  present). Fresh rig named after the folder.
- Before dispatch the operator pre-approves for every seat: `rig queue`
  commands and `python3 tools/*.py` inside the job folder.
- File prefixes: docs by name in `docs/`, reviews `docs/review-<seat>.md`,
  helper files `<seat>-*.md`.
- The operator acts only when messaged. The team stays up between
  milestones; woken seats idle at no cost.

## 8. Limits

- Never spend money, create accounts, post publicly or contact anyone.
- Stop at every gate. If usage warnings appear: stop, save, report.
- Two-exchange disagreement rule: write both positions into `decisions.md`
  and let the director decide; pillar-level disagreements go to the owner as
  a gate.
