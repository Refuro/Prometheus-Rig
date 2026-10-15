# Asset manifest format, v1 (Studio Architect, 2026-10-14)

One manifest per job that makes assets. The console's Assets tab reads `<job>/assets/manifest.json`
(R-013). Production keeps it in `game/assets/manifest.json`, and milestone builds copy it to
`<job>/assets/manifest.json`. Production also uses it for licence audits and for Steam's AI-content
disclosure.

v1 adopts the assets-1 proposal (`~/openrig/research/assets-1/asset-manifest-format.md`), which keeps
every v0 field. v0 manifests stay valid: a missing v1 field reads as null, and a missing `kind` reads as
`asset`.

```json
{"version": 1,
 "game": "bridge",
 "assets": [
  {"id": "prop-wagon-01",
   "type": "sprite | ui | texture | prop3d | character3d | animation | vfx | environment | sfx | music | ambience | concept",
   "kind": "asset | evidence | archived",
   "file": "game/art/props/wagon.tscn",
   "preview": "game/art/props/wagon.png",
   "model_preview": null,
   "title": "Wagon",
   "set": "reach-1",
   "direction": "river-collage",
   "status": "concept | candidate | approved | in-game | rejected",
   "route": "codex-imagegen | blender-script | local-sd | procedural | cc0 | human | other",
   "tool": "Godot 4.7.1 + game/art/recipes/props.json",
   "tool_version": "4.7.1.stable.official | unknown",
   "recipe": "game/art/recipes/props.json#wagon",
   "seed": null,
   "prompt": null,
   "references": [],
   "ai_made": true,
   "ai_role": "generated image | agent-written code/recipe | human | CC0 third-party",
   "licence": "own | CC0 | <licence name + URL>",
   "source_url": null,
   "source_licence_file": null,
   "made": "2026-10-14",
   "by": "art-production",
   "reviewed_by": null,
   "evidence": [],
   "notes": ""}
 ]}
```

## Fields added in v1
| Field | Why |
|---|---|
| `kind` | Screenshots and captures were mixed in with real assets in the bake-off (103 of 128 records weren't assets). Audits and the disclosure count only `kind: asset`. |
| `direction` | Assets from a superseded art direction stay recorded but don't count. |
| `tool_version` | Tool provenance matters (the bake-off found a Godot binary of unknown origin). |
| `seed`, `prompt`, `references` | Split out of `recipe`, so a seat can make another asset in the same style. |
| `ai_role` | Steam's disclosure asks how AI was involved, not just whether. |
| `source_licence_file` | CC0 or third-party assets keep the licence text the audit relied on. |
| `evidence` | Links an asset to its capture or review record (e.g. `milestones/m2/reviews/art-b1.md`). |

## Rules
- **Paths are relative to the job folder,** including in production (`game/...`), because the build
  copies the file to `<job>/assets/` unchanged.
- `preview` is a PNG, WebP or GIF for images. For audio it is null (the console plays `file`). For 3D,
  `model_preview` is a turntable PNG or WebM.
- **Required fields:** `ai_made`, `ai_role` and `licence`. Nothing with an unclear licence reaches
  `approved`.
- **Records:** every asset that enters a build has one. `kind: evidence` records never reach
  `approved`; they exist for provenance.
- **Status** moves forward only through review: `concept` → `candidate` (made for the bible or a batch)
  → `approved` (passed the lineup review) → `in-game`.
- **One writer at a time:** in production, `art-production` edits the manifest on its batch branch and
  the merge brings it into main. A job with several art seats writes `manifest-<seat>.json` fragments,
  and the lead merges them.
- **Owner notes:** the owner's notes on an asset live in `notes/asset-<id>.md` (written by the console,
  R-013), never in the manifest.
