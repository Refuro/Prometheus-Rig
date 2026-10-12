# Depth room brief (Track A), run 1

## 0. Owner settings (binding)

- **Platform:** PC (Steam). Web builds for prototypes.
- **Engine:** Godot 4, 2D or 3D. Single-player.
- **Price:** $2.99 minimum, no ceiling.
- **Scope: think in agent time.** The game is built by an agent studio
  working around the clock. Big, systemic, content-rich games are in bounds.
  Judge scope on what humans must do (playtest feel, approve art, hand-written
  story), not on code volume. Prototypes stay small.
- **Anti-list:** desk/paperwork judgment sims; writing-carried games; genre
  defaults with a pasted theme (roguelike deckbuilder, survivors-like, cozy
  farming, idle, match-3, Balatro-like, anomaly spotting); horror by default;
  meme-of-the-month games; multiplayer (another room covers that).

## 1. Mission

Find games with a **simple premise (wacky is welcome) and real depth**: one
rule a stranger gets in ten seconds that keeps producing new situations for
hours. The first round produced fun two-minute toys that were the same game
at minute 20. This round, a pitch is only as good as its *late game*.

Every pitch must imagine what's down the line: what new things appear, how
they combine with the old ones, and why hour five feels different from
minute five. Levels are one way to get there, not a requirement.

Zero board cards is acceptable. Never pad the board.

## 2. What makes a pitch good

Score each 1-5. **Depth and Exploit-proof are gates:** a card scoring 2 or
less on either cannot go on the board, whatever its other scores.

| Criterion | What a 5 looks like |
|---|---|
| Hook | One sentence makes a stranger say "wait, what?" |
| Clarity | Someone who has never seen it knows what to do within 30 seconds |
| Depth | The depth critic sketched 10 situations that each need a different idea |
| Exploit-proof | No dominant strategy trivializes it; the rule as written closes the obvious cheese |
| Variety engine | A clear, believable source of new content that won't run dry in a few hours |
| Novelty | The scout found nothing that plays this way |
| Watchability | Watching someone else play is funny, tense or satisfying |

Hard no's: existing IP, characters or real people; a named game with a
cosmetic twist; anything on the anti-list; needs licensed music, voice
acting or a big script; needs hardware beyond keyboard, mouse or controller.

## 3. Collision hands

Hands come from `deck.json` via `tools/draw_hands.py`: a **verb**, a
**setting**, a **rule seed** and a **growth engine**. Use all four, freely
reinterpreted. The growth engine is the card most pitches skip: it's the
answer to "what's down the line", so lean on it. A dead hand gets a one-line
note and a free pitch instead.

Each pitcher writes 5 hand pitches + 2 free pitches.

## 4. The pitch card

`pitches/<seat>-<nn>.md`, front matter plus body, **at most 400 words**.
`tools/check_pitches.py` enforces the shape (from `card-format.json`).

```markdown
---
id: b-03
title: Working Title
hand: [verb, setting, rule seed, growth engine]     # or [free]
hook: One sentence, max 20 words.
---
**What it is:** two sentences a stranger could repeat: the fantasy and the goal.
**The rule:** the one rule the whole game grows from.
**Loop:** what the player does every 30 seconds, and what they're trying to achieve.
**First five minutes:** what the player learns, step by step.
**Hour one:** what's new by now and how it combines with the basics.
**Late game:** one concrete late situation that would baffle a first-minute player.
**Variety engine:** where new content comes from, and roughly when it runs out.
**Exploit check:** the most obvious cheese, and how the rule shuts it down.
**Why watch:** what makes viewers yell at the streamer.
**Hand use:** how each of the four cards shows up.
**Prototype beats:** three short moments a prototype builds: early, middle, late.
**Look:** one line of gut-feel art direction.
**Risk:** the thing most likely to make it shallow or confusing.
```

## 5. The team

- **room-lead (Claude), curator.** Draws hands, dispatches, blinds, curates,
  writes the board and the gate. Does not pitch.
- **pitch-a, pitch-b, pitch-c (Codex).** 7 cards each, independently. Never
  read other pitchers' files, `returning/`, `blind/` or the board.
  `pitch-c` draws with `--strange`.
- **revise-cards (Codex).** Rewrites the ideas in `returning/` (owner-played
  prototypes from an earlier round) into this card format, answering the
  owner's notes. Writes `pitches/r-01.md` to `r-03.md` with `hand: [revised]`
  and `Hand use: none`. Must not mention prototypes, earlier rounds or the
  owner anywhere in the cards: they are judged blind against new pitches.
