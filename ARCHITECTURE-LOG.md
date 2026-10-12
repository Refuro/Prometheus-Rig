# Rig architecture log

**Who writes here:** only the **Rig Architect**: the Claude session that set up the rig, owns the shared
rules and writes the research and validation team templates. (Rig Console was built here too, until the
Platform Architect took over the codebase; see PD-013.) The **Studio Architect** has its own log ([`studio/ARCHITECTURE-LOG.md`](studio/ARCHITECTURE-LOG.md)),
the **Platform Architect** keeps [`dashboard/ARCHITECTURE-LOG.md`](dashboard/ARCHITECTURE-LOG.md), and the
**Model Architect** grades all three. No architect edits another's log.
**Who reads it:** the owner, future Rig Architect sessions (read before changing the shared rules or the
research/validation templates), the other architects, and the Model Architect and its Codex reviewer
(read-only, as evidence). Agent seats never read or write it.

**Format:** same as the studio log: one entry per decision (what, why, what it replaced), and later
the outcome, written plainly, misses included. Rig decisions are numbered **PD-nnn**.
**Grading note for the Model Architect:** many of my "decisions" were made in conversation with the owner. Where
the owner directed something, the entry says so; judge me on the parts I designed and on what I advised.

---

## PD-001 Supervise by mirroring, not attaching (2026-10-11)
**Decision:** a logger writes every agent's screen, the OpenRig queue and ps state, and the research
folders into the synced project folder every 10 s, so a supervising session can read them without
touching tmux.
**Outcome:** holding. It made every later diagnosis possible (stalls, approval waits, a stuck usage
limit, false alerts), and later became the console's main data source.
**Cost:** a polling design. OpenRig's own activity signal turned out to be unreliable (see PD-007),
so screen-diffing had to fill the gaps.

## PD-002 Research brief v1 (run 1) (2026-10-11)
**Decision:** weighted scoring, a skeptic seat, a funnel of 25 → 8 → 3, owner checkpoints, and the
owner's interests as tiebreakers.
**Outcome: miss.** Listing the interests (and search lanes shaped by them) pulled 7 of 25 longlist
ideas toward one of them. Both deep dives were rejected. Approval prompts cost about 33 agent-minutes.
**What I'd change, and did in v2:** never name the owner's interests in a research brief. Search by
method, not by topic.

## PD-003 Research brief v2 (run 2) (2026-10-11)
**Decision:** no interests; at most 3 ideas per industry; two analysts with opposite methods
(complaints-first, spending-first); economics as a pass/fail gate at screen; the skeptic states what
evidence would overturn each objection; a lead rebuttal round; four verdict categories; permissions
and a dry run before dispatch; fresh sessions.
**Outcome:** partial hit. A broad, unbiased longlist and honest verdicts (0 shortlisted rather than
padded); overturn searches changed real verdicts (one became Contradicted, another was reinstated).
One niche found verifiable paid demand and moved to validation.
**Miss:** desk research hit its ceiling. "Paid premium settlements" and "buyer counts" can't be found by
reading pages, so the deep-dive bar was unreachable by design. Next time, a research brief should
say up front which questions only a market test can answer.

## PD-004 AI-income team, money-1 (2026-10-11)
**Decision:** a parallel team searching for AI-run income methods, requiring 3+ independent operators with
verified earnings.
**Outcome: miss, mostly in the question.** Zero survivors. Proof existed only for human-made work, and
operators rarely publish earnings. Blocked marketplace pages (PD-005) hid some evidence: a cover-design
gig with 14k reviews was invisible to the team. I recommended retiring the track rather than re-running it.
**Lesson:** test the question before building the team. "Can this question be answered with public
evidence at all?" is a five-minute check.

## PD-005 Web access rule: v1 never route around, v2 tiered (2026-10-11)
**v1:** built-in web tools only; a blocked page is recorded as blocked.
**Outcome v1: miss.** It systematically under-evidenced marketplace businesses (Etsy, Fiverr and Medium
pages refuse bots).
**v2 (owner approved):** built-in tools → official APIs → Exa → a logged-out browser at human pace for
verdict-deciding pages; never logged in, no CAPTCHA solving, no proxies or bulk scraping; every fallback
logged; the owner verifies still-blocked pages by hand.
**Outcome v2:** pending. The setup tested fine; first real use was validation-1's evidence review.

## PD-006 Rig Console: stdlib Python + static pages (2026-10-11 onward)
**Decision:** no framework, no build step, no dependencies; read-mostly; POSTs require a custom header
(CSRF); a phone view; features added as the owner asked.
**Outcome:** holding. Fast iteration: dozens of features in two days, each tested in a headless browser
before shipping. **Risk:** `serve.py` is near the size where it should split into modules (trigger noted
in ROADMAP).

## PD-007 Alert rules (2026-10-11 → 12)
**Decision:** alerts for approvals, usage limits, frozen screens, stuck handoffs, long busy streaks and
context ≥ 80%, with dismiss-until-cleared.
**Outcome: repeated misses, all false positives, each fixed after the owner hit it:**
- A normal blocked dependency flagged as stuck.
- Agents shown "active" on first sight.
- An idle lead flagged "frozen for 623 min": OpenRig reported "running" because of text typed but not
  sent, and the alert flapped, so the phone was re-notified repeatedly.
- Parked handoffs animated as live.

**Lesson (now the rule):** OpenRig's activity signal alone is not evidence. An alert needs corroboration
(a live spinner, screen change), must persist about 25 s before notifying, and is rate-limited per key
for 6 h.

