# How the system fits together

Three views of the same setup: what runs where, how a team's work reaches your phone, and who owns
what. For the short version, see the diagram in the [README](../README.md#how-it-fits-together).

## 1. What runs where

```mermaid
flowchart LR
  you((You))
  phone((Phone))
  ntfy["ntfy.sh"]

  subgraph wsl["Windows PC · WSL2 Ubuntu"]
    subgraph openrig["OpenRig"]
      op["Operator<br/>(Codex)"] --> lead["Team lead<br/>(Claude)"]
      lead <--> seats["Seats<br/>(Claude · Codex)"]
    end
    logger["Snapshot logger<br/>every 10 s"]
    snaps[("snapshots/<br/>screens · queue · state")]
    jobs[("Job folders<br/>gate.json · events.jsonl<br/>builds/ · decisions/")]
    subgraph console["Rig Console"]
      watcher["Watcher<br/>every 10 s"] --> db[("SQLite<br/>events")]
      db --> api["Pages + API"]
    end
  end

  openrig -- "rig ps · queue · screens" --> logger --> snaps --> watcher
  seats -- "files · gates · events" --> jobs --> watcher
  watcher -- "alerts" --> ntfy -- "push" --> phone
  you -- "browser (localhost)" --> api
  phone -- "Tailscale Serve + token" --> api
  api -- "decisions" --> jobs
  api -- "rig send" --> lead
```

## 2. From agent work to your phone

```mermaid
sequenceDiagram
  autonumber
  participant S as Seat
  participant J as Job folder
  participant L as Snapshot logger
  participant W as Console watcher
  participant N as ntfy
  participant Y as You (phone)
  participant A as Console API

  S->>J: writes gate.json (or hits a prompt, limit, stall)
  L->>L: every 10 s: rig ps, queue, screens → snapshots/
  W->>J: every 10 s: read gates, files, events.jsonl
  W->>W: graph(): nodes, edges, alerts (+ dismissals)
  W->>W: collector → SQLite (feed, replay)
  W->>N: alert still there after 25 s, not sent in 6 h
  N->>Y: push notification
  Y->>A: tap → decision page (token cookie)
  Y->>A: decide
  A->>J: decisions/<id>.json + .md (closes the gate)
  A->>S: rig send to the lead: "read the decision"
```

## 3. Who owns what, and how roles talk

Every file has one owner. Roles change each other's files only by asking through the owner. Full detail
in [`ROLES.md`](../ROLES.md).

```mermaid
flowchart TB
  owner((Owner))

  subgraph arch["Architects (Claude sessions)"]
    rig["Rig Architect<br/>briefs/ · shared rules"]
    studio["Studio Architect<br/>studio/"]
    plat["Platform Architect<br/>dashboard/ · setup/ · tests · docs"]
    model["Model Architect<br/>ledger · report cards"]
  end

  subgraph files["Shared files"]
    req["dashboard/REQUESTS.md"]
    logs["Architecture logs<br/>+ Notes for &lt;Role&gt;"]
    contract["Console contract<br/>dashboard/JOBS.md"]
  end

  subgraph runtime["Live rig"]
    operator["Operator<br/>(Codex seat)"]
    teams["Team seats"]
    gates[("Gates in job folders")]
  end

  rig -- "requests" --> req
  studio -- "requests" --> req
  model -- "requests" --> req
  req --> plat
  plat -- "owns" --> contract
  rig -. "templates use" .-> contract
  studio -. "templates use" .-> contract
  rig & studio & plat --> logs
  model -- "grades from evidence" --> logs
  logs --> owner
  owner -- "priorities · approvals" --> arch
  rig & studio -- "draft operator prompts" --> owner
  owner -- "sends prompts" --> operator
  operator -- "starts · stops · standing rules" --> teams
  teams -- "open" --> gates
  owner -- "decides in console" --> gates
```
