# Prototype art style (placeholder, readable)

Goal: the player can tell what every thing is from its shape and colour alone.

- **Shapes:** flat SVG silhouettes, 2-4 px dark outline (#11141c), no gradients,
  no text inside art. A boat looks like a boat; a bridge looks like a bridge.
- **Palette roles (keep consistent):** background #1d2230, ground #3b4256,
  player/controllable #f2c14e (it should be the warmest thing on screen),
  goal #7bd389, danger #e4572e, neutral objects #c9ccd5. One accent per
  new mechanic, introduced with it.
- **Size:** author at 2x the on-screen size (e.g. 96x96 for a 48 px object).
- **One file per thing:** art/<thing>.svg, lowercase names.
- **Generated images** (Codex $imagegen) only for the few key objects where an
  SVG can't read clearly; max 8 per prototype; flat style matching these
  colours; transparent background; log each in ai-content-log.md.
