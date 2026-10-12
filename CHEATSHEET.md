# OpenRig cheat sheet (run in Ubuntu)

## Mental model
- daemon   = background service that tracks everything (port 7433)
- rig      = a team. `kernel` is the always-on admin team; project rigs are teams you launch
- seat     = one agent = one tmux session, named role@rig (e.g. operator-agent@kernel)
- spec     = YAML recipe that defines a team
- queue    = durable task list; tasks wake the agent they're addressed to

## Look around
    rig status                  # daemon + kernel health
    rig ps --nodes -A           # every seat in every rig
    tmux ls                     # every agent session
    rig tui                     # dashboard

## Talk to an agent
    tmux attach -t 'operator-agent@kernel'    # open its conversation, type normally
    Ctrl+B, then D                            # LEAVE it running (detach)
    rig send <seat> 'message'                 # message without attaching

## Check in without disturbing
    rig capture <seat> --lines 30   # peek at an agent's screen, no attach
    Ctrl+B, then S                  # (attached) pick another agent from a list
    Ctrl+B, then [                  # (attached) scroll history; Q to return
Don't press Esc while an agent works: it interrupts the task.

Never type `exit`, spam Ctrl+C, or close the tab while attached.

## Start / stop
    rig down <rig>              # stops that team AND kills its in-progress work
    rig daemon stop             # stops the service; agent sessions keep running
After a Windows reboot: run `rig`, choose to resume the kernel, then ask the
operator to bring other teams back.

## Always-on logging
- rig-snapshots service: mirrors agent screens + logs activity to snapshots/.
      systemctl status rig-snapshots        # is it running?
      sudo systemctl restart rig-snapshots  # restart it
- Windows task "WSL keep-alive (OpenRig)" keeps Ubuntu running after sign-in,
  even with every terminal closed.

## Cost hygiene
- Idle agents cost nothing; agents thinking or polling spend your Claude/ChatGPT limits.
- Check usage: claude.ai/settings/usage and the Codex usage page in ChatGPT.
- If a team is looping or chatty, `rig down` it.

## Permissions
- Kernel operator: Codex, no sandbox, no approval prompts (can reach /mnt/c too).
- Project teams: narrower default; lifecycle commands like `rig up` still ask.
- Never choose the YOLO policy for project teams.
