# Depth room (studio stage 1, Track A)

Single-player games with a simple premise and real depth. Runs in parallel
with the friendslop room (`../friend-room`).

What's different from the first pitch room:
- Cards must describe the late game, the variety engine and their own exploit.
- A Codex **depth critic** tries to break every card (exploits, ten distinct
  situations); Depth and Exploit-proof are gates.
- Three returning ideas (Pile Driver, Bruise Architecture, Roll Up the
  Distance) are rewritten by a **reviser** and judged **blind** with the new
  pitches (`tools/blind.py`).
- Proto specs ask for three beats (early, middle, late) and a clear
  "what this game is".

## Launch (in Ubuntu)

    cp -r ~/openrig/studio/rigs/depth-room ~/openrig/jobs/depth-1
    cd ~/openrig/jobs/depth-1
    rig spec validate rig.yaml
    rig spec preflight rig.yaml
    rig up ./rig.yaml --cwd . --plan
    rig up ./rig.yaml --cwd .

Seats: `room-lead@depth-1`, `pitch-a/b/c@depth-1`, `revise-cards@depth-1`,
`depth-critic@depth-1`, `scout-novelty@depth-1`.

Ends with `gate.json` under "Needs you" in the Rig Console.
