# Co-op prototype sprint (studio stage 2, friendslop picks)

Template for a co-op prototype job. Copy it to `~/openrig/jobs/coop-N/`,
copy in the specs and the previous round's work, launch.

Builders make 2-4 player online prototypes in Godot that teach one idea per
stage and show every player which one they are and what the group must do.
Each build hosts and joins over ENet, passes an automated sync test (a
headless host plus bot clients on one machine must end in the same state),
screenshots every stage from an offline preview with bot players, and
exports a Windows zip with a download page on the Rig Console's **Play
builds** page. The preview also shows there as `<id>-preview` (a look only,
with bots; the real game is the zip). The sprint ends with a gate after you
play with friends.

## One-time setup

    bash ~/openrig/studio/setup/install-godot-wsl.sh     # already done
    bash ~/openrig/studio/setup/install-shots-wsl.sh     # screenshots

If the shots installer says libraries are missing, run the `sudo` line it
prints once.

## Launch round 2 (in Ubuntu)

First check the picks line at the top of `owner-notes.md` in the template
(default: x-08, x-19, x-03, x-02) and edit it if your coop-1 decision
changed them. Then:

    cp -r ~/openrig/studio/rigs/coop-proto ~/openrig/jobs/coop-2
    cd ~/openrig/jobs/coop-2
    for id in x-08 x-19 x-03 x-02; do
      cp ~/openrig/jobs/coop-1/specs/proto-spec-$id.md specs/
      mkdir -p inputs/$id
      cp ~/openrig/jobs/coop-1/reviews/*-$id.md inputs/$id/ 2>/dev/null
      cp -r ~/openrig/jobs/coop-1/protos/$id inputs/$id/old-proto
      rm -rf inputs/$id/old-proto/.godot inputs/$id/old-proto/net-test
    done
    cp -r ~/openrig/jobs/coop-1/decisions inputs/coop-1-decisions 2>/dev/null
    ls specs inputs
    rig spec validate rig.yaml
    rig spec preflight rig.yaml
    rig up ./rig.yaml --cwd .

Seats: `proto-lead`, `player-eyes`, `depth-critic`, `build-a`, `build-b`,
`build-c` (each `@coop-2`).

## Playing with friends

1. On the Play builds page, open the prototype and download the zip.
2. Share the zip with friends (Discord, Drive).
3. Everyone installs Tailscale (free); share your PC with them from the
   Tailscale admin page (Machines > your PC > Share).
4. You click **Host**; friends type your Tailscale IP (100.x.y.z) and click
   **Join**. Windows may warn about an unknown publisher: More info, Run anyway.
5. Windows Firewall will ask to allow the game on first host: allow it on
   private networks (Tailscale counts).

## What lands where

- `specs/v2-<id>.md`: the lead's round-2 spec (teaching sequence, who is
  who, together moments)
- `protos/<id>/`: each Godot project; `protos/<id>/shots/`: screenshots;
  `protos/<id>/net-test/`: sync test logs
- `builds/<id>/<id>-windows.zip` + `index.html`: the build and its download
  page; `builds/<id>-preview/`: the offline web preview
- `reviews/eyes-<id>.md`, `reviews/depth-<id>.md`, `reviews/lead-<id>.md`
- `lead-summary.md` + `gate.json`: the end-of-sprint decision

## Tested

The round-2 scaffold was run end to end with Godot 4.7.1 on Linux: scaffold,
headless import and run, smoke test, sync test with a host and 2 bot clients
(stage synced across peers), Windows export and zip, text budget check, web
preview export, and screenshots of the splash and all three example stages
in headless Chromium. Round 1 also tested 3 clients, a deliberate drift
(fails, as it should) and parallel tests on separate ports. Not tested here:
the .exe on real Windows PCs over Tailscale.
