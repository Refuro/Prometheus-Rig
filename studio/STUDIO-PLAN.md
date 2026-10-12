# Game studio plan

Written 2026-10-11, updated 2026-10-12 after the first prototype round. Audience: you, and any agent seat that needs the big picture.
Each stage has its own brief and rig. This file says how they fit together; a
stage's brief wins on details.

## The idea in one paragraph

An agent studio that invents an original game, proves it is fun with cheap
playable prototypes, locks a vision and an art direction, then builds it.
The key difference from a human studio: **ideas are narrowed by playing
prototypes, not by writing documents.** Agents can build a grey-box Godot toy
in hours, so "is this fun?" gets answered by you playing it, not by anyone
imagining it.

## Stages and gates

| # | Stage | Rig | Output | Your gate |
|---|---|---|---|---|
| 1A | Depth room (single-player) | `depth-N` | Up to 8 blind-judged cards | Gate: pick 2-5 (or "none, go again") |
| 1B | Friendslop room (online co-op) | `friends-N` | Up to 6 blind-judged cards | Gate: pick 1-3 (or none) |
| 2 | Prototype sprint | `proto-N` | Three-beat playable builds (web for 1A; Windows co-op for 1B) | Gate: play them, pick 1-2 (or none) |
| — | Asset pipeline research | research job | Recommended way for Codex to make game assets | Gate: approve the pipeline |
| 3 | Vision | `studio` (first seats) | Pillars doc, art bible | Approve pillars + one art direction |
| 4 | Production | `studio` (full) | Milestone builds | Play every milestone build |

Going back is cheap and expected: "none of these" at gate 1 or 2 just starts
another pitch round, carrying your notes forward. Tracks 1A and 1B run in
parallel and never read each other's files.

**Lessons from round 1** (pitch-1 → proto-1): the toys were fun for two
minutes and the same at minute twenty, and several didn't explain what the
game was. Round 2 answers both: pitches must describe their late game and
survive a depth critic, and prototypes must show three beats with a title
card and contextual hints.

## Stage 1: Pitch rooms (specced, ready to run)

Templates: `studio/rigs/depth-room/` (Track A) and `studio/rigs/friend-room/`
(Track B); copy to `~/openrig/jobs/depth-N/` and `~/openrig/jobs/friends-N/`.
The original `studio/rigs/pitch-room/` is kept as the round-1 reference.

| Seat | Runtime | Job |
|---|---|---|
| `room-lead` | Claude | Draws collision hands, blinds the cards, curates, writes the board, the gate and the proto specs |
| `pitch-a..c` | Codex | Pitch from their hands, independently |
| `revise-cards` | Codex | Track A only: rewrites returning ideas against your notes |
| `depth-critic` | Codex | Tries to break every card: exploits, ten distinct situations/sessions, variety engine |
| `scout-novelty` | Codex | Nearest existing games per card; Track B also writes a co-op market read |

What makes it work:
- **Depth first.** Cards must describe the first five minutes, hour one, a
  late-game moment and their variety engine (Track B: the friends moment and
  the tenth session). Depth and exploit-proofing are gates, judged by a critic
  from a different model family than the curator.
- **Blind judging.** `tools/blind.py` anonymizes every card before the
  critic, scout and curator see it, so returning ideas (and any pitcher's
  style) can't sway the board. The key is revealed only after the gate.
- **Collision hands** with a growth-engine suit (Track A) or a social-twist
  suit (Track B) push past "pitch me a game" averages.

## Stage 2: Prototype sprints (both tracks specced)

Template: `studio/rigs/proto-sprint/` (copy to `~/openrig/jobs/proto-N/`).

| Seat | Runtime | Job |
|---|---|---|
| `proto-lead` | Claude | Dispatches specs in waves of three, reviews each against its spec, writes the gate |
| `depth-critic` | Codex | Reads each prototype's code for exploits before the lead's review |
| `build-a..c` | Codex | One prototype at a time: three beats, title card, hints, web export |

Every prototype: a title card from `ABOUT.txt` (what the game is, win/lose,
what every object does), contextual hints for every new object, three beats
on keys 1/2/3 (early, middle, late), the spec's exploit closed. One command
(`tools/build.py`) scaffolds, checks, smoke-tests and web-exports; builds
appear on the Play builds page as they land.

**Prototypes are throwaway.** They answer "is it fun, and does it deepen?"
and nothing else. No prototype code is carried into production.

**Track B (co-op): `studio/rigs/coop-proto/`** (copy to
`~/openrig/jobs/coop-N/`). Same seats and rules, plus: a scaffold that
already hosts and joins over ENet (host-authoritative: clients send inputs,
the host simulates and broadcasts state), an automated sync test
(`tools/net_test.py`: a headless host plus bot clients must end in the same
state), Windows zips with a download page on the Play builds page, and
friends joining over Tailscale. The gate comes after you play with friends.

**Prerequisite (done):** Godot 4.7.1 + export templates in WSL
(`studio/setup/install-godot-wsl.sh`).

## Stage 3: Vision (template ready: `studio/rigs/design-team/`)

The design team turns the winning prototype into a signed-off design, then
**stays on through production** (copy to `~/openrig/jobs/<game>-design/`).

