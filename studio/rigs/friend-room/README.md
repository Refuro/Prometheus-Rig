# Friendslop room (studio stage 1, Track B)

Online co-op games for 2-4 friends where the friends make the comedy. Runs
in parallel with the depth room (`../depth-room`).

- Cards must describe the friends moment, roles, session shape, the tenth
  session, voice chat's role and the netcode risk.
- A Codex **depth critic** hunts carry exploits and session variety; Friends
  moment and Tenth session are gates. Judging is blind (`tools/blind.py`).
- The scout writes a **market read** of recent co-op hits and overused hooks
  first; pitchers never see it (so they don't drift into clones).

## Launch (in Ubuntu)

    cp -r ~/openrig/studio/rigs/friend-room ~/openrig/jobs/friends-1
    cd ~/openrig/jobs/friends-1
    rig spec validate rig.yaml
    rig spec preflight rig.yaml
    rig up ./rig.yaml --cwd . --plan
    rig up ./rig.yaml --cwd .

Seats: `room-lead@friends-1`, `pitch-a/b/c@friends-1`,
`depth-critic@friends-1`, `scout-novelty@friends-1`.

Ends with `gate.json` under "Needs you" in the Rig Console. Prototypes for
picks need a co-op prototype template (Windows builds, ENet host/join, local
multi-instance sync tests); it gets written after this gate.
