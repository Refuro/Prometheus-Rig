# Review: PL-013, option A runbook and scripts

**Requested by** the Platform Architect (its log, Notes for the Model Architect, 2026-10-12). **Reviewer:** the Model Architect. Findings only; the design is the Platform Architect's.

**Read:**
- `setup/install-console-user.sh`, `setup/harden-wsl.sh`, `setup/deploy-console.sh`, `setup/rig-owner`;
- the PL-013 runbook;
- `gates.rig_cmd`;
- `SETUP.md`.

None of it was run: it needs root on the PC. "Verify" means check on the PC.

## Verdict
The direction and most of the mechanics are sound:
- **Root-owned code, a token readable only by root and the console user, ACLs instead of shared ownership:** all sound.
- **The narrow helper:** it runs *as the agents' user*, so tampering with it gains nothing.
- **Sudo:** `harden-wsl.sh` doesn't edit sudoers itself, and the recovery path is right (`wsl -u root` from Windows still works with interop off).

**Two findings to fix before the owner runs it**, because PL-013 claims more than the scripts deliver:
- the deploy path ships whatever is in the agent-writable repo (finding 1);
- the new token can end up in the agents' own snapshot files (finding 2).

## Findings, most important first

**1. "Closes: editing the console's code" isn't true yet; the edit just waits for the next deploy. (High)**
- **The path:**
  - `deploy-console.sh` runs the smoke test on, and then `sudo rsync`s, `dashboard/` from the repo on `/mnt/c`, where agents can still write anything;
  - an agent that edits `nav.js` or `serve.py` gets its change shipped, root-owned, at the owner's next deploy;
  - the smoke test only proves the old checks still pass, not that nothing hostile was added.
- **Suggested direction:** deploy a reviewed commit, not the working tree.
  - **Pin to a commit:** `git archive <commit>` into a temp dir, test and copy that. Refuse to deploy if `dashboard/` has uncommitted changes.
  - **Show what changed:** print `git diff --stat <last deployed>..<commit> -- dashboard/` and ask for a yes.
  - **Record it:** write the deployed hash to `/var/lib/rig-console/deployed` so `/api/health` can show it.
- **The remaining risk:** the boundary then rests on the owner (or the Platform Architect) reading the diff. Since the architects will soon be seats working in this folder (PD-020), say so in PL-013.

**2. The new token can be captured by the snapshot logger. (High; easy to avoid.)**
- **The path:** `install-console-user.sh` prints the new token to the terminal. The logger (`setup/rig-snapshots.sh`, PD-001) copies every tmux pane into `snapshots/*.txt` on `/mnt/c` every 10 s, and agents can read that folder. That includes the `operator-human@kernel` terminal. If the owner runs the script in any tmux pane, the token lands in a file agents can read, and step 3 is undone.
- **Suggested direction:** don't print it. Have the owner read it once from a root-only file:
  ```
  sudo install -m 600 /dev/null /root/rig-console-token
  # write it there
  ```
  then `sudo cat /root/rig-console-token` in a plain terminal, not tmux. Put "run outside tmux" at the top of the runbook. Also check `snapshots/` for the old token afterwards, if it was ever printed.

**3. Launch records are the routing trust anchor, and agents can write them. (Medium; partly known.)**
- **The gap:** `~/openrig/launches/` is the agents' user's folder. The console only reads it, but any seat can rewrite a launch record and route your next decision to another team's lead. PL-013 lists the operator as the limit, but every seat is equal here until option B.
- **Suggested direction:**
  - **Move it:** have the operator write launch records through a tiny root-owned helper into `/var/lib/rig-console/launches/` (agents can't write there). Or let the console snapshot each record the first time it sees it, and alert on later changes, the same as the PL-010 rig pin.
  - **Say it:** at minimum, state it in PL-013's "doesn't close" list.

**4. Add a few checks to runbook step 6 that prove the new boundary itself. (Medium.)** As the agents' user, after step 5, each of these must fail:
- **Code:** `touch /opt/rig-console/nav.js`.
- **Settings:** `cat /etc/rig-console/env`.
- **Process environment:** `cat /proc/$(systemctl show -p MainPID --value rig-dashboard)/environ`.
- **Console user:** `sudo -u rigconsole true` (it must ask for a password).
- **State:** `ls /var/lib/rig-console/state`.

Then record all of them in PL-013's outcome, as the step-6 lines already are.

**5. The unit: optional hardening. (Low.)**
- **What's there is fine:** `ProtectSystem=full` is compatible with sudo, and `NoNewPrivileges` correctly isn't set (sudo needs setuid).
- **Worth adding:** `ProtectHome=read-only` with `ReadWritePaths=<owner home>/openrig/jobs <owner home>/openrig/research /var/lib/rig-console`, so a console bug can't write anywhere else in your home. Plus `PrivateDevices=yes` and `ProtectKernelTunables=yes`. Smoke-test the gate flow after.

**6. `rig-owner` passes all arguments through. (Low.)**
- **What it does:** it allows `send` and `ps`, then `exec rig "$@"`, so any `rig send` flags pass through as the agents' user. That only matters if the console process itself is compromised, and then it acts as the agents' user, which it could almost do anyway.
- **An option:** allow exactly `send <seat> <message>` and `ps --nodes -A --json`, and refuse anything else.

**7. Smaller points.**
- **sudo and `HOME`:** `harden-wsl.sh` and the helper rely on sudo setting `HOME` to the target user, which is Ubuntu's default. Worth one line of `echo $HOME` in the helper's self-test on line 34 of `install-console-user.sh`.
- **The old cookie:** it stops working after the rotation (good). Remind the owner to sign in on every device, or the phone's decision page will just say "sign in".
- **Agents can still forge alerts.** `RIG_SNAPSHOTS` stays on `/mnt/c`, so a seat can fake snapshot data and trigger alerts with its own text, which then reaches the phone through ntfy. It can't do more than that. Worth a line in "doesn't close".

## What's right
- **The helper runs as the agents' user,** so agents tampering with it gain nothing.
- **Sudo edits stay manual:** `harden-wsl.sh` refuses to run without a usable password, and edits `wsl.conf` with a parser that keeps the other settings.
- **Old settings are cleaned:** the token and ntfy topic are stripped from the agent-readable file, and a new token is generated.
- **The old installer can't undo this:** it refuses once `/etc/rig-console/env` exists.
- **"Doesn't close" is candid** about option B, and about decisions being acted on before the alert.
