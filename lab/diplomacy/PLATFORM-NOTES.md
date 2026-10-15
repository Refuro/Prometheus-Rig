# Notes for the Platform Architect (from the Owner's Advisor, 2026-10-13; the owner asked me to build this page)

The owner told you an outside agent built a Diplomacy addition. This is it. You own `dashboard/`; nothing here
was written there. Adopt `console/diplomacy.html` into `dashboard/` as you see fit (rename, restyle, split).

## What the page needs from the console
1. **Nothing new for reads.** It fetches `/job/<job>/board/*.json|.svg|.md`, `/job/<job>/archive/<phase>/...` and
   `/job/<job>/powers/<p>/press/sent.jsonl` through your existing `translate_path` `/job/` route. The job is
   `~/openrig/jobs/diplomacy-1` (type `lab`). If `safe_path` restricts which job types or paths are servable,
   `lab` jobs need the whole job folder readable except nothing sensitive lives there.
2. **One POST, `/api/lab/control`**, body `{"job": "<job>", "paused": true|false}` or `{"job": "<job>", "stop": true}`.
   Owner cookie plus `X-Rig-Console: 1`, same as `/api/task`. It read-modify-writes `<job>/board/control.json`,
   changing only `paused` / `stop` (the clerk owns `phase`, `state`, `deadline`), and answers `{"ok": true, "note":
   "..."}`. No notification; the clerk polls the file. Refuse if the job folder has no `board/control.json`
   (game not started). Suggested: write to a temp file and rename, since the clerk may read mid-write.
3. **Nav:** under More, "Diplomacy", shown only when a `lab` job with `board/control.json` exists (or always; your call).
4. **Smoke checks:** `console/fixture/` is a job folder you can drop under the test watch root (it lacks the SVGs;
   copy any SVG to `board/S1901M.svg` and `board/F1901M.svg`, the page only needs a 200). Suggested checks: the page
   loads; `/api/lab/control` without the cookie is 401; with it, `paused` flips and `phase` is untouched; `stop` sets
   `stop`; a job without `control.json` is refused.

## Things I decided that you may want to change
- The board is an `<img>` of agent-written SVG, never inlined. Keep that: the renderer's SVG carries `<script>`-free
  markup today, but the clerk is an agent.
- Live press during an open phase comes from seven small `sent.jsonl` fetches every 20 s. Cheap, but if you'd rather
  have one file, have the clerk merge them; the page already prefers `archive/<phase>/press.jsonl` when it exists.
- Sealed intentions are only read when `board/final.md` exists. Please don't add a route that exposes
  `powers/*/intentions/` during play; it would make the owner a channel.
- Power colours are CSS variables on `:root` (`--AUSTRIA` ...), set to the engine's own palette from
  `standard.svg` so the cards match the board. Germany's tan is low-contrast on the light theme; your call.
- Phone: the map scales down and is legible at 390 px; the drawer is full width there.

## Licence
The adjudicator (`pip install diplomacy`) is AGPL-3.0. Nothing from it is copied into this repo: the clerk calls
it at run time on the PC and its rendered SVGs are data in the job folder. `map.json` here is adjacency data I
derived and verified from its `standard.map` (facts, not code). Keep it that way; don't vendor its SVG or source.

## What I verified
- `map.json`: 75 provinces + Switzerland (impassable) + 6 coasts, 34 supply centres, 0 asymmetric adjacencies,
  St Petersburg / Spain / Bulgaria coasts match the rulebook. Derived from the engine's own map file.
- The page: headless Chromium, 1280 px light and 390 px dark, phase switch, power drawer, chart, results, no JS errors
  (404s for optional files are expected and handled).
- Not verified: `tools/adjudicate.py` against the installed package (no network here). The clerk's dry run does that.

## Addition 2026-10-13 15:45 (owner request): pending orders per power
`console/diplomacy.html` now shows each power's orders as currently written for the open phase, under its card
(monospace, tagged "pending" while the phase is open; "no orders written yet (holds)" if the file is missing), and
at the top of the power drawer. Source: `powers/<p>/orders/<phase>.txt` live, falling back to
`archive/<phase>/orders/<p>.txt` after adjudication. Seven small reads per refresh, same as `sent.jsonl`.
Owner-only by construction (powers never see the console). Please merge into your copy; the diff is confined to
`loadPhase`, `renderPowers`, `openPower` and three CSS rules. Tested against the fixture.

## Addition 2026-10-13 15:50 (owner request): conversations inside the power drawer
The drawer's press section is now webDiplomacy-style: a chip row (All, then each other power in its colour, with
counts), and the selected pair's thread across every phase as two-sided bubbles (the drawer's power on the right,
the other on the left, each bubble edged in the sender's colour; broadcasts marked "to everyone"; phase dividers).
Reads every phase's `archive/<phase>/press.jsonl` plus the live `sent.jsonl` files when the drawer opens. Diff is
confined to `openPower` and CSS. Tested against the fixture.

## Addition 2026-10-13 15:55 (owner): Press tab is a plain feed; both names coloured
The Press tab's "as conversations" view is gone (pairs live in the drawer now). Each feed line shows sender and
recipient each with their own dot and colour. Diff: `msgHtml`, the press branch of `renderPanel`, one CSS rule.

## Fix 2026-10-13 16:00 (owner): no more flicker on refresh
The 20 s poll now re-renders only when a fingerprint of the data changed, restores scroll position, swaps the
board `<img>` only when the SVG's Last-Modified/ETag/length changed (no cache-buster on every tick), and skips
polling while the drawer is open or the tab is hidden (refreshes on return). Countdown still ticks every second.
Diff: `loadPhase` (board stamp), `renderAll`/`fingerprint`, the two handlers that call `renderAll(true)`, the
interval. If your copy serves `/job/` files without Last-Modified, the stamp falls back to content-length.
