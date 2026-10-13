# Handoff: Studio Architect (written by the Studio Architect chat session, 2026-10-12)

## 1. Scope in one paragraph
I designed the AI game studio and own everything in `studio/`: `STUDIO-PLAN.md` (the pipeline), the stage
templates in `studio/rigs/`, studio briefs in `studio/briefs/`, setup scripts in `studio/setup/`, and
`studio/ARCHITECTURE-LOG.md` (AD-001 to AD-025). The pipeline: pitch rooms (Track A single-player
`depth-room`, Track B online co-op `friend-room`) → prototype sprints (`proto-sprint` web builds,
`coop-proto` Windows co-op builds) → design team (`design-team`, one job per game) → production (template
**not written yet**). Prototypes are throwaway; production is a clean Godot 4 + GodotSteam build.
Edges in practice:
- Cross-team rules belong to the Rig Architect (`briefs/SHARED-RULES.md`). Studio rules may be stricter,
  never looser, and templates point at SHARED-RULES instead of copying it.
- Console needs go in `dashboard/REQUESTS.md` (R-012 to R-015 are mine).
- The Model Architect grades my teams' seats; I answer in my log.
- I never message team seats or the operator; the owner (or, in this rig, an approved gate) does.

## 2. Current state (2026-10-13 07:30Z, studio@architects)
- **Production template v1 written** (`studio/rigs/production/`, AD-027), tested in
  `~/openrig/scratch/studio/prod-test/` on Bridge's real data. Owner gate
  Gate studio-prod-1 **approved** 07:31Z. `studio/` synced to `~/openrig/studio/` (production
  template verified identical). Launch text sent to the operator as qitem-20261013073904-e9d4680743c5cb9d
  (design-brief copy into bridge-design, bridge-prod up, pre-approvals, wake tech-lead only).
  Next: when the operator confirms, read bridge-prod's dry run and first plan from
  `~/openrig/jobs/bridge-prod/`.
- bridge-design: Stage 3 done, design and art direction approved (River Collage visuals, Painted
  Monument audio); team idle in production support.
- Platform has a note on `milestones.json` (R-015).

## Earlier state (2026-10-12 ~19:15)
- **proto-3** (`~/openrig/jobs/proto-3`, template `studio/rigs/proto-sprint` v3 "feels like a game"):
  building x-15 Track Eater and x-18 Three Hard Landings only (x-14 and x-19 went straight to design).
  Both have green builds. Ends with a gate.
- **coop-2** (`~/openrig/jobs/coop-2`, template `studio/rigs/coop-proto` v2 "readable together"):
  rebuilding the coop-1 picks x-08, x-19 (Borrow My Door), x-03 and x-02 (wave 2) with the presentation
  rules, a player-eyes seat, and screenshots from an offline web preview with bots. Wave 1 is building.
- **bridge-design** (`~/openrig/jobs/bridge-design`, template `studio/rigs/design-team` v2): A Bridge Goes
  Walking (x-14). The **pillars-and-product gate is open** (`gates/pillars-product.json`). I recommended
  approve with five notes (deterministic sim, a way past stuck crossings, a readout view as an accessibility
  setting, the 20 crossings vs 8-12 hours mismatch, and recording that this supersedes the proto-2
  "not yet" decision).
- **sunrise-design** (Shovel the Sunrise, x-19 from proto-2): set up from the same template but **not seen
  running** in the mirrors. The owner may have held it back to save usage. Launch steps are in
  `studio/rigs/design-team/README.md`.
- **assets-1** (`~/openrig/research/assets-1`, brief `studio/briefs/asset-pipeline-research.md` v2): running
  on the research team. Covers art, 3D, animation, SFX, music (with a priced human-composer option); a
  13-asset lineup test for consistency; ends with two gates.
- **Old jobs:** proto-2, depth-1, coop-1, friends-1 are done. Bring their rigs down once leads have written
  decision notes and model notes; keep the folders (design jobs copied inputs from proto-2).

