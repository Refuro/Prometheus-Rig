# Architecture log

**Who writes here:** only the studio architect: the Claude chat session that
designs the studio, or any session the owner explicitly names as architect.
**Who reads it:** the owner, future architect sessions (read this before
changing any template), the model analyst and the Codex reviewer (read-only,
as evidence). **Studio seats never read or write it**; their instructions
live in their briefs.

**Format:** one entry per design decision: what, why, what it replaced, and
later the outcome. Outcomes are filled in when evidence arrives, with links.
Misses get written down plainly; this log exists to learn from them.

---

## AD-001 Prototype-first studio (2026-10-11)
**Decision:** narrow ideas by playing cheap prototypes, not by writing design
docs. Stages: pitch → prototype → vision → production, each its own rig, the
owner deciding at every gate.
**Why:** agents build grey-box toys in hours, so "is it fun" can be answered
by playing.
**Outcome:** holding. The owner played six round-1 prototypes within a day,
and that play produced the sharpest feedback of the project (depth, clarity,
cheese).

## AD-002 Pitch room v1 (2026-10-11)
**Decision:** collision hands (verb, setting, constraint, odd input), one
Claude and two Codex pitchers working independently, a Codex novelty scout,
a Claude curator with a per-pitcher quota.
**Why:** push past "pitch me a game" averages; spread across model families.
**Outcome (pitch-1 → proto-1):** partial. Novel premises, but all judged as
two-minute toys; the brief never asked about the late game. Owner: "if the
whole game is the same, people will get bored quick." Miss: the brief
optimised for hook and toy-ability only.

## AD-003 Prototype sprint v1 (2026-10-11)
**Decision:** one question per prototype, one-day toy, web export, the lead
reviews code against the spec, **at most one send-back** per toy.
**Why:** keep prototypes cheap and prevent review loops.
**Outcome (proto-1): miss on two points.**
- The one-send-back cap shipped known cheese: the lead's b-06 review said the
  raised jump speed "enables a direct moving-wall-to-exit shortcut that needs
  no bruise at all", but it had to accept. The owner then found "you can cheese
  everything." Evidence: proto-1/reviews/lead-b-06.md.
- Explanations lived in HOW-TO-PLAY files, not in the game; the owner didn't
  know what to do with the cheese in a-07 although the file said so.
- No stop or retry policy in the template: three provider-capacity blips
  became three owner gates around 23:30 (proto-1/decisions/provider-capacity-*).

## AD-004 Owner decisions through Rig Console gates (2026-10-11, owner rule)
**Decision:** every owner checkpoint is a gate.json in a job folder; teams
never ask in chat or write decisions. Every stage runs as a console job.
**Outcome:** holding. Decisions arrive within minutes, the owner can decide by
phone, and gate maxima are sometimes exceeded by owner note (friends-1 pick 4
of max 3), which leads handled correctly.

## AD-005 Round 2 pitch rooms: two tracks, depth gates, blind judging (2026-10-12)
**Decision:** split into a depth room (single-player, simple premise, real
depth) and a friendslop room (2-4 online co-op). Cards must describe the late
game, variety engine and own exploit; a Codex depth critic gates on Depth and
Exploit-proof (depth) or Friends moment and Tenth session (friends); all
cards judged blind; returning ideas rewritten by a reviser and entered blind;
all pitchers Codex to save Claude usage.
**Outcome (depth-1, friends-1):** mixed.
- Hit: blind judging held; the rewritten Roll Up the Distance made the board
  on merit. Every card had a real late game. Rooms ran 15-18 minutes.
- Miss: the depth critic gated nothing (24 of 24 passed, 15 at depth 5), so
  the curator filled the gap with unlabelled judgment calls, applied
  unevenly (x-16 Catch the Echo cut for clarity 3 while x-13 with the same
  scores made the board; x-08 lost to a lower-depth card on watchability).
- Miss: the depth rubric favoured closed puzzles (exploit-proofing is easiest
  to argue there), so all 8 board cards were deterministic puzzles.