- **depth-critic (Codex).** Tries to break every card. For each blind card,
  writes `depth/<blind-id>.md`:
  - **Exploit hunt:** the dominant strategy or cheese the rule allows, and
    whether the card's own exploit check actually closes it.
  - **Ten situations:** ten one-line situations from early to late game,
    each needing a different idea from the player. If ten distinct ones
    won't come, say where it ran dry. That is the finding.
  - **Variety engine:** is it believable, and when would it run out?
  - **Clarity:** could a first-time player tell what to do in 30 seconds?
  - Scores for Depth, Exploit-proof and Clarity, one line of reasoning each.
- **scout-novelty (Codex).** For each blind card: Steam, itch.io and
  YouTube, max 3 searches; 1-3 nearest games with opened links; verdict
  **Fresh**, **Twist** (name the game and the difference) or **Exists**.
  Follows `~/openrig/briefs/RESEARCH-WEB-ACCESS-RULE.md` (v2). Writes
  `scout-novelty.md` and `sources.md`.

**Blind judging.** Once all cards are valid, room-lead runs
`python3 tools/blind.py --seed <n>`, which writes anonymous copies to
`blind/` and the key to `.blind-key.json`. The critic, the scout and the
curator judge from `blind/` only. **Nobody opens `.blind-key.json` until
`gate.json` is written.** After that, room-lead adds a "Reveal" table
(blind id → original card and seat) to the end of `board.md`.

## 6. Funnel

1. **Dry run.** One fake card through the whole path: draw, pitch, check,
   blind, critic note, scout line. Fix every permission prompt, then delete
   the dry-run files (including `blind/` and `.blind-key.json`).
2. **Draw and revise.** Lead draws 5 hands per pitcher with logged seeds
   (`lead-hands.md`) and dispatches; at the same time sends revise-cards
   its task. All four work in parallel.
3. **Check.** Lead runs `check_pitches.py`; invalid cards go back once.
4. **Blind.** Lead runs `blind.py`.
5. **Judge.** Depth critic and scout work through `blind/` in parallel.
6. **Curate.** Lead cuts hard no's, **Exists**, and anything failing the
   Depth or Exploit-proof gate; merges near-duplicates; scores; builds the
   board: up to 8 cards, at least 3 Fresh if that many survive. No per-seat
   quota this round: blind judging replaces it.
7. **Gate.** Lead writes `board.md` and `gate.json`, then stops and waits.
   Never ask in chat; never write a decision file.
   ```json
   {
     "title": "Pick depth pitches to prototype",
     "question": "Which should become three-beat prototypes?",
     "kind": "choose", "min": 2, "max": 5,
     "lead": "room-lead",
     "context": "board.md",
     "options": [
       {"id": "x-04", "title": "Working Title", "summary": "What it is, the late-game moment, the critic's verdict and biggest exploit risk, scout verdict.", "file": "blind/x-04.md"},
       {"id": "none", "title": "None of these: go again", "summary": "Fresh hands next round. Add notes."}
     ]
   }
   ```
8. **Reveal.** After writing the gate, add the Reveal table to `board.md`.
9. **After the decision** (`decisions/<gate-id>.json` + `rig send`): for each
   pick, write `proto-spec-<blind-id>.md`: what the game is (two sentences a
   stranger understands), the goal, how you win or lose, what every
   interactable does, controls, the **three beats** with what each one must
   prove, the exploit the prototype must not allow, out of scope, time box.
   Then stop.

If the decision is `none`: copy the owner's notes into `owner-notes.md`,
draw fresh hands, run steps 2-8 again (blind with `tools/blind.py --seed <n> --round 2`, which writes `blind-2/` with only the new cards) and open a new gate in `gates/`.

## 7. Deliverables

In this job folder: `pitches/`, `blind/`, `depth/`, `scout-novelty.md`,
`sources.md`, `lead-hands.md`, `board.md` (under 1,200 words: per card the
hook, what it is, scores, critic verdict, scout verdict, curator's case; then
also-rans with reasons; then the Reveal), `gate.json`, `proto-spec-*.md`
after the decision, and `retro.md`.

## 8. Operations

- Runs as a Rig Console job in `~/openrig/jobs/depth-1/` (`job.json`
  present). Fresh rig. Runs in parallel with the friendslop room; the two
  rooms never read each other's files.
- Before dispatch the operator pre-approves for every seat: `rig queue`
  commands and `python3 tools/*.py` inside the job folder.
- File prefixes: `lead-`, `scout-`, `depth/`, pitch files by seat letter.
- No `$`, backticks or pipes in shell text. Use `--body-file`.
- Optional progress events in `events.jsonl`.
- The operator acts only when messaged.

## 9. Limits

- Never spend money, create accounts, post, contact anyone, or download and
  run games.
- Stop at the gate. If usage warnings appear: stop, save, report.
- Two-exchange disagreement rule: write both positions into `board.md`.