## 3. Open items
| Item | Waiting on | Next step | Where it's recorded |
|---|---|---|---|
| Reviewer worktree (AD-031) | Next template batch | In the repo only; not synced to `~/openrig/studio/`. bridge-prod already works this way | AD-031 |
| Production fixes from the dry run | First fresh bridge-prod session | Installed 08:46Z (backup `bridge-prod/ops/studio-fixes-1-backup`, record `ops/studio-fixes-1-installed.json`); role blocks gone from shared files (checked). Then, after the first fresh bridge-prod session boots with the right role, make the same `guidance: []` change in the other templates' agent.yaml files (one Edit each) | AD-029, AD-030 |
| Production template | Launched (studio-prod-1 approved) | On approval: install, send operator text, watch bridge-prod's dry run. Later: GodotSteam install script before milestone 2; update STUDIO-PLAN stage 4 to match | AD-027 |
| `milestones.json` contract | Platform drafts it (R-015) | Review it alongside the production template | `dashboard/REQUESTS.md` R-015 |
| R-012 audio in gate options | Platform (next on their list) | Art-and-audio direction gates use `audio` and `model_preview`; if they land first, summaries point at the file | AD-021, AD-023 |
| R-013/R-014 Assets and Docs tabs | Platform | Nothing; manifest v0 is `studio/briefs/asset-manifest.md` | AD-023 |
| R-001 `max_soft` | Live after a console restart | Pitch-room gates already carry it | AD-024 |
| Asset manifest v1 | assets-1 gate 2 | Merge their proposal into `studio/briefs/asset-manifest.md`; tell `platform` if fields change | AD-021 |
| proto-3, coop-2, bridge-design gates | Owner | Read each gate, give the owner a recommendation (they ask for one) | job folders |
| Next pitch round items (MA-004, AD-011) | Before any new pitch round | Critic score anchors + forced bottom-third ranking; deck draws without replacement, 4 hands + 3 free; E1-E3; clarification channel; lessons file; playbooks | AD-011, AD-015, AD-025 |
| Bring down finished rigs | Operator via owner | proto-2, depth-1, coop-1 after their notes | — |

## 4. Decisions that matter and why
- **Prototypes are throwaway; production is a clean build** with GodotSteam (AD-009). Never let a team grow
  a prototype into the product.
- **Presentation rules** (AD-017, AD-018): one idea per stage, goal always visible, things look like what
  they are, text last and short and once, clean screen, feedback within 0.1 s, the 30-second test; co-op
  adds "you know which one you are", "the together moment is on screen", "works at 2 and at 4". Born from
  three rounds of owner complaints ("robotic", "Dwarf Fortress", text walls). The **player-eyes** seat
  judges screenshots only, never code. Don't remove it.
- **Agents must see the game:** `build.py` screenshots every stage (Playwright Chromium); co-op builds have
  an offline web preview with bots so screenshots exist. Builds also write `build.json` for the console.
- **Design team designs the polished product, buildable** (AD-020): product brief and scope, quality bar,
  feel as values + acceptance checks + an owner checklist, every screen, Steam features, art and audio
  bible with a consistency kit. The owner judges feel by playing production milestone 1 (he declined a
  feel-toy gate during design).
- **Art direction makes or breaks the game** (owner, AD-021): consistency kit and lineup tests in the
  design team and asset research; cross-model review of the art director's lineup.
- **Up to two send-backs; lead-judgment labels; open exploits named first in every gate** (AD-010).
- **Cheese policy, not "no cheese"**: bug / degenerate / clever (design team).
- **Brevity enforced twice**: a Codex editor cuts Claude-written text; `check_text.py` fails over-budget
  strings and AI-isms.

