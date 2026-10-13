# Research brief: game asset pipeline, run 1 (v2)

## 1. Mission

Find the best way for this agent studio (Codex seats doing the work, Claude
reviewing) to produce **every kind of game asset** (art, models, animation,
UI, sound effects and music) for a Godot 4 game on Steam, at production
volume and **consistent with one art and audio bible**. Art direction makes
or breaks a game, so consistency across hundreds of assets matters as much
as the quality of any one. Produce a recommendation per asset type, backed
by a bake-off, so the owner can approve one pipeline before production
starts.

Two games are now in design (`~/openrig/jobs/bridge-design/` A Bridge Goes
Walking, a physics game; `~/openrig/jobs/sunrise-design/` Shovel the
Sunrise). Their art and audio directions are being drafted in
`art/directions/` in each job. Research general routes first; the bake-off
uses those directions (section 6).

## 2. Routes to compare (at least these)

Art and models:
1. **Codex image generation** (`$imagegen`): concept art, 2D sprites, UI,
   textures, reference sheets.
2. **Blender driven by agents:** Blender MCP servers and plain headless
   Blender Python (`blender -b --python`): modeling, UV, materials, rigging,
   simple animation, glTF export for Godot.
3. **Text/image-to-3D models:** hosted services and open models that run
   locally on the owner's RTX 4080 SUPER (16 GB). Mesh quality, topology,
   textures, whether output is game-ready.
4. **Local image generation on the 4080** (e.g. ComfyUI with open models
   and a style LoRA trained on approved assets) for consistent batches.
5. **Procedural generation in Godot** (shaders, CSG, code-drawn assets).
6. **CC0 asset libraries** as baseline and filler.

Audio:
7. **Procedural and tool-made sound effects** (free sfxr-style generators,
   synthesis in code or in a scriptable audio tool).
8. **AI sound-effect and music generators**, hosted and local. Licence
   terms and commercial-use rights are the first filter: many open music
   model weights are non-commercial. Read the actual terms.
9. **Music made by agents with tools** (tracker or MIDI composition
   rendered with free instruments and soundfonts).
10. **CC0 and royalty-free audio libraries** (licence per file).
11. **A human composer or sound designer** as a priced option for the
    owner (rates from public sources only; no contact). Music carries a
    game's identity; the owner should see this option next to the AI
    routes.

12. Any route that beats these.

## 3. Criteria per route, per asset type

Asset types: 2D sprites/characters, UI, tileable textures, 3D props, 3D
characters, character animation, VFX, environment pieces, sound effects,
music, ambience.

| Criterion | What a 5 looks like |
|---|---|
| Quality | Indistinguishable from a small indie team's work in that style |
| **Consistency** | 50 assets look and sound like one game, given an art and audio bible; the route has a way to lock style (reference images, seeds, LoRA, shared materials and shaders, shared instruments and mix) |
| Agent-drivable | A Codex seat can run it unattended from WSL, scriptable, no GUI clicking |
| Throughput | Dozens of assets per day |
| Cost | Free, or the monthly cost is stated from the vendor's own pricing page |
| Licensing | Commercial use clearly allowed, output ownership clear (cite the terms page) |
| Steam fit | AI-content disclosure understood and manageable (cite Steam's policy page) |
| Godot fit | Imports cleanly (glTF, PNG, atlases, OGG/WAV), sane poly counts, texture sizes and loudness |

## 4. Hard no's

- Spending money or creating accounts without an owner gate (a paid route
  can be *recommended* with its price; it can't be used in this run).
- Tools whose licence forbids commercial use of output, or whose terms are
  unclear after reading them.
- Anything that needs the owner to click through a GUI per asset.
- Models or tools from unofficial mirrors; install only from official
  sources (pip, npm, GitHub releases of the project itself).
- Imitating a named living artist's or composer's style, or existing game
  IP.

## 5. Evidence rules

Your usual research rules apply: every claim links to a page you opened;
prices from vendors' pricing pages with the date; licences from the actual
licence/terms text; **found** vs **inferred** labels; web access per
`briefs/RESEARCH-WEB-ACCESS-RULE.md` (v2).

## 6. Funnel

1. **Dry run** of the working path, as usual.
2. **Desk research:** a scored table of every route x asset type, with
   sources. Shortlist up to 4 art routes and up to 3 audio routes.
3. **Gate 1** (`gate.json`, kind `choose`, min 1, max 7): which routes to
   bake off, with the free/local setup each needs and its disk/GPU needs.
   Stop and wait.
4. **Bake-off** (approved routes, free tools only). If either design job
   has a chosen art direction (`decisions/art-direction.json`) use it;
   otherwise use its two leading directions from `art/directions/`. Read
   them; never edit design job files. Per route and game:
   - **Art:** three test assets (a key prop, a character or the game's
     main object, a tileable ground or background), imported into a
     throwaway Godot project and screenshotted. 3D assets also get a
     turntable PNG or WebM (the console shows these as `model_preview`).
   - **Consistency test:** then **ten more assets** in the same style
     through the same route, rendered as one **lineup image** (all assets
     side by side, same lighting and scale). This is the test that matters:
     does it still look like one game at asset 13?
   - **Audio:** five sound effects for the game's core actions (from its
     feel doc's action table if present) and one 60-90 s music loop in the
     direction's described mood, loudness-normalised, OGG.
   Log time, steps, failures and the style-lock method per route.
5. **Gate 2** (`gate.json`, kind `approve`, context = `recommendation.md`):
   the recommended pipeline per asset type per game, with lineup images as
   option `image`, a music sample as option `audio` and a 3D turntable as
   `model_preview` where relevant (console request R-012), cost per month, licensing summary,
   the Steam disclosure text it implies, and the human-composer option
   priced next to the audio recommendation. Stop and wait.

## 7. Deliverables

In the job folder: `routes.md` (scored table + sources),
`bakeoff/<game>/<route>/` (assets, lineup, audio, log), `recommendation.md`
(pipeline per asset type; setup steps a Codex seat can follow; the
**consistency kit** each route needs: reference sheets, prompt and seed
recipes, LoRA or material library, palette files, instrument and mix
settings; risks), `asset-manifest-format.md` (start from
`~/openrig/studio/briefs/asset-manifest.md` v0, which the console already
reads, and propose changes only where the bake-off shows a need; keep a
`bakeoff/assets/manifest.json` in that format yourselves), `sources.md`, `retro.md`, and the two gates.

## 8. Operations and limits

- Runs as a Rig Console job in `~/openrig/research/assets-1/` with
  `job.json` (`{"type": "research", "rig": "assets-1", "title": "Asset pipeline research"}`).
  Use your standard research-team setup (lead, analysts, skeptic) with web
  access rule v2 and a dry run before dispatch.
- Installing free tools inside WSL for the bake-off is allowed after gate 1,
  from official sources only, into the job folder or `~/.local`. GPU work
  uses the owner's 4080; keep jobs that need it one at a time.
- Never spend money, create accounts, post publicly or contact anyone.
- Stop at both gates. Other stops and retries: `briefs/SHARED-RULES.md`.
