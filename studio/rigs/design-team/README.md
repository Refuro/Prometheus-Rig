# Design team (studio stage 3, then production support)

Template for the design team that turns a winning prototype into a signed-off
game design, then stays on through production.

| Seat | Runtime | Owns |
|---|---|---|
| `creative-director` | Claude | Pillars, tone, final call; inbox; milestone vision checks |
| `design-systems` | Claude | Core loop, progression map, variety engine, content plan |
| `design-balance` | Codex | Numbers in `data/balance/`, simulations, cheese register |
| `design-onboarding` | Claude | First ten minutes; every object explains itself |
| `words-narrative` | Claude | Whether a story earns its place; structure and voice |
| `words-editor` | Codex | Word budgets; cuts every player string; `check_text.py` green |
| `art-director` | Codex | Visual directions, then the art bible |

Only the creative director and systems designer work continuously; the others
idle until woken.

## Tools
- `tools/check_text.py`: word budgets + banned AI-isms for every player
  string (`text-budgets.json`). Also a production build step.
- `tools/inbox.py`: design questions and discoveries with statuses
  (adopt / spike / park / reject / escalate).

## Launch (in Ubuntu), after the prototype gate

    cp -r ~/openrig/studio/rigs/design-team ~/openrig/jobs/<game>-design
    cd ~/openrig/jobs/<game>-design
    sed -i 's/design-1/<game>-design/' rig.yaml job.json
    mkdir -p inputs/shots
    # copy into inputs/: the winning pitch card, its proto spec, and from the
    # prototype job: protos/<id>/ABOUT.txt, HOW-TO-PLAY.md, build-*-notes.md,
    # reviews/*-<id>.md, and decisions/*.json + .md
    rig spec validate rig.yaml
    rig spec preflight rig.yaml
    rig up ./rig.yaml --cwd .

Ends stage 3 with three gates: pillars (approve), art direction (choose 1),
design (approve). Then it stays up for production.

## Adding a discovery yourself

    cd ~/openrig/jobs/<game>-design
    python3 tools/inbox.py add discovery --title "What happened" --by owner --text "How to repeat it. Why it's fun."

Or message the director: `rig send creative-director@<game>-design 'Discovery: ...'`.
