# Friendslop room brief (Track B), run 1

Shared rules first: every seat follows `~/openrig/briefs/SHARED-RULES.md`
(decisions and gates, when to stop, provider-capacity retries, shell
commands, the outside world, run start and end, end-of-run model notes).
This brief adds studio rules on top; where it is stricter, it wins.

## 0. Owner settings (binding)

- **Genre:** "friendslop": cheap-to-play online co-op for 2-4 friends where
  the comedy comes from the friends (Lethal Company, Content Warning,
  R.E.P.O., Peak are the reference points for the *genre*, not templates).
- **Platform:** PC (Steam). Online co-op, 2-4 players; playable by a smaller
  group than the max. Proximity voice chat is assumed.
- **Engine:** Godot 4, usually 3D. Crude, low-fi looks are fine and fit the
  genre.
- **Networking (for planning):** prototypes use Godot's built-in ENet with a
  host/join-by-address screen; friends join over Tailscale. The real game is
  built from scratch later on Steam networking (GodotSteam). Pitches don't
  need to solve networking, but must name their netcode risk.
- **Price:** $2.99 minimum, no ceiling. Most of the genre sits at $5-10.
- **Scope: think in agent time.** Judge scope on what humans must do. The
  big human cost here is playtests, which need the owner plus 2-3 friends.
- **Anti-list:** "horror co-op but X" with no new verb; a reskin of a named
  hit; competitive/ranked/esports; anything needing dedicated servers,
  persistent worlds, accounts, or more than 4 players to work;
  writing-carried games; meme-of-the-month games.

## 1. Mission

Find original co-op games where **a group of friends will create the funny
moment themselves**, the 30-second clip nobody has seen yet, and that stays
fun on the tenth session, not just the first. The genre is crowded after a
wave of hits; the hook has to be a new shared verb or a new social twist,
not a new monster in an old structure.

Zero board cards is acceptable. Never pad the board.

## 2. What makes a pitch good

Score each 1-5. **Friends moment and Tenth session are gates:** 2 or less on
either keeps a card off the board.

| Criterion | What a 5 looks like |
|---|---|
| Hook | One sentence makes a group chat say "we have to play this" |
| Friends moment | The rule reliably produces chaos *between players*, not just at them |
| Tenth session | Runs vary enough (places, events, roles, goals) that session 10 still surprises |
| Clarity | A new player joining mid-session gets it in a minute |
| Exploit-proof | No dominant strategy, and one strong player can't carry the rest |
| Novelty | The scout found nothing that plays this way |
| Buildability | The netcode risk is honest and survivable for a small agent studio |

Hard no's: existing IP, characters or real people; anything on the
anti-list; needs licensed music or voice acting; needs hardware beyond
keyboard, mouse, controller and a headset.

## 3. Collision hands

Hands come from `deck.json` via `tools/draw_hands.py`: a **shared job**, a
**place**, a **social twist** and a **pressure**. Use all four, freely
reinterpreted. The social twist is where the comedy lives: lean on it.
Each pitcher writes 5 hand pitches + 2 free pitches.

## 4. The pitch card

`pitches/<seat>-<nn>.md`, front matter plus body, **at most 400 words**.
`tools/check_pitches.py` enforces the shape (from `card-format.json`).

```markdown
---
id: b-03
title: Working Title
hand: [shared job, place, social twist, pressure]     # or [free]
hook: One sentence, max 20 words.
---
**What it is:** two sentences a stranger could repeat: the fantasy and the goal.
**The rule:** the one rule the game grows from.
**Players and roles:** player count, and what each player does (asymmetry if any).
**Session shape:** what a 20-30 minute session looks like, start to finish.
**The friends moment:** the 30-second clip: what goes wrong between the players.
**Voice:** how proximity voice (or its absence) creates the comedy.
**Tenth session:** what's different by session ten: places, events, roles, unlocks.
**Exploit check:** the obvious cheese, and how one strong player is kept from carrying.
**Why watch:** why a streamer group is fun to watch.
**Hand use:** how each of the four cards shows up.
**Prototype beats:** three short moments a 2-4 player prototype builds.
**Netcode risk:** what's hard to sync (physics, many objects, ragdolls) and how to keep it simple.
**Look:** one line of gut-feel art direction.
**Risk:** the thing most likely to make it unfunny or same-y.
```

## 5. The team

- **room-lead (Claude), curator.** Draws hands, dispatches, blinds, curates,
  writes the board and the gate. Does not pitch.
- **pitch-a, pitch-b, pitch-c (Codex).** 7 cards each, independently. Never
  read other pitchers' files, `blind/` or the board. `pitch-c` draws with
  `--strange` (this deck has no strange cards, so it changes nothing; keep
  the flag for symmetry).
