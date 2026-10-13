# Design team (studio stage 3, then production support)

Template for the design team that turns a winning prototype into a signed-off
game design, then stays on through production.

| Seat | Runtime | Owns |
|---|---|---|
| `creative-director` | Claude | Pillars, product brief and scope, quality bar, handoff; final call; inbox; milestone vision checks |
| `design-systems` | Claude | Core loop, progression, variety, content plan; Steam achievements and features |
| `design-feel` | Claude | How it feels in hand: physics, controls, camera, response to every action, with values and checks |
| `design-balance` | Codex | Numbers in `data/balance/`, simulations, cheese register |
| `design-ux` | Claude | Onboarding, every screen, settings, controller and Deck, accessibility, localization |
| `words-narrative` | Claude | Whether a story earns its place; structure and voice |
| `words-editor` | Codex | Word budgets; cuts every player string; `check_text.py` green |
| `art-director` | Codex | Art and audio directions, then the art and audio bible |

The team designs the polished 1.0 the owner will sell, written so production
can build it without guessing: feel values, achievements and text in
`data/`, behaviours with checks a test can run. Only the creative director and systems designer work continuously; the others
idle until woken.

## Tools
- `tools/check_text.py`: word budgets + banned AI-isms for every player
  string (`text-budgets.json`). Also a production build step.
- `tools/shoot.py`: screenshots a prototype web build into `inputs/shots/`.
- `tools/inbox.py`: design questions and discoveries with statuses
  (adopt / spike / park / reject / escalate).

## Launch (in Ubuntu), after the prototype gate

One job per game. Set the two names, then paste the rest (example: A Bridge
Goes Walking from proto-2; for Shovel the Sunrise use `GAME=sunrise ID=x-19`):

    GAME=bridge ID=x-14 PROTO=proto-2 PITCH=depth-1
    cp -r ~/openrig/studio/rigs/design-team ~/openrig/jobs/$GAME-design
    cd ~/openrig/jobs/$GAME-design
    sed -i "s/design-1/$GAME-design/" rig.yaml job.json
    mkdir -p inputs/shots inputs/decisions
    cp ~/openrig/jobs/$PITCH/blind/$ID.md inputs/pitch-card.md
    cp ~/openrig/jobs/$PITCH/depth/$ID.md inputs/depth-review.md 2>/dev/null
    cp ~/openrig/jobs/$PROTO/specs/proto-spec-$ID.md inputs/
    cp ~/openrig/jobs/$PROTO/reviews/*-$ID.md inputs/ 2>/dev/null
    cp -r ~/openrig/jobs/$PROTO/protos/$ID inputs/proto
    rm -rf inputs/proto/.godot
    cp -r ~/openrig/jobs/$PROTO/builds/$ID inputs/build
    cp ~/openrig/jobs/$PROTO/decisions/* inputs/decisions/ 2>/dev/null
    cp launch/owner-notes-$ID.md inputs/owner-notes.md
    cp templates/presentation-rules.md inputs/
    python3 tools/shoot.py inputs/build inputs/shots 3
    ls inputs inputs/shots
    rig spec validate rig.yaml
    rig spec preflight rig.yaml

If `shoot.py` fails, carry on; the team can retry it. Then ask the operator
to bring the rig up (`rig up ./rig.yaml --cwd .`).

Stage 3 gates: pillars and product (approve; the team waits for it before
drafting), art and audio direction (choose 1), design (approve, via
`docs/handoff.md`). Then the handoff names production milestone 1, a feel
build you play, and the team stays up for production.

## Adding a discovery yourself

    cd ~/openrig/jobs/<game>-design
    python3 tools/inbox.py add discovery --title "What happened" --by owner --text "How to repeat it. Why it's fun."

Or message the director: `rig send creative-director@<game>-design 'Discovery: ...'`.
