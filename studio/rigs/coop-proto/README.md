# Co-op prototype sprint (studio stage 2, friendslop picks)

Template for a co-op prototype job. Copy it to `~/openrig/jobs/coop-N/`,
drop in the specs, launch.

Builders make 2-4 player online prototypes in Godot. Each one hosts and joins
over ENet, passes an automated sync test (a headless host plus bot clients on
one machine must end in the same state), and exports a Windows zip with a
download page that shows on the Rig Console's **Play builds** page. The sprint
ends with a gate after you play with friends.

## Launch (in Ubuntu)

    cp -r ~/openrig/studio/rigs/coop-proto ~/openrig/jobs/coop-1
    cp ~/openrig/jobs/friends-1/proto-spec-*.md ~/openrig/jobs/coop-1/specs/
    cd ~/openrig/jobs/coop-1
    ls specs
    rig spec validate rig.yaml
    rig spec preflight rig.yaml
    rig up ./rig.yaml --cwd .

Then tell the operator: "coop-1 is up in ~/openrig/jobs/coop-1. Pre-approve
rig queue commands, python3 tools/build.py and python3 tools/net_test.py for
every seat per brief.md section 7, then have proto-lead run the dry run from
section 6 and start."

Seats: `proto-lead`, `depth-critic`, `build-a`, `build-b`, `build-c` (each
`@coop-1`).

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

- `protos/<id>/`: each Godot project; `protos/<id>/net-test/`: sync test logs
- `builds/<id>/<id>-windows.zip` + `index.html`: the build and its download page
- `reviews/depth-<id>.md`, `reviews/lead-<id>.md`: critic and lead reviews
- `lead-summary.md` + `gate.json`: the end-of-sprint decision

## Tested

The scaffold was run end to end with Godot 4.7.1 on Linux: headless import
and run, smoke test, a sync test with a host and 3 bot clients (passes), the
same test with a deliberate 0.3-unit client drift (fails, as it should), two
sync tests in parallel on separate ports, and a Windows export zipped with
its download page. Not tested here: the .exe on real Windows PCs over
Tailscale. The dry run should include one owner check that the zip runs.
