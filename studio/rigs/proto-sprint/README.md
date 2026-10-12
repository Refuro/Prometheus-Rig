# Prototype sprint (studio stage 2)

Template for a prototype job. Copy it to `~/openrig/jobs/proto-N/`, drop in
the specs, launch. Builders make grey-box Godot toys; web builds appear on the
Rig Console's **Play builds** page as they land; the sprint ends with a gate.

## One-time setup (Godot in WSL)

    bash ~/openrig/studio/setup/install-godot-wsl.sh

Installs Godot 4.7.1 (matches your Windows editor) and its export templates
under `~/.local/`. Free, ~1.4 GB download, no sudo (needs `unzip` and `curl`).

## Launch (in Ubuntu)

Example for the depth room's picks (next free name: proto-2):

    cp -r ~/openrig/studio/rigs/proto-sprint ~/openrig/jobs/proto-2
    cp ~/openrig/jobs/depth-1/proto-spec-*.md ~/openrig/jobs/proto-2/specs/
    cd ~/openrig/jobs/proto-2
    sed -i 's/proto-1/proto-2/' rig.yaml job.json
    sed -i 's/Prototype sprint 1/Prototype sprint 2/' job.json
    ls specs
    rig spec validate rig.yaml
    rig spec preflight rig.yaml
    rig up ./rig.yaml --cwd . --plan
    rig up ./rig.yaml --cwd .

Then tell the operator: "proto-2 is up in ~/openrig/jobs/proto-2. Pre-approve
rig queue commands and python3 tools/build.py for every seat per brief.md
section 7, then have proto-lead run the dry run from section 6 and start."

Seats: `proto-lead`, `depth-critic`, `build-a`, `build-b`, `build-c` (each
`@proto-N`).

Friendslop picks need a different template (Windows builds, ENet host/join,
multi-instance sync tests); that one is written after the friendslop gate.

## What lands where

- `protos/<id>/`: each Godot project (open it in the Windows editor via
  `\\wsl$\Ubuntu-24.04\home\you\openrig\jobs\proto-N\protos\<id>` if curious)
- `builds/<id>/index.html`: the web build (Play builds page)
- `reviews/depth-<id>.md`: depth critic's exploit list per toy
- `reviews/lead-<id>.md`: lead's review per toy
- `lead-summary.md` + `gate.json`: the end-of-sprint decision
- `events.jsonl`: one line per build attempt

## Tested

`tools/build.py` was run end to end with Godot 4.7.1 on Linux: scaffold,
headless import and run, smoke test, web export (no threads); the exported
build loads and runs in headless Chromium with the ABOUT.txt title card
showing; a script error, or an ABOUT.txt with [TODO] lines, turns the build
RED.
