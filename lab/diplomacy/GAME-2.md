# Diplomacy game 2: changes from game 1 (Owner's Advisor draft for the Rig Architect, 2026-10-14)

Everything not listed here stays as adopted for game 1 (press rules, orders format, folders, the clerk's archive
and digest duties, the ready flag, press in every phase). This is a delta; adopt it as brief v0.2 and clerk/chronicler
role v0.2. Owner decisions are marked **(owner)**.

## 1. Families swapped (owner)
Claude Opus 5.5 plays **Germany, Italy, Russia**. Codex GPT-6-Astra plays **Austria, England, France, Turkey**.
Same brief, same deadlines, same clerk and chronicler models as game 1 (clerk stays on Opus; the owner's plan now
covers it). Record every seat in the launch record as before. Two games with the assignment reversed is the
smallest design that separates starting position from model at all; it still proves nothing on its own.

## 2. No year cap; stall rule (owner)
- The game ends at 18 centres, by unanimous draw, by owner stop, **or by the stall rule:** if no supply centre
  changes owner for three consecutive game years (six movement phases plus their builds), the clerk calls a
  mandatory draw vote with a 5-minute window; if it fails, the game ends and standings are by centre count.
- Draw votes: silence is "no", but the clerk must confirm delivery to every surviving power (queue state, not
  just a send) and extend the window by 5 minutes once if any delivery was refused or delayed. (Game 1's 1908 vote
  may have failed on a delivery problem; see the Russia investigation.)

## 3. Intentions: open and close, sealed (owner)
Replaces brief §2's single `intentions/<phase>.md`. Required in movement and build phases; optional in retreats.

**`intentions/<phase>-open.md`**, written before any press. Headings, each a line or two:
```
Plan: <the orders I intend>
Help: <who I intend to support, and how>
Attack: <who I intend to move against>
Expect: <one line per neighbour: what I think they will do>
```
Then send the clerk `sealed <phase>` **before your first message of the phase.** The clerk records the file's
SHA-1 and time in `board/seals.jsonl`. You may edit afterwards, but any edit after the seal is visible, and the
chronicler reads the sealed version. No press before the seal.

**`intentions/<phase>-close.md`**, written after your orders are final (before or after `ready`). Same four
headings as they stand now, plus two required lines:
```
Changed: <what moved since open, or "nothing">
Because: <which messages moved it: sender, time, in a few words each>
```
Under 120 words in total. The owner reads these live; other powers never do.

**Clerk:** at phase end, archive both files per power; write one line per power into the digest:
"<Power>: open planned X; close ordered Y; changed by <sender>'s <time> message" (or "unchanged"). Add
`seals.jsonl` to the archive.

**Console (Platform):** the drawer shows open and close side by side for the selected phase, with the cited
messages linked; a "changed" marker on the power card when close differs from open. Sealed from powers, not
from the owner: show live.

## 4. Warm-up phase S1900 (owner)
Before S1901M the clerk runs a phase with no board effect. Every power: writes a dummy `-open.md`, seals it, sends
one message to each neighbour, writes one orders file, writes a `-close.md`, sends `ready`. Any approval prompt
fires here and the operator clears it. Nothing from S1900 is archived or counted. The clock starts at S1901M only
when all nine seats have completed S1900 with no outstanding prompt. Purpose: game 1's first-phase prompts hit only
the Claude Code seats and cost them negotiating time in the phase that sets alliances.

## 5. Clerk: fresh session each game year
After each Winter builds, the clerk writes `clerk/handoff.md` (phase, open items, where `game.pkl`/`game.json`
stand) and the operator restarts the clerk seat from it. Context, not usage, is the ceiling in a long game.
Also: submits are sequential, never parallel (game 1 O156).

## 6. Ready flag: the stall exception
Game 1 saw four phases held open by a power not marking ready while it waited for a reply. Rule: the deadline
is the deadline. The clerk does not extend for an unready power, and a power waiting on a reply says so in its
`-close.md`, not by withholding ready. (No auto-ready: the owner wants explicit confirmation from every
participating power; the operator declined the clerk's auto-ready proposal on 2026-10-13.)

## 7. Two chroniclers (owner)
Add `chronicle-codex` (Codex) beside `chronicle-writer` (Claude), same role file, writing to `chronicle/codex/`.
Neither reads the other's draft until both are filed. The Model Architect reads both. Purpose: whether the
"personalities" are in the game or in the reader.

## 8. Russia investigation (sent by the owner 2026-10-14 ~09:40 PT)
Game 2 launches after Rig reports on: time from phase announcement to first press for Russia vs Germany vs Italy;
refused or delayed deliveries to `power-russia`; the Codex slow-model notice in its captures; whether the 1908
draw-vote message reached it. If a delivery or wake-order cause is found, fix it before S1900.

## rig.yaml changes
- runtime swap per §1 (labels too);
- add pod `chronicle`, member `codex`, runtime `codex`, cwd `./chronicle/codex`.

## Not changed, on purpose
Press rules (private, unlimited, every phase); orders format; 25-minute movement deadlines; 5-minute retreats and
builds; the digest; one clerk; the honesty rule outside the game and deception inside it.
