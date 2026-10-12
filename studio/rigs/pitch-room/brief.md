# Pitch room brief, run 1

## 0. Owner settings (binding)

- **Platform:** PC (Steam). Web builds for prototypes are welcome.
- **Engine:** Godot 4, 2D or 3D.
- **Price:** $2.99 minimum, no ceiling. A bigger, deeper game can price
  higher; don't shrink an idea to fit a cheap price.
- **Scope: think in agent time, not human time.** The game will be built by
  an agent studio working around the clock. Your instinct for "how long
  would this take" is calibrated on human teams and runs long, so be
  generous: systems-heavy, content-heavy or simulation-heavy ideas are in
  bounds. Don't cut an idea for size alone. What still costs real time is
  what humans must do: playtesting by feel, approving art, and anything
  needing hand-crafted writing. Judge scope on those, not on code volume.
  Prototypes still stay small: one day, one question.
- **Anti-list (curator's defaults, owner-approved):** cut or heavily
  discount pitches that are:
  - desk, paperwork or inspection judgment sims (stamp/approve/deny loops);
  - mainly carried by writing: branching narrative, dialogue-heavy, lore-first;
  - a genre default with a theme pasted on: roguelike deckbuilder,
    survivors-like, cozy farming/life sim, idle/incremental, match-3,
    Balatro-like score chaser, walking-sim horror, "anomaly spotting";
  - horror by default (horror is fine only if the core rule is the scary
    part, not the setting);
  - built on a meme or trend that will be stale in six months.
- **Owner curiosity:** none set. Pitchers follow the deck.

## 1. Mission

Invent original game premises and put about 10 of the best on a board for
me to pick 3. Those 3 become one-day playable prototypes, so a pitch is only
as good as the toy it implies. Originality and a hook I can feel in ten
seconds matter more than polish or market proof.

Inspiration is games like Needle in a Haystack: one absurd rule taken
completely seriously, instantly legible in a clip, fun to watch someone else
struggle with. Use that as a reference point for tone and legibility, not as
a template to copy.

Zero pitches I love is an acceptable outcome. Never pad the board.

## 2. What makes a pitch good

Score each 1-5. Scores are advisory: they order the board, they don't decide
it. The curator explains any card it ranks against its score.

| Criterion | What a 5 looks like |
|---|---|
| Hook | One sentence makes a stranger say "wait, what?" and want to try it |
| Clip test | A 10-second silent clip shows the whole idea with no explanation |
| Toy-ability | The fun core can be built as a grey-box toy in one day (the full game can be big) |
| Novelty | The scout found nothing that plays the same way |
| Watchability | Watching someone else play it is funny, tense or satisfying |
| Depth | There is a clear way the hundredth minute differs from the first |

Hard no's (a card with any of these is cut):
- Uses an existing franchise, character, brand or real person.
- Is a named existing game with a cosmetic twist (the twist must change the
  core verb or the win condition).
- Depends on multiplayer networking, user accounts, live servers, or
  user-generated content moderation.
- Needs licensed music, voice acting, or a large written script to work.
- Anything on the owner's anti-list in section 0.
- Needs hardware beyond keyboard, mouse, controller, microphone or webcam.
  (Mic/webcam/desktop/clock inputs are allowed and encouraged as odd inputs,
  but the game must still be playable if the player declines permission.)

## 3. Collision hands

Every pitch starts from a hand drawn from `deck.json`
by `tools/draw_hands.py`: one card each of **verb**, **setting**,
**constraint**, and **twist input**. A pitcher may reinterpret any card
freely (a "funeral" can be a metaphor) but must use all four in some form
and say how in the card. A hand that truly produces nothing gets a one-line
"dead hand" note instead of a forced pitch.

Each pitcher also writes **2 free pitches** with no hand: whatever it
thinks is its single most original idea.

## 4. The pitch card

One markdown file per pitch at
`pitches/<seat>-<nn>.md`, front matter plus body, **at most
250 words of body**. `tools/check_pitches.py` enforces the shape.

```markdown
---
id: b-03                 # seat letter + number
title: Working Title
hand: [dig, wedding, one button, system clock]   # or [free]
hook: One sentence, max 20 words.
---
**Ten-second clip:** what a silent clip shows, frame by frame.
**The rule:** the one absurd rule the game takes seriously.
**Loop:** what the player does every 30 seconds.
**Minute 100:** how it deepens or escalates.
**Why watch:** what makes viewers yell at the streamer.
**Hand use:** how each of the four cards shows up.
**Prototype question:** the one question a one-day toy answers.
**Look:** one line of gut-feel art direction.
**Risk:** the thing most likely to make it not fun.
```

## 5. How the team works

- **room-lead (Claude), curator.** Draws hands, dispatches, merges, scores,
  builds the board. Does not pitch. Keep messages short: Claude usage is the
  scarce budget.
- **pitch-a (Claude), pitch-b (Codex), pitch-c (Codex).** Each gets 5 hands
  and writes 5 hand pitches + 2 free pitches (7 cards, 21 total).
  **Pitchers never read another pitcher's files** and never read the board
  until it is published. `pitch-c` draws from the deck with `--strange`
  (heavier weighting on odd inputs and constraints).
- **scout-novelty (Codex), novelty check.** For each card: search Steam, itch.io and
  YouTube for games that play the same way. Report the 1-3 nearest with
  links and one line on how close each is, then a verdict:
  - **Fresh:** nothing found that plays this way.
  - **Twist:** a known game shares the premise, but this changes the core
    verb or win condition (name the game and the difference).
  - **Exists:** a game already does this. Cut.
  Evidence rules: link only pages actually opened. Follow
  `~/openrig/briefs/RESEARCH-WEB-ACCESS-RULE.md` (v2). Max 3 searches per card; this
  is a sanity check, not a research run.

## 6. Funnel

1. **Dry run.** One fake card through the whole path: lead draws a hand,
   a pitcher claims it, writes a card, runs `check_pitches.py`, hands back;
   scout checks it and writes a line. Fix every permission prompt before
   dispatch.
2. **Draw.** Lead runs `draw_hands.py` once per pitcher with a logged seed
   (5 hands each), writes `lead-hands.md`, dispatches.
3. **Pitch.** Pitchers write their 7 cards and hand back. All three work in
   parallel.
4. **Novelty.** Lead sends every valid card to `scout-novelty`, which writes
   `scout-novelty.md` (one section per card id).
5. **Curate.** Lead cuts hard no's and **Exists**, merges near-duplicates
   (keep the stronger card, credit both), scores, and builds the board:
   - about 10 cards (fewer is fine, never more than 12);
   - at least 2 cards from each pitcher if that many survive the cuts;
   - at least 3 **Fresh** cards if that many exist.
6. **Gate.** Lead writes `board.md`, then the decision gate `gate.json`
   (format: `~/openrig/dashboard/JOBS.md` section 4), and **stops and waits**.
   Never ask for the decision in chat, and never write the decision file.
   ```json
   {
     "title": "Pick pitches to prototype",
     "question": "Which pitches should become one-day prototypes?",
     "kind": "choose", "min": 3, "max": 6,
     "lead": "room-lead",
     "context": "board.md",
     "options": [
       {"id": "a-06", "title": "Long Exposure", "summary": "One paragraph: hook, rule, why it made the board, scout verdict.", "file": "pitches/a-06.md"},
       {"id": "none", "title": "None of these: go again", "summary": "Start round 2 with fresh hands. Add notes on what you liked and didn't."}
     ]
   }
   ```
   One option per board card, in board order, plus the `none` option.
7. **After the decision** (it arrives as `decisions/<gate-id>.json` plus a
   `rig send`): for each chosen card, lead writes `proto-spec-<id>.md` (one
   page: the prototype question, what "done" looks like, controls, explicitly
   out of scope, a one-day time box). Then stop. Stage 2 is a separate rig.

If the decision is `none`: lead copies the owner's note into
`owner-notes.md`, draws fresh hands with a new seed, runs steps 3-6 again as
round 2 in the same folder (new card numbers continue from the last), and
opens a new gate with a new id in `gates/`. Pitchers read `owner-notes.md`
before round 2.

## 7. Deliverables

All in the job folder (this folder):
- `pitches/*.md`: every card, including cut ones.
- `lead-hands.md`: every hand, its seed and who got it.
- `scout-novelty.md`: nearest games and verdict per card.
- `gate.json`: the decision gate (step 6).
- `board.md`: the readable board behind the gate. For each board card: title, hook, pitcher
  (seat and model), scores, scout verdict with nearest game, and the
  curator's one-line case for it. Then a short "also-rans" list (title, hook,
  why cut). Under 1,000 words total.
