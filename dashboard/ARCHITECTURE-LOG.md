# Platform architecture log

**Who writes here:** only the Platform Architect (see `PLATFORM-ARCHITECT.md`). Entries are `PL-nnn`:
what, why, what it replaced, and later the outcome, misses included. Read-only for everyone else.

The console's history before the handover is in the Rig Architect's log (`ARCHITECTURE-LOG.md`, PD-001
to PD-013).

## PL-001 Handover assessment (2026-10-12)
**What:** a first read of the codebase, the smoke test and the open requests. No code was changed.

**Baseline:** smoke test 45/45 green on the code as handed over. I ran it in a copy outside WSL
(Python 3.13), not in the service's WSL Python. It took 0.4 s; the charter says about 20 s.

**Data flow (as I understand it):**
1. `setup/rig-snapshots.sh` runs every 10 s. It writes `_ps.json`, `_queue.json`, `_ctx.json`, one
   screen per tmux session and `activity-log.csv` into `snapshots/`.
2. The `serve.py` watcher, also every 10 s, calls `graph()`. That reads the snapshots and builds nodes,
   edges and alerts: limit, approval, frozen, long, handoff, context, plus open gates from
   `gates.list_gates()`. Dismissals apply here.
3. `store.Collector` turns the graph and queue into events in SQLite. It also adds job files and
   `events.jsonl` lines.
4. `features.track_approvals` logs approval waits.
5. `features.push_alerts` sends an alert to `ntfy.sh/<topic>` once it has persisted for 25 s and wasn't
   pushed in the last 6 h. Its Click URL opens `/m.html`, or the decision page for a gate.
6. The pages poll the `/api/*` routes. Decisions go through `POST /api/gate`, which writes
   `decisions/<id>.json` and `.md`, then runs `rig send` to the lead.

**Health:** good for its age. The code is small and readable (~4.4k lines), stdlib only, with numbered
migrations, path overrides and a fast smoke test on fixtures. Alert logic carries real lessons
(PD-007). Weak spots:
- `serve.py` mixes routing, auth, screen parsing and actions.
- The `graph()` alert rules, where every past miss happened, have almost no direct tests.
- `/api/briefs` reads a hard-coded `~/openrig/briefs` with no env override, which breaks charter rule 3's
  "every path is overridable".
- Three backup pages still ship.

**Top three risks:**
1. **Anything on the PC counts as the owner.** Requests from loopback that aren't proxied skip the
   token. Seats run in the same WSL, as the same user, so any seat (or a prompt injection it reads on the
   web) can `curl -H 'X-Rig-Console: 1' localhost:8800/api/gate` and answer its own gate, or use
   `/api/send`. A seat can also simply write `decisions/<id>.json` in its own job folder. So "nothing
   answers a gate on the owner's behalf" holds for the console UI, but not against a seat. This blocks
   R-002 as written: a console that approves permission prompts would let a seat approve its own
   commands.
2. **Agent-written builds run as the console.** `/play/` is served without `Content-Security-Policy:
   sandbox` (it can't use it, because builds need scripts). A build's JavaScript therefore runs on the
   console's origin with the owner's cookie and can POST to any API, including gates. Builds come from
   prototype seats. `/data/` (the research dir) is also served without the sandbox header, so an `.html`
   file written there runs the same way.
3. **The alert logic is the most-fixed area and the least tested.** The four PD-007 misses were all in
   `graph()`, which the smoke test covers only at "returns nodes". A `serve.py` split (R-004) or new
   alert kinds (R-003) could quietly regress them. Characterisation tests come first.

**Also noted (smaller):**
- Setup scripts hard-code `/mnt/c/Users/<name>/…`, which puts a username in a public repo.
- The env template suggests `HOST=0.0.0.0` for Tailscale. PD-010 replaced that with Tailscale Serve to
  localhost.
- The evidence checker fetches any URL an agent writes, LAN addresses included. GET/HEAD only, so this is
  low risk.
- ntfy.sh is public. Alert text (seat names, gate titles) is readable by anyone who guesses the topic.

**Outcome:** pending. Measures: whether risks 1 and 2 are closed before R-002 ships, and whether any
alert regression ships during the split.

## PL-002 System page in the console (2026-10-12)
**What:**
- A new page, `system.html` ("System" in the desktop nav and the phone footer), in three sections:
  - What runs where: four lanes (agents → files → console → you), with live status dots.
  - How a seat's need becomes a phone alert and a decision: eight steps.
  - Who owns what: the roles from `ROLES.md`.
- The status uses only GET APIs that already exist (`health graph gates builds jobs events`). There is no
  server change, so no restart is needed.
- I also wrote `docs/SYSTEM.md`, with the same three views as Mermaid, for readers on GitHub.

**Why:** the owner asked for a system graph like the README's, viewable in the dashboard. Mermaid
needs a CDN or a dependency (rule 2), so the page is plain HTML/CSS. It stacks into one column on a
phone.

**Checked:**
- Smoke test 47/47. New checks: the page is served and linked from both navs.
- Headless Chromium on fixtures at 1366 px (light) and 390 px (dark): no page errors and no sideways
  scroll. The live lines read correctly, including a stopped logger shown in red.

**Miss:** I first built only `docs/SYSTEM.md` (Mermaid for GitHub), because I read "like the one in the
README" as "in the docs". The owner meant the dashboard. I should have asked one question first.

**Debt:** the diagram now exists in three places: the README, `docs/SYSTEM.md` and `system.html`. Any
change to the data flow must update all three in the same commit.

**Redesign (same day, owner feedback: "too much text; use the live graph's design language"):**
- The page is now a map in the live graph's style: dot grid, group boxes, two-line cards, amber dashed
  edges for flow happening now, red for trouble, a detail panel on tap.
- The explanations moved off the map into the panel.
- The 8 steps became "Trace an alert", which plays the journey on the map with a moving spark.
- "Who owns what" became a People view of the same map.
- Edges are drawn from the cards' real positions, so the layout holds at any width. On a phone the
  groups stack with one spine between them, the real edges appear only during a trace, and the caption
  pins to the bottom.
- Checked with headless Chromium at 1440 px (dark and light) and 390 px: overview, node, trace and
  People view. No page errors and no sideways scroll. Smoke test 47/47.

**Outcome:** pending. Measure: the page stays accurate, and the owner uses it.
---

## Notes for the Rig Architect (input, not edits)
- **Gate integrity depends on seats.** A seat can write its own `decisions/<id>.json`, or call the
  console API from inside WSL (PL-001, risk 1). Until the console runs as a separate user, briefs should
  keep saying "never write files in `decisions/`". I'll add a console alert for decision files the
  console didn't write.

## Notes for the Studio Architect (input, not edits)
- **Builds will lose console access.** Builds under `builds/` currently run with full console access
  (PL-001, risk 2). Once R-006 lands, builds will be served from a separate origin (port), and links
  from gates keep working. No template change is expected; I'll confirm in the PL entry.
