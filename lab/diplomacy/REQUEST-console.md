# Draft console requests for `dashboard/REQUESTS.md` (Platform owns that file; the owner or Rig Architect files these)

## R-0xx Diplomacy board page: adopt `lab/diplomacy/console/diplomacy.html`, wire `/api/lab/control`
**What:** the page is built and tested (`lab/diplomacy/PLATFORM-NOTES.md` has the contract). Needed from the
console: one owner-only POST that flips `paused`/`stop` in `<job>/board/control.json`; a nav entry under More;
smoke checks against `lab/diplomacy/console/fixture/`. Reads already work through `/job/<job>/...`.
**Why:** the owner watches the game and pauses it from the console, on desktop and phone.
**Not asked:** anything that lets the console send press or orders, or read sealed intentions during play.

## R-0yy Queue message bodies in the snapshot mirror
**What:** `_queue.json` keeps rows without bodies, so seat-to-seat messages aren't in the mirror (MA-013 had
to read them live). Proposal: the logger runs `rig queue show <id> --full --json` for each row it hasn't
seen, under the PL-015 timeouts, and writes `snapshots/_queue_bodies.jsonl` (append-only, id-keyed).
**Why:** the Model Architect verifies quotes from the mirror; the owner can read what agents say to each
other; any future game or team with press gets observed for free. Not needed for Diplomacy game 1 (press is
in files), so low priority.
