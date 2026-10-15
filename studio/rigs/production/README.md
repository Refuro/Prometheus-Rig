# Production (studio stage 4)

Template for the team that builds a designed game, milestone by milestone, as a clean Godot
project made for Steam. Brief: `brief.md`.

| Seat | Runtime | Job |
|---|---|---|
| `tech-lead` | Claude | Architecture, plans, tasks, merges, packets, gates; only contact with the design team |
| `dev-a`, `dev-b` | Codex | Tasks with their tests, each in its own worktree |
| `review-code` | Claude | Reviews every task before merge |
| `playtest-bot` | Codex | Bots, long runs, determinism and performance, exploit reports |
| `player-eyes` | Claude | Screenshot review per milestone (woken) |
| `art-production` | Codex | Art and audio to the bible (woken from milestone 2) |
| `art-review` | Claude | Checks art batches against the bible (woken from milestone 2) |

## Tools
- `tools/build.py`: scaffold (`--new`), worktrees (`--worktree <seat>`), the one build-and-check
  command, and milestone builds (`--milestone <m>`: Windows zip with a download page, web build,
  screenshots).
- `tools/sync_data.py`: copies the design job's `data/` into `game/data/`; the build fails if the
  copy is edited by hand.
- `tools/check_text.py`: word budgets and banned phrases (the design team's checker).

## Launch (in Ubuntu), after the design gate is approved

Needs Godot 4.7 with export templates (`studio/setup/install-godot-wsl.sh`) and screenshot
support (`studio/setup/install-shots-wsl.sh`). Set the names, then paste the rest (example: A
Bridge Goes Walking):

    GAME=bridge
    cp -r ~/openrig/studio/rigs/production ~/openrig/jobs/$GAME-prod
    cd ~/openrig/jobs/$GAME-prod
    sed -i "s/prod-1/$GAME-prod/" rig.yaml job.json
    sed -i "s/DESIGN-JOB/$GAME-design/" job.json
    rig spec validate rig.yaml
    rig spec preflight rig.yaml

Then ask the operator to bring the rig up (`rig up ./rig.yaml --cwd .`), pre-approve the commands in
brief section 11, and wake only `tech-lead` with: "Read brief.md and agents/tech-lead/guidance/role.md,
then start setup." The tech lead scaffolds the game, syncs the data and runs the dry run.

Before any art or audio work, the Studio Architect fills in `asset-pipeline.md` from the owner's asset
pipeline decision.

## What you'll see
- One gate per milestone, after the design team's vision check passes. Open exploits and bugs come
  first; the Windows download is on the Play builds page.
- `milestones.json` in the job folder: status of every milestone.
