# Prototype sprint (studio stage 2)

Template for a prototype job. Copy it to `~/openrig/jobs/proto-N/`, drop in
the specs, launch. Builders make small web prototypes that teach one idea at
a time and screenshot themselves; builds appear on the
Rig Console's **Play builds** page as they land; the sprint ends with a gate.

## One-time setup (Godot in WSL)

    bash ~/openrig/studio/setup/install-godot-wsl.sh

Installs Godot 4.7.1 (matches your Windows editor) and its export templates
under `~/.local/`. Free, ~1.4 GB download, no sudo (needs `unzip` and `curl`).

## One-time setup for screenshots

    bash ~/openrig/studio/setup/install-shots-wsl.sh

Installs Playwright and its Chromium (free) so builds can screenshot each
stage. If its final check says libraries are missing, run the `sudo` line it
prints once.

## Launch round 3 (in Ubuntu)

    cp -r ~/openrig/studio/rigs/proto-sprint ~/openrig/jobs/proto-3
    cd ~/openrig/jobs/proto-3
    for id in x-14 x-19 x-15 x-18; do
      cp ~/openrig/jobs/proto-2/specs/proto-spec-$id.md specs/
      mkdir -p inputs/$id
      cp ~/openrig/jobs/proto-2/reviews/*-$id.md inputs/$id/ 2>/dev/null
      cp -r ~/openrig/jobs/proto-2/protos/$id inputs/$id/old-proto
      rm -rf inputs/$id/old-proto/.godot
    done
    ls specs inputs
    rig spec validate rig.yaml
    rig spec preflight rig.yaml
    rig up ./rig.yaml --cwd .

(`owner-notes.md` is already in the template with your round-2 notes.)

Seats: `proto-lead`, `player-eyes`, `depth-critic`, `build-a`, `build-b`,
`build-c` (each `@proto-3`).

## What lands where

- `protos/<id>/`: each Godot project (open it in the Windows editor via
  `\\wsl$\Ubuntu-24.04\home\you\openrig\jobs\proto-N\protos\<id>` if curious)
- `builds/<id>/index.html`: the web build (Play builds page)
- `protos/<id>/shots/`: screenshots of the splash and every stage
- `reviews/eyes-<id>.md`: the player-eyes review from screenshots
- `reviews/depth-<id>.md`: depth critic's exploit list per toy
- `reviews/lead-<id>.md`: lead's review per toy
- `lead-summary.md` + `gate.json`: the end-of-sprint decision
- `events.jsonl`: one line per build attempt

## Tested

`tools/build.py` was run end to end with Godot 4.7.1 on Linux: scaffold,
headless import and run, smoke test, web export (no threads); the exported
build loads and runs in headless Chromium; round 3 adds the stage framework,
ProtoUI goal bar and markers, SVG art, text budgets (a [TODO] or over-budget
string turns the build RED) and per-stage screenshots, all tested end to end.
