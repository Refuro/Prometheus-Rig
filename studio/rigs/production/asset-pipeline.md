# Approved asset pipeline: [game]

[The Studio Architect fills this in before any art or audio work and replaces this line. Until then, no
asset batch starts.]

**What the owner approved:** [gate id, date, note] (`[path to decisions/<gate>.json]`), covering
`[path to the asset research recommendation]`. Read that file whole before the first batch; where this
page and it differ, the recommendation and the owner's notes win.

## Route per asset type
| Asset type | Route | Notes |
|---|---|---|
| | | |

Anything not listed (a tool, a download, a paid service, local AI models) is not approved: ask the owner
through the tech lead.

## Consistency kit (minimum)
[the design job's `data/art/` files, plus the research's kit list]

## Records
Every asset gets a v1 record in `game/assets/manifest.json` (`~/openrig/studio/briefs/asset-manifest.md`),
including `ai_role`. Every AI-made asset is also logged in `ai-content-log.md`.
