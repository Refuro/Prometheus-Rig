# Research brief: game asset pipeline, run 1

## 1. Mission

Find the best way for this agent studio (Codex seats doing the work, Claude
reviewing) to produce **real game assets** for a Godot 4 game on Steam: 2D
and 3D, consistent with one art bible, at production volume. Produce a
recommendation per asset type, backed by a small bake-off, so the owner can
approve one pipeline before production starts.

No game has been chosen yet. Assume either a 2D or a low-to-mid-fidelity 3D
game (stylized, low-poly or crude "friendslop" looks are all candidates).

## 2. Routes to compare (at least these)

1. **Codex image generation** (Codex's built-in image tools): concept art,
   2D sprites, UI, textures.
2. **Blender driven by agents:** Blender MCP servers and plain headless
   Blender Python scripting (`blender -b --python`), for modeling, UV,
   materials, rigging, simple animation, and export to glTF for Godot.
3. **Text/image-to-3D models:** hosted services and open-source models that
   can run locally on the owner's RTX 4080 SUPER (16 GB). Mesh quality,
   topology, texture quality, and whether output is game-ready.
4. **Local image generation on the 4080** (e.g. ComfyUI with open models and
   a style LoRA trained on the art bible) for consistent batches.
5. **Procedural generation in Godot** (shaders, CSG, code-drawn assets).
6. **CC0 asset libraries** as a baseline and filler (well-known CC0 game
   asset sites), including how far a game can get on them alone.
7. Any route the team finds that beats these.

## 3. Criteria per route, per asset type

Asset types: 2D sprites/characters, UI, tileable textures, 3D props, 3D
characters, character animation, VFX, environment pieces.

| Criterion | What a 5 looks like |
|---|---|
| Quality | Indistinguishable from a small indie team's work in that style |
| Consistency | 50 assets look like one game, given an art bible |
| Agent-drivable | A Codex seat can run it unattended from WSL, scriptable, no GUI clicking |
| Throughput | Dozens of assets per day |
| Cost | Free, or the monthly cost is stated from the vendor's own pricing page |
| Licensing | Commercial use clearly allowed, output ownership clear (cite the terms page) |
| Steam fit | Disclosure requirements understood and manageable (cite Steam's policy page) |
| Godot fit | Imports cleanly (glTF, PNG, atlases), sane poly counts and texture sizes |

## 4. Hard no's

- Spending money or creating accounts without an owner gate (a paid route
  can be *recommended* with its price; it can't be used in this run).
- Tools whose license forbids commercial use of output, or whose terms are
  unclear after reading them.
- Anything that needs the owner to click through a GUI per asset.
- Models or tools from unofficial mirrors; install only from official
  sources (pip, npm, GitHub releases of the project itself).

## 5. Evidence rules

Your usual research rules apply: every claim links to a page you opened;
prices from vendors' pricing pages with the date; licenses from the actual
license/terms text; **found** vs **inferred** labels; web access per
`briefs/RESEARCH-WEB-ACCESS-RULE.md` (v2).

## 6. Funnel

1. **Dry run** of the working path, as usual.
2. **Desk research:** a scored table of every route x asset type, with
   sources. Shortlist up to 4 routes for a bake-off.
3. **Gate 1** (`gate.json`, kind `choose`, min 1, max 4): which routes to
   bake off, with the free/local setup each needs and its disk/GPU needs.
   Stop and wait.
4. **Bake-off** (only approved routes, free tools only): every route makes
   the same three test assets from one shared mini art bible the lead writes
   (e.g. "chunky low-poly, flat colours, one accent colour"): a prop (a
   lantern), a character (a small explorer, rigged if the route can), and a
   tileable ground texture. Import each into a throwaway Godot project and
   capture a screenshot. Log time, steps and failures per route.
5. **Gate 2** (`gate.json`, kind `approve`, context = `recommendation.md`):
   the recommended pipeline per asset type, with the bake-off screenshots as
   option images, cost per month, licensing summary and the Steam disclosure
   text it implies. Stop and wait.

## 7. Deliverables

In the job folder: `routes.md` (scored table + sources), `bakeoff/<route>/`
(assets, screenshot, log), `recommendation.md` (pipeline per asset type,
setup steps a Codex seat can follow, risks), `sources.md`, `retro.md`, and
the two gates.

## 8. Operations and limits

- Runs as a Rig Console job in `~/openrig/research/assets-1/` with
  `job.json` (`{"type": "research", "rig": "assets-1", "title": "Asset pipeline research"}`).
  Use your standard research-team setup (lead, analysts, skeptic) with web
  access rule v2 and a dry run before dispatch.
- Installing free tools inside WSL for the bake-off is allowed after gate 1,
  from official sources only, into the job folder or `~/.local`. GPU work
  uses the owner's 4080; keep jobs that need it one at a time.
- Never spend money, create accounts, post publicly or contact anyone.
- Stop at both gates. If usage warnings appear: stop, save, report.