- **depth-critic (Codex).** Tries to break every blind card. For each, writes
  `depth/<blind-id>.md`:
  - **Carry and cheese hunt:** the dominant strategy, and whether one good
    player can solo it while friends watch.
  - **Ten sessions:** ten one-line descriptions of different sessions
    (place, event, role mix, goal). If ten distinct ones won't come, say
    where it ran dry.
  - **Friends test:** does the chaos come from players affecting each other,
    or just from the environment? Environment-only chaos scores low.
  - **Netcode reality check:** is the stated risk honest?
  - Scores for Friends moment, Tenth session, Exploit-proof, Clarity, one
    line each.
- **scout-novelty (Codex).** Two jobs:
  1. **Market read first** (`scout-market.md`, under 600 words): co-op
     "friendslop" games that broke out in the last ~24 months, each with its
     hook in one line, price, and a rough popularity signal (Steam review
     count from the store page, with link). Then: which hooks are now
     overused. Room-lead shares this file with the critic at curation, not
     with pitchers (it would pull them toward clones).
  2. **Novelty per blind card:** Steam, itch.io, YouTube, max 3 searches;
     1-3 nearest games with opened links; verdict **Fresh**, **Twist** or
     **Exists**.
  Follows `~/openrig/briefs/RESEARCH-WEB-ACCESS-RULE.md` (v2). Writes
  `scout-novelty.md` and `sources.md`.

**Blind judging.** As in the depth room: room-lead runs
`python3 tools/blind.py --seed <n>` once all cards are valid; the critic, the
scout and the curator judge from `blind/` only; nobody opens
`.blind-key.json` until `gate.json` is written; then room-lead adds a Reveal
table to `board.md`.

## 6. Funnel

1. **Dry run.** One fake card through draw, pitch, check, blind, critic note
   and scout line. Fix every permission prompt; delete the dry-run files.
2. **Market read and draw.** Scout starts the market read; lead draws 5
   hands per pitcher (`lead-hands.md`) and dispatches. All in parallel.
3. **Check.** `check_pitches.py`; invalid cards go back once.
4. **Blind.** `blind.py`.
5. **Judge.** Critic and scout work through `blind/` in parallel.
6. **Curate.** Cut hard no's, **Exists**, overused hooks (per the market
   read), and anything failing the Friends-moment or Tenth-session gate.
   Board: up to 6 cards.
7. **Gate.** `board.md` and `gate.json`, then stop. Never ask in chat;
   never write a decision file.
   ```json
   {
     "title": "Pick co-op pitches to prototype",
     "question": "Which should become 2-4 player prototypes? Each one needs a playtest session with friends.",
     "kind": "choose", "min": 1, "max": 3, "max_soft": true,
     "lead": "room-lead",
     "context": "board.md",
     "options": [
       {"id": "x-02", "title": "Working Title", "summary": "What it is, the friends moment, the critic's verdict, netcode risk, scout verdict.", "file": "blind/x-02.md"},
       {"id": "none", "title": "None of these: go again", "summary": "Fresh hands next round. Add notes."}
     ]
   }
   ```
8. **Reveal.** Add the Reveal table to `board.md`.
9. **After the decision:** for each pick, write `proto-spec-<blind-id>.md`:
   what the game is, the goal, how a session ends, every interactable, the
   roles, controls, the three beats and what each must prove, the carry
   exploit it must not allow, the netcode plan (ENet, host + up to 3
   clients, what is synced and what is local), out of scope, time box. Then
   stop.

If the decision is `none`: copy the owner's notes into `owner-notes.md`,
draw fresh hands, run steps 2-8 again (blind with `--round 2`) and open a
new gate in `gates/`.

## 7. Deliverables

In this job folder: `pitches/`, `blind/`, `depth/`, `scout-market.md`,
`scout-novelty.md`, `sources.md`, `lead-hands.md`, `board.md` (under 1,200
words, with also-rans and the Reveal), `gate.json`, `proto-spec-*.md` after
the decision, and `retro.md`.

## 8. Operations

- Runs as a Rig Console job in `~/openrig/jobs/friends-1/` (`job.json`
  present). Fresh rig. Runs in parallel with the depth room; the two rooms
  never read each other's files.
- Before dispatch the operator pre-approves for every seat: `rig queue`
  commands and `python3 tools/*.py` inside the job folder.
- Shell text: SHARED-RULES.md (use `--body-file`).
- The operator acts only when messaged.

## 9. Limits

- Never spend money, create accounts, post, contact anyone, or download and
  run games.
- Stop at the gate. Other stops and retries: SHARED-RULES.md.
- Two-exchange disagreement rule: write both positions into `board.md`.
