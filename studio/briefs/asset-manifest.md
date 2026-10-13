# Asset manifest format, v0 (Studio Architect, 2026-10-12)

One manifest per job that makes assets: `<job>/assets/manifest.json`. The
console's Assets tab reads it (R-013); production uses it for licence audits
and Steam's AI-content disclosure. The asset research job (assets-1) may
propose v1; until then, use this.

```json
{"version": 0,
 "assets": [
  {"id": "prop-lantern-01",
   "type": "sprite | ui | texture | prop3d | character3d | animation | vfx | environment | sfx | music | ambience | concept",
   "file": "art/props/lantern-01.png",
   "preview": "art/props/lantern-01.png",
   "model_preview": "art/props/lantern-01-turntable.webm",
   "title": "Lantern",
   "set": "world-1",
   "status": "concept | candidate | approved | in-game | rejected",
   "route": "codex-imagegen | blender-script | local-sd | procedural | cc0 | human | other",
   "tool": "name and version",
   "recipe": "prompt, script path or seed (enough to make another in the same style)",
   "ai_made": true,
   "licence": "own | CC0 | <licence name + URL>",
   "source_url": null,
   "made": "2026-10-12",
   "by": "art-director",
   "reviewed_by": null,
   "notes": ""}
 ]}
```

Rules:
- Paths are relative to the job folder. `preview` is a PNG/WebP/GIF for
  images; for audio leave it null (the console plays `file`); for 3D,
  `model_preview` is a turntable PNG or WebM (no live viewer in v1).
- Every asset that enters a build has a record. `ai_made` and `licence` are
  required; nothing with an unclear licence reaches `approved`.
- `status` moves forward only through review: concept → candidate (made
  for the bible or a batch) → approved (passed the lineup review) → in-game.
- The owner's notes on an asset live in `notes/asset-<id>.md` (written by
  the console, R-013), never in the manifest.