## PD-008 SQLite event store and the jobs abstraction (2026-10-11)
**Decision:** add a real database once replay needed history; keep it in the Linux filesystem, not
the synced folder; use numbered migrations. Any folder under a watched root is a job (`job.json`;
custom events via `events.jsonl`). Research is one job type, not the shape of the system.
**Outcome:** holding. Studio jobs (pitch, depth, friends, proto, coop) appeared in the graph, feed, replay
and gates with no console changes.

## PD-009 Gates in the console (implements studio AD-004 on the console side) (2026-10-11 → 12)
**Decision:** `gate.json` → a decision page → `decisions/<id>.json` plus a `rig send` to the lead;
choose and approve kinds; option cards with Read and Play; background docs rendered in place, with an
in-page reader that follows file links.
**Outcome:** holding. Decisions arrive within minutes, including from the phone.
**Misses so far:**
- No way to close a gate decided elsewhere (stale proto-1 gate). Added "Close without deciding"; the
  operator closes gates for chat decisions.
- The background doc first opened as a raw text link; now rendered.
- **Open:** the console enforces `max` strictly, but the owner has exceeded maxima by note
  (friends-1, 4 of max 3). Candidate: an optional `"max_soft": true`, so the owner can go over with a
  confirm.

## PD-010 Remote access and push (2026-10-11)
**Decision:** Tailscale Serve (HTTPS, reachable only from the owner's own devices) plus a console token
and cookie; ntfy push with tap-to-open; the token never stays in URLs.
**Outcome:** holding after one miss: a `SameSite=Strict` cookie broke opening the console from a
notification tap. Fixed with `Lax` plus a sign-in page. Also: the owner's phone VPN app conflicted with
Tailscale (Android allows one VPN). Setup docs should warn about that.

## PD-011 Validation brief v1 (2026-10-11)
**Decision:** phased outreach: plan → build and warm-up → owner-approved calibration batch → autonomous,
with automatic stops (bounces, complaints, angry replies). CAN-SPAM compliant, US business contacts only,
no personas, honest AI disclosure, $0 agent spend, a separate sending domain. An evidence review came
first (owner request).
**Outcome:** pending. Phase 0 produced a plan and two gates. The open owner dependency (Word vs
LibreOffice for delivery checks) was surfaced by the team, not by the brief: the brief should have
asked it.

## PD-012 My own supervision misses (for the report card)
- I assumed the operator was answering approval prompts; it was the owner, by hand.
- I generalised from one competitor page during run-1 discussion (later corrected).
- I suggested HOST=0.0.0.0 for remote access before proposing the tighter Tailscale Serve setup;
  I switched once the owner asked whether it was trustworthy.
- First git commits contained personal details that later needed a history rewrite before going public.
  Check before the first commit, not after.

## PD-013 Hand the console codebase to a Platform Architect (2026-10-12)
**Decision:** a dedicated Platform Architect session owns `dashboard/`, `setup/`, tests and repo hygiene,
with a charter (`PLATFORM-ARCHITECT.md`), a request inbox (`dashboard/REQUESTS.md`) and its own log.
Before handing over: every data path was made overridable by environment variables, and a stdlib smoke
test (`dashboard/tests/smoke.py`, 45 checks on fixtures) was added. The Rig Architect stops editing console
code and files requests instead.
**Why:** the console reached about 5.5k lines, the repo is public, and three architects now want features.
A code-focused session with tests is cheaper and more careful than a long supervision chat doing it.
**Outcome:** pending.

## PD-014 Response to the Model Architect (models/LOG.md, MA-004 notes) (2026-10-12)
All four recommendations adopted:
1. **Shell rule:** adopted for every seat, any model: no `$`, backticks or pipes in shell text; free text
   through files; one command per call. It's in `briefs/SHARED-RULES.md` section 4. The Claude seats in
   run-2 and validation-1 lacked it; that was my gap (O039, O045, O048).
2. **Stop and capacity rules** (the Studio Architect's proposal, AD-014 notes): adopted as cross-team
   rules, `SHARED-RULES.md` sections 2 and 3, worded close to the studio's text so studio rigs don't need
   to change. They're consistent with the existing "pause on usage warnings" rule, because capacity
   errors are not usage limits.
3. **Answerability check:** added to the research template as section 0. Each funnel question is marked
   answerable from public evidence or not; "no" questions become market-test recommendations, not
   research bars. This answers PD-003's and PD-004's misses.
4. **Who answered the run-1 approval prompts (O064):** the owner, by hand. The evidence is the owner's
   own words to me during run 1 ("I've been going in and accepting when they get stuck, the operator's
   been idle"), which corrected my assumption at the time. The run-1 retro's "until the operator approved
   them" is inaccurate. It isn't in a file the Model Architect can cite except here, so this entry is
   the record. The Operator shouldn't be credited or debited for run-1 approvals.

**Also new:** `briefs/SHARED-RULES.md` is now the single home for cross-team rules (decisions as gates,
gates for owner decisions only, stops, provider errors, shell commands, the outside world, run start and
end). That includes the Model Architect's end-of-run model-notes line, extended to research and
validation runs. The research and validation briefs and the web rule now point to it.
**Outcome:** pending: first measured in the next research run and in validation-1's remaining phases
(watch for approval events per seat and for stops that aren't on the list).

---

## Notes for the Studio Architect (input, not edits)
- **Operational problems belong in alerts, not gates.** AD-003's three provider-capacity blips became
  owner gates. Gates should hold owner decisions only; the console already alerts on usage limits and
  stalls. AD-010's retry policy addresses the cause.
- **Gate maxima:** see PD-009. If owner overrides are expected, add `max_soft` to the template rather
  than relying on notes.
- **Close gates on chat decisions** (now an operator rule) so the owner's "Needs you" list stays true.
- **Console support available today** for the next round: `events.jsonl` for playtest-bot and sync-test
  results, Play builds for web exports, and per-option `play` links in prototype gates.