## 5. The owner: how they like to work
- Ambitious and fast; thinks AI timelines are human-padded ("I'll essentially have an AI studio working
  around the clock"). Price floor $2.99, no ceiling.
- Plays every build and gives blunt, specific feedback. Favourites so far: A Bridge Goes Walking, Shovel the
  Sunrise (single-player); likes "where the heads are at" on the co-op ideas but couldn't read them.
- Asks for my opinion and expects a recommendation with reasons, then decides. Never decide for him; never
  answer a gate on his behalf. He sometimes goes over gate maxima by note.
- Wants short replies, exact commands to paste (say Ubuntu vs PowerShell), and for anything another role
  reads: **notes in my log, then one line naming who has new notes** (ROLES.md handoff format). In this rig,
  message them directly instead.
- Wants original game ideas, not existing IP. No spending, accounts, posting or contacting people without
  him. No GitHub use by agents.
- Explicitly asked for: a design team that decides art direction, physics feel and polish "so it can be
  built"; Steam achievements and integrations designed up front; production iterating to done after design.

## 6. Working knowledge
- **Template install:** templates are copied into WSL with
  `rsync -a --exclude runs/ "/mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/studio/" ~/openrig/studio/`
  (add `--delete` per folder when files were removed). Jobs are `cp -r` copies of a template, so **template
  changes don't reach running jobs**: name the files to copy into each running job.
- **Godot:** 4.7.1 in WSL (`studio/setup/install-godot-wsl.sh`), GL Compatibility, web export without
  threads, Windows export with embed_pck. `build.py` redirects XDG dirs into `<job>/.godot/home` so sandboxed
  seats can run it.
- **Screenshots:** `studio/setup/install-shots-wsl.sh` installs Playwright + Chromium into
  `~/.local/share/studio-shots`; system libraries come from apt (`libnss3 libnspr4 libasound2t64`), because
  `sudo npx` can't see the user's Node.
- **Co-op net test:** `tools/net_test.py` runs a headless host + bot clients on a free port with a shared
  clock (`--clock`, `--report-at`) so all report at the same moment; compares final states.
- **Text:** all player words in `text.json`; budgets in `text-budgets.json`; long string literals in `.gd`
  files fail the build; `[TODO]` anywhere fails.
- **Gates:** studio gates are JOBS.md section 4; options use `image` (best screenshot), `play`, `file`, and
  now `audio` / `model_preview`. Pitch gates carry `max_soft`.
- **Card decks:** pitch cards must not contain commas (`check_pitches.py` splits on them; `draw_hands.py`
  rejects them).
- **Owner messages tagged `[msg <id>]`:** answer with `~/openrig/jobs/architects/replies/<id>.json`
  (`{"id", "text", "at"}`; follow-ups `<id>-2.json`), per JOBS.md 3e and brief v1.4 section 2.
- **Rule changes:** the operator relays them to team leads (SHARED-RULES section 7); check before
  relaying again.
- **Supervision:** read `~/openrig/jobs/<job>/` directly (read-only; `jobs-mirror/` is stale, PL-020)
  and `snapshots/<seat>@<rig>.txt` pane captures.
- **Ids collide across tracks:** x-19 is Shovel the Sunrise in proto-2/proto-3 and Borrow My Door in
  coop-1/coop-2. Always say the title.
- **Testing templates:** I tested scaffolds end to end (import, run, smoke, net, export, text, shots) in a
  scratch copy before every template change. Keep doing that; never test inside a live job folder.

## 7. Read first
1. `architects/brief.md`, `ROLES.md`, `briefs/SHARED-RULES.md`
2. `studio/STUDIO-PLAN.md`
3. `studio/ARCHITECTURE-LOG.md` (AD-017 onward in detail; Notes sections at the end)
4. `studio/rigs/proto-sprint/brief.md` and `studio/rigs/coop-proto/brief.md`
5. `studio/rigs/design-team/brief.md`
6. `studio/briefs/asset-pipeline-research.md` and `studio/briefs/asset-manifest.md`
7. `models/LOG.md` "Notes for the Studio Architect" and `models/roles/studio-architect.md`
8. `dashboard/REQUESTS.md` R-012 to R-015

## 8. Don't
- Edit anything outside `studio/` (and this handoff), including `briefs/`, `dashboard/`, `models/` or
  another architect's log. Request it.
- Copy shared rules into templates; point at SHARED-RULES.
- Hand prototype code to production, or let "polish" mean prototype polish.
- Write feel, art or "juice" as adjectives in a spec; it must be buildable and checkable.
- Answer a gate for the owner, message team seats directly, or send the operator anything without the
  owner's approval (in this rig: an approve gate).
- Change a running job's files without telling its lead to re-read them.
- Assume a template change reached a running job.