| Seat | Runtime | Owns |
|---|---|---|
| `creative-director` | Claude | Pillars, tone, final call below you; inbox; milestone vision checks |
| `design-systems` | Claude | Core loop, progression map, variety engine, content plan |
| `design-balance` | Codex | Numbers in data, simulations, the cheese register |
| `design-onboarding` | Claude | First ten minutes; every object explains itself |
| `words-narrative` | Claude | Whether a story earns its place; structure and voice |
| `words-editor` | Codex | Word budgets; cuts every player string; `check_text.py` green |
| `art-director` | Codex (images) | 3-4 visual directions, then the art bible |

Only the director and systems designer work continuously; the rest wake on
demand. Stage 3 ends with three gates: pillars (approve), art direction
(choose 1), design (approve).

- **Brevity is enforced twice:** a Codex editor cuts text written by Claude
  seats, and `tools/check_text.py` fails any string over its word budget or
  containing a banned AI-ism. Budgets come from the pillars' text profile.
- **Cheese policy:** exploits are bug / degenerate / clever. Degenerate cheese
  gets fixed; clever cheese that rewards insight stays.
- **Discoveries can morph the game:** a discovery inbox (`tools/inbox.py`);
  the director adopts, spikes, parks, rejects or escalates. Anything that
  breaks a pillar becomes an amend gate for you. Each milestone reserves
  10-15% of build time for spikes.
- **Data-first:** numbers and text live in the game's `data/`, so designers
  change the game without touching code.

## Stage 4: Production (to spec after gate 3)

**A clean build, not a grown prototype.** Production starts a new project
designed for shipping from day one: Steam integration (GodotSteam:
achievements, cloud saves, and lobbies/networking for co-op), save system,
settings, input remapping, localization hooks, and an architecture the tech
lead designs up front. The winning prototype is reference material (what
the fun feels like, which numbers worked), never a code base.

| Seat | Runtime | Job |
|---|---|---|
| `tech-lead` | Claude | Architecture + milestone plan; each milestone ends in a playable build |
| `dev-N` + `review-N` | Codex + Claude | Implementer/reviewer pairs, cross-vendor (your starter pattern) |
| `art-concept` | Codex | Concepts, one-off assets, UI |
| `art-production` | Codex + the researched pipeline | Production assets (2D and/or 3D) through the pipeline chosen by the asset research job, held to the art bible |
| `art-review` | Claude | Checks every asset batch against the art bible before it enters the game |
| `playtest-bot` | Codex | Headless simulations: softlocks, difficulty curves, solvability; reports exploits to the balance designer |
| producer | kernel operator | Queue health, usage budget, phase tracking |

**Working with the design team** (which stays up in its own rig): builders
send design questions and discoveries to `creative-director`, never guess;
`check_text.py` runs as a production build step; balance changes are data
changes. **Vision check per milestone:** the tech lead sends a packet (what
changed, screenshots, build path, open exploits) to the creative director,
who returns PASS or FAIL against the pillars. FAIL goes back to the tech
lead; PASS milestones reach you as a gate, and you play every one.

## Studio-wide rules (from your research-run retros)

1. **Decisions live in files**, never only in messages: pitch cards, pillars,
   art bible, `decisions.md`. Messages point at files.
2. **Fresh rig per stage.** Long conversations burn usage on every turn.
3. **Dry run every new seat type** through claim, work, save, hand back
   before dispatch; fix every permission prompt first.
4. **Shell hygiene:** no `$`, backticks or pipes in shell text; use
   `--body-file` for any free text sent through `rig`.
5. **File prefixes per seat** so no two seats write the same file.
6. **Claude for judgment, Codex for volume.** Claude seats: leads, creative
   director, reviewers. Everything else Codex. Stop and save on any usage
   warning.
7. **Every owner decision is a Rig Console gate** (`gate.json`, see
   `dashboard/JOBS.md`), never a chat question. Teams stop at the gate and
   never write decision files. No stage starts the next one by itself.
8. **Originality:** no existing franchises, characters or real people; no
   "X but with Y" clones of a named game unless the twist changes the core
   verb.
9. **Steam:** AI-generated content must be disclosed on the store page. Keep
   a running `ai-content-log.md` from stage 3 on.
10. **Every stage runs as a job** in `~/openrig/jobs/<name>/` with a
   `job.json`, so the console tracks it; web builds go in `builds/<name>/`.

## Scope principle

Plan in agent time, not human time. The studio runs around the clock, so
code volume is cheap; estimates calibrated on human teams run long. What
still costs real time is the human loop: you playing builds, approving art,
and any hand-crafted writing. Scope decisions weigh those, not lines of
code. Price floor is $2.99 with no ceiling, so bigger ideas can price
higher instead of being cut down.

## Asset pipeline research (run any time before stage 3)

Games need real assets, and Codex should make them. Brief:
`studio/briefs/asset-pipeline-research.md`, for a research team. It compares
the routes (Codex image generation, Blender driven over MCP or Python
scripting, text/image-to-3D models, local generation on the 4080, procedural
generation in Godot) on quality, style consistency, cost, licensing and Steam
disclosure, and ends with a gate recommending one pipeline per asset type.

## Open questions

- Platform beyond PC/Steam (web on itch for public prototypes)? Default: PC
  only, web builds just for internal prototypes.
