# Architects rig

The four architects (Rig, Studio, Platform, Model) and a Codex reviewer as seats in one rig, so they can
message each other directly. The owner talks to them through the console ("Message it") or by attaching.
They open gates for anything that needs the owner. Contract: `brief.md`. Ownership: `../ROLES.md`.

## Before launch
Each departing chat architect writes its handoff: `handoffs/<role>.md`, from `handoffs/TEMPLATE.md`.
The new seats start from those (`rig-architect.md` is done).

## Launch (operator, in Ubuntu)
    mkdir -p ~/openrig/jobs/architects/gates
    cp job.json ~/openrig/jobs/architects/job.json
    cd /mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/architects
    rig spec validate rig.yaml && rig spec preflight rig.yaml
    rig up ./rig.yaml --plan
    rig up ./rig.yaml

- **Working directory:** every seat works in the repo root, set as an absolute path in `rig.yaml`. Don't
  pass `--cwd`: it overrides every seat's working directory (the first launch used `--cwd .`, so seats
  started in `architects/` and repo edits prompted). Check with `rig whoami` or the seat's header.
- **Launch record:** write `~/openrig/launches/architects.json` with `folder` = `~/openrig/jobs/architects`
  (gates live there), rig `architects` and lead `arch-rig`.
- **Models:** start `arch-model@architects` on the strongest Claude model (`/model` in the seat if it isn't the
  default). The other Claude seats can use the default.
- **First message to each seat:** "You are the <Role>. Read `architects/brief.md`, `ROLES.md`,
  `briefs/SHARED-RULES.md`, your role file and `architects/handoffs/<role>.md`, then reply with a three-line
  status and wait."

Seats: `arch-rig@architects`, `arch-studio@architects`, `arch-platform@architects`, `arch-model@architects`,
`review-codex@architects`. OpenRig names each seat `<pod>-<member>`.
