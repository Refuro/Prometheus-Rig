# prometheus-rig

**A home lab for AI agent teams.** Claude Code and Codex agents work as small teams on one Windows PC
(*Prometheus*). They research markets, validate offers, and design and prototype games, coordinated by
[OpenRig](https://www.npmjs.com/package/@openrig/cli) inside WSL2. A custom dashboard, **Rig Console**,
lets you watch them work and make their decisions from a desktop or phone.

It's a hobby and learning project. The goal is to find out how far a supervised "factory" of agents can
go: from finding an opportunity to validating it, building it and selling it. The rule throughout is that a
human makes every call that matters.

![Rig Console's live graph replaying a research run: three agents working, handoffs in flight, and the activity feed](docs/graph.png)

---

## What's inside

### Rig Console: a live dashboard for agent teams
A small stdlib-Python server plus plain HTML pages, with no build step and no dependencies.

| Page | What it shows |
|---|---|
| **Live graph** | Every team as a card tree, with each agent's state, what it's doing in plain English, a 30-minute activity strip and handoffs between agents. Handoffs animate as sparks along the lines; files pop up as agents write them. |
| **Replay** | Any team's recorded history played back at 30–600×, with scrubbing and quiet stretches skipped. A four-hour run becomes a four-minute watch. |
| **Activity feed** | One running story: who started, what they're doing, what they handed off, which files they wrote. |
| **Decisions** | "Gates" the teams open for you: pick 3 pitches, approve a plan, choose a brand name. Background docs are rendered in place, with an in-page reader for every file they mention. |
| **Play builds** | Godot web exports from prototype jobs, one tap to play. Cross-origin isolation is handled, so threaded builds work too. |
| **Niche board / Run report** | Research funnels, checkpoint pickers, a per-agent timeline of where the time went, approval waits, a usage log and an evidence link checker. |
| **Phone view** | "Needs you", teams and the feed in a phone layout, installable as an app. Alerts arrive as push notifications via ntfy. |

<table>
<tr>
<td width="68%"><img src="docs/decision.png" alt="A decision gate on desktop: pick 3 pitches, with picks numbered in order"></td>
<td width="32%"><img src="docs/phone.png" alt="The same decision on a phone"></td>
</tr>
<tr>
<td align="center"><sub>Teams ask, you decide: a gate on desktop</sub></td>
<td align="center"><sub>…or from your phone</sub></td>
</tr>
</table>

Under the hood:
- **SQLite event store** for states, actions, handoffs, files and custom events. It backfills from logs, uses numbered migrations, and lives outside the synced folder.
- **Job-agnostic.** Any folder under a watched root is a job (research run, validation campaign, game prototype…). Jobs describe themselves with `job.json` and can log their own events through `events.jsonl`. See [`dashboard/JOBS.md`](dashboard/JOBS.md).
- **Alert rules tuned against false alarms.** Approval prompts, usage limits, genuinely frozen agents, stuck handoffs, nearly full context windows. Alerts can be dismissed, have to persist before they notify, and are rate-limited, so a flapping alert doesn't spam your phone.

### Teams
| Team | What it does | Typical shape |
|---|---|---|
| **Research** | Finds a narrow, evidenced business opportunity: longlist → screen → skeptic → deep dive → shortlist, with checkpoints for the human. | Claude lead + two Codex analysts (complaints-first and spending-first) + Claude skeptic |
| **Validation** | Turns a finalist into a real offer, then tests it with honest, rule-following outreach, in phases that need human approval before anything is sent. | Claude lead and writer, Codex ops and prospector, skeptic at the gates |
| **Game studio** | Pitch rooms invent original games, prototype sprints build playable grey-box Godot toys, then a design team locks pillars and art direction. Ideas are narrowed by **playing prototypes, not writing documents**. | See [`studio/STUDIO-PLAN.md`](studio/STUDIO-PLAN.md) |

---

## How it fits together

```mermaid
flowchart LR
  you((You)) -- "decisions & messages" --> console["Rig Console<br/>(desktop · phone)"]
  console -- "push alerts" --> phone((Phone))
  subgraph wsl["WSL2 Ubuntu"]
    op["Operator<br/>(Codex)"] --> lead["Team lead<br/>(Claude)"]
    lead <--> seats["Seats<br/>(Claude · Codex)"]
    logger["Snapshot logger<br/>(every 10 s)"]
  end
  console -- "rig send" --> lead
  seats -- "files, gates, events" --> jobs[("Job folders")]
  jobs --> console
  logger -- "screens, queue, state" --> console
```

- **Decisions live in files, not chat.** Teams write `gate.json`, you answer in the console, and the answer lands in `decisions/<id>.json` with a message to the lead.
- **The snapshot logger** mirrors agent screens, the OpenRig queue and research output every 10 seconds, so the console (and a supervising assistant) can follow the work without interrupting it.
- **Remote access** goes through Tailscale Serve: HTTPS, reachable only from your own devices, plus a console token.

---

## Repository layout

| Path | Contents |
|---|---|
| [`dashboard/`](dashboard) | Rig Console: `serve.py` (server and routes), `store.py` (event store), `gates.py` (decisions and builds), `features.py` (timelines, usage, evidence checks, push), pages, [`JOBS.md`](dashboard/JOBS.md), [`ROADMAP.md`](dashboard/ROADMAP.md) |
| [`briefs/`](briefs) | Team briefs and shared rules, e.g. the tiered [web access rule](briefs/RESEARCH-WEB-ACCESS-RULE.md) |
| [`studio/`](studio) | The game studio plan and rig templates (pitch rooms, prototype sprints, design team) |
| [`setup/`](setup) | WSL bootstrap, the snapshot logger, and services for the logger, the dashboard and WSL keep-alive |
| [`model-test/`](model-test) | A small harness for testing local Ollama models on agent tasks (JSON output, skeptic reasoning, tool calls) |
| [`SETUP.md`](SETUP.md) · [`CHEATSHEET.md`](CHEATSHEET.md) | The setup log with the reasoning behind each choice, and day-to-day commands |

Not in the repo, on purpose: live snapshots, research and job mirrors, run outputs, dashboard state,
the event database and every credential (those live in `~/.config/` inside WSL).

---

## Getting started

> Paths in the scripts point at this machine's folder (`/mnt/c/Users/<you>/…/OpenRig`). Adjust them for yours.

**Prerequisites:** Windows 11 with WSL2 (Ubuntu 24.04, mirrored networking), Node 22 via nvm, Python 3,
plus [Claude Code](https://docs.claude.com/en/docs/claude-code) and the Codex CLI, both logged in.

```bash
# 1. Base tooling inside Ubuntu
bash setup/bootstrap-wsl.sh

# 2. OpenRig
npm install -g @openrig/cli
rig setup --no-herdr && rig doctor

# 3. Snapshot logger + Rig Console as auto-starting services
bash setup/install-autostart.sh
bash setup/install-dashboard-service.sh
```
Then open **http://localhost:8800**. For the dashboard to survive Windows logons, run
`setup/install-wsl-keepalive.ps1` in PowerShell once.

**Phone access (optional):** install Tailscale on the PC and phone, set `RIG_CONSOLE_TOKEN` in
`~/.config/rig-console.env`, run `tailscale serve --bg 8800` in PowerShell, and open your
`https://<pc>.<tailnet>.ts.net/?token=…` link once. For push alerts, set `NTFY_TOPIC` (and `NTFY_CLICK`
to your console URL) and subscribe to the topic in the ntfy app.

---

## Safety model

- **Humans decide.** Teams stop at gates. Nothing that spends money, creates accounts, posts publicly or contacts people happens without an explicit approval. Validation outreach has its own phased brief with automatic stops.
- **Least access.** The console is reachable only from loopback or your Tailscale devices, and every remote request needs the token. Agent-written files are served sandboxed (no scripts), and decisions can't be answered on your behalf.
- **Web access is tiered.** Built-in tools first, then official APIs, an index service, and finally a logged-out browser at human pace for pages that decide a verdict. Never logged in, never solving CAPTCHAs, never bulk scraping. Every fallback is logged.

---

## Lessons so far

- **Agents follow a brief literally.** Listing the owner's interests in run 1 skewed seven of 25 ideas toward them. Run 2 removed them and got a far broader search.
- **Honest zero beats a padded shortlist.** Strict evidence bars produced "no finalist" more than once, and that was the right answer.
- **Approval prompts are the hidden cost.** Agents spent over 30 minutes waiting on prompts in one run. Pre-approved scripts and a dry run before dispatch fixed most of it.
- **Blocked pages hide evidence.** Marketplace and help-center pages often refuse bots, which biased research against marketplace businesses until the tiered web rule.
- **Fresh sessions and files beat long chats.** Handoff notes and decision files survive `/clear`; a 300k-token conversation doesn't.

---

## License

[MIT](LICENSE): use it, fork it, adapt it.

*Not affiliated with OpenRig, Anthropic or OpenAI. A personal project, shared in case the patterns are useful.
The screenshots show a replay of a real research run and a demo decision.*
