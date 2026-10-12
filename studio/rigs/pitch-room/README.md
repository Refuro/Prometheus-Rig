# Pitch room (studio stage 1)

Files:
- `brief.md`: the run contract. Section 0 holds the owner settings.
- `rig.yaml` + `agents/`: the team (curator, 3 pitchers, novelty scout).
- `deck.json`: the collision deck. Edit freely.
- `tools/draw_hands.py`, `tools/check_pitches.py`: the lead's draw and the
  card validator.

## Launch (in Ubuntu)

This folder is a template. Each pitch round runs as a Rig Console job in its
own copy under `~/openrig/jobs/`:

    cp -r ~/openrig/studio/rigs/pitch-room ~/openrig/jobs/pitch-2
    cd ~/openrig/jobs/pitch-2
    # change the rig name to pitch-2 in rig.yaml (name:) and job.json (rig, title)
    rig spec validate rig.yaml
    rig spec preflight rig.yaml
    rig up ./rig.yaml --cwd . --plan
    rig up ./rig.yaml --cwd .

Seats: `room-lead@pitch-N`, `pitch-a@pitch-N`, `pitch-b@pitch-N`,
`pitch-c@pitch-N`, `scout-novelty@pitch-N`.

Outputs land in the job folder. The round ends with `gate.json`, which shows
up under "Needs you" in the Rig Console; your answer lands in `decisions/`.

## Notes

- Agent specs declare the `openrig-core` plugin directly (OpenRig 0.6.5+)
  rather than importing the builtin `shared` spec.
- Pitcher startup messages mention seat letters only, not the rig name, so
  they work unchanged in any copy.