- `sources.md`: every link the scout opened, with date.
- `retro.md`: phase times, waits and why, unclear rules, what to change.

## 8. Operations

- This folder is a Rig Console job: run it from `~/openrig/jobs/pitch-N/`
  with `job.json` present. Launch as a fresh rig named after the folder.
  Don't reuse research seats.
- Optional: append one-line progress events to `events.jsonl` (JOBS.md
  section 3), e.g. `{"kind": "cards", "seat": "room-lead", "text": "21 cards in"}`.
- Before dispatch, the operator pre-approves for every seat: `rig queue`
  commands, and `python3 tools/draw_hands.py` / `python3
  tools/check_pitches.py` inside the rig root. Lifecycle commands still ask.
- File prefixes: `lead-`, `scout-`, and pitch files named by seat letter.
- No `$`, backticks or pipes in shell text. Use `--body-file` for free text.
- The lead parks its goal row on the rows it dispatches.
- The operator does not monitor the run; it acts only when messaged.

## 9. Limits and stop rules

- Never: spend money, create accounts, sign up, post publicly, contact
  anyone, or download/run game builds from the web.
- Stop and wait at the gate. Never write a decision file yourself.
- If usage-limit warnings appear: stop, save progress, report.
- If two seats disagree and can't settle it in two exchanges: write both
  positions into `board.md` and let me decide.