- Miss: the friendslop deck I wrote (move/deliver cards) pulled 4 of 6 board
  cards toward moving-company games.
- Miss: dealt hands lost to free pitches in both rooms (depth: 5 of 8 board
  spots from 6 free cards; friends: 4 of 6 from 6).
- Miss: no near-miss lane. Strong cores failing on fixable write-up gaps
  (friends x-12 Pass the Floor) were simply cut.

## AD-006 Prototype sprint v2 (2026-10-12)
**Decision:** title card from ABOUT.txt (build fails while it has [TODO]),
contextual hints, three beats on keys 1/2/3, the spec's exploit must be
closed, a Codex depth critic reviews code for exploits before the lead.
Prototypes are throwaway.
**Why:** answers AD-002 and AD-003 misses.
**Outcome:** pending (proto-2 running). Early: builders stopped on trivial
errors under a lead-written "any tool failure" stop rule; leads clarified it
case by case.

## AD-007 Co-op prototype template (2026-10-12)
**Decision:** scaffold with host-authoritative ENet (clients send inputs, host
simulates and broadcasts state), Host/Join-by-address menu, an automated
multi-instance sync test (headless host plus bot clients must end in the same
state, free port per run), Windows zip with a download page, friends join
over Tailscale. No voice chat or GodotSteam in prototypes.
**Evidence at decision time:** sync test passes with 3 clients, fails on an
injected 0.3-unit drift, runs in parallel; Windows export zips. Not tested:
the .exe on real Windows PCs over Tailscale.
**Outcome:** pending (coop-1 running).

## AD-008 Design team template (2026-10-12)
**Decision:** creative director and systems designer always on; balance,
onboarding, narrative, brevity editor and art director woken on demand.
Brevity enforced twice (a Codex editor cuts Claude text; check_text.py fails
over-budget strings and banned AI phrases). Cheese policy: bug / degenerate /
clever. Discovery inbox; pillar changes only through an owner amend gate;
10-15% exploration budget per milestone. Design lives in data.
**Outcome:** pending (not yet launched).

## AD-009 Production as a clean build; asset pipeline research (2026-10-12, owner direction)
**Decision:** production starts a new project designed for Steam
(GodotSteam) from day one; prototypes are reference only. A research job
compares asset routes (Codex images, agent-driven Blender, text-to-3D, local
generation, procedural, CC0) with a bake-off and a gate.
**Outcome:** pending.

## AD-010 Stop policy, capacity retries, second send-back, lead-judgment labels (2026-10-12)
**Decision (relayed to the operator for all studio rigs):** stop only for
approval prompts, usage-limit warnings or approved tools failing to run;
transient capacity errors retry at about 2, 5 and 10 minutes before a single
operator note; a second send-back is allowed when a finding defeats the
prototype's question; known exploits lead every prototype gate summary; cuts
against the critic or scout are labelled "lead judgment" and listed as near
misses.
**Why:** AD-003 and AD-005 misses.
**Outcome:** pending. Not yet written into the templates themselves (do that
with the next-round changes).

## AD-011 Next-round backlog (2026-10-12, deferred by owner)
Clarification channel (prototype lead → room-lead), lessons.md loop from
prototype gates to the next pitch round, per-role playbooks (memory as
files, pitchers never see what won), deck changes (fewer move/deliver cards,
more free pitches), critic calibration anchors and forced bottom-third
ranking, near-miss lane with revise-and-resubmit, and AD-010 written into
the templates. Details: STUDIO-PLAN.md, "Planned for the next round".

## AD-012 Model analyst role (2026-10-12)
**Decision:** a separate Opus session keeps an evidence ledger, metrics and
role report cards keyed by model x role x brief, a routing guide, and
head-to-head experiment proposals; a Codex reviewer checks it for bias.
The architect (this log's author) is in its scope too.
**Why:** much observed "model behaviour" was really brief behaviour; route
and write briefs on evidence.
**Outcome:** pending.
