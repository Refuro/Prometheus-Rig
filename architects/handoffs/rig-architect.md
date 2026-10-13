# Handoff: Rig Architect (written by the Rig Architect chat session, 2026-10-12)

## 1. Scope in one paragraph
I set up the rig (WSL2 Ubuntu, OpenRig, Claude Code and Codex seats, the snapshot logger), wrote the
research and validation team briefs, supervised runs 1 and 2, money-1 and validation-1, and built Rig
Console until handing the codebase to the Platform Architect (PD-013). I now own the **shared rules**
(`briefs/SHARED-RULES.md`, the one home for cross-team rules), the research and validation templates,
`ROLES.md`, `SETUP.md`, `CHEATSHEET.md`, the architects rig brief, and `ARCHITECTURE-LOG.md` (PD-001 to PD-019).
Edges in practice:
- The Studio Architect proposes cross-team rules to me and keeps studio-only rules.
- The Platform Architect owns all console code and the contract files (`JOBS.md`, `NICHES-SCHEMA.md`).
  I request things.
- The Model Architect grades me; I answer in my log.

## 2. Current state
**Architects rig, 2026-10-13 (paused 03:30Z for usage, resumed 05:41Z).**
- Done since the seat launched (PD-023, PD-024):
  - Owner's Advisor role added to ROLES.md (PD-023).
  - Seat names fixed to `arch-*` and `review-codex` in brief.md (now v1.2, also with the console-sender
    and `--dangerously-interact` notes), README.md, all role files and ROLES.md.
  - Launch fix: `rig.yaml` gives each seat's cwd as an absolute path to the repo root, and README drops
    `--cwd .` (spec validates). It applies only after a relaunch.
  - Operator's work checked: installed SHARED-RULES v1.5, JOBS.md and NICHES-SCHEMA.md match the repo; the
    scratch folders exist; `launches/architects.json` has `seats`. No gaps, so no gate.
  - Permission policy: my plan is in `~/openrig/scratch/rig/permission-policy-architects.md`. The operator
    applied it in the repo-root `.claude/settings.local.json` (the source Claude actually reads) and in
    `architects/.claude/settings.json`.
- Open:
  - Permission fix **fixed and tested at 06:42Z**, after my premature "solved" at 05:48Z (see PD-024).
    - **Cause:** running sessions missed later outside edits to the rules file.
    - **Refresh:** a native `/permissions` save in each seat, then read back the file, diff it against the
      operator's Linux master copy, and probe twice.
    - **Hazard:** a save from a seat with an out-of-date view can drop newer rules.
    - **Owner option:** one settings file per seat.
    - **By design:** new tools still ask.
  - `architects/.claude/settings.json` is not gitignored, and the repo is public. I asked Platform
    (log note, PD-024).
  - The relaunch at the repo root (`rig.yaml` fix) is the owner's call.
  - Kickoff item 6 waits on the owner (validation-1 gate, D3). **validation-1 is on hold by the owner's
    choice** until they have free time for setup (2026-10-13). Don't nudge.

- **Later on 2026-10-13:**
  - PD-025 approved: SHARED-RULES v1.6 and brief v1.3. The operator installed them; verified with cmp.
  - **Lounge** (PD-026): I own its conventions; Platform owns the panel (R-019).
    - The owner gave a standing delegation: Rig and Platform decide future Lounge changes with no owner
      round, within the rules, and with no spending, publishing or privileged actions.
    - All architects were told on 07:43Z; Platform's notice waits in its queue.
  - **R-020 is live and verified (08:10Z):** four console items went to the operator, one per wait
    episode, each 46–55 s after the wait began, with no duplicates. Platform is dropping Claude's "Tip"
    line from the screen excerpt.
  - **SHARED-RULES v1.7 approved and applied at 15:31Z (PD-027):** reply files, daemon retries,
    own-folder launches; brief v1.4. Installed and verified identical with cmp (15:42Z). Relayed to the
    other architects as quiet queue notes.
    - **At validation-1's next launch** (from its own folder): the operator removes the validation
      CULTURE block from `~/openrig/CLAUDE.md` and `AGENTS.md`. See
      `scratch/rig/root-culture-leak-20261013.md`.
  - **My open owner cards** (`~/openrig/jobs/architects/tasks/`): `stylesteady-trademark`,
    `stylesteady-po-box`, `commit-oct-13`.
    - When one is answered: send the operator the `decisions/task-<id>.json` path in one line. The
      operator passes it to the validation lead, with no gate needed for that relay (agreed 08:20Z).
    - Never edit validation files.
    - A new brand name is still an owner gate.
    - After acting, delete the task file.
  - **"Needs you" (R-018) after the owner's 08:10Z correction:** a standalone inbox page with only To do
    and Questions cards. Gates, approval waits and alerts stay off it. Platform is building it now.
  - Owner-requested advice, written in `~/openrig/scratch/rig/` and relayed by the operator:
    `assets-1-gpu-memory-advice.md`, `owner-work-board-proposal.md` (the owner delegated the choice; filed as
    R-018 for Platform to build) and `architects-lounge-idea.md`.

The state below predates the architects rig and is partly stale. SHARED-RULES is now v1.6, and the
operator item in section 3 is verified.
- **Research:** runs 1, 2 and money-1 are closed. Run 2: 0 shortlisted; A07 (Word multilevel-numbering and
  template repair service) moved to validation; B05 cut; A02 (certificate-renewal automation) on the
  watch list until the 2027-03-15 certificate-lifetime step. The current research template is
  `briefs/research-brief-run-2.md`, with the section 0 answerability check (PD-014) and checkpoints as gates
  (PD-016). Neither is used in a run yet.
- **validation-1** (`~/openrig/research/validation-1/`, brief `briefs/validation-brief-1.md`):
  - Phase 0 done; the owner picked the brand **StyleSteady**.
  - **Open owner gate:** `phase0-plan`, with D2–D10 in `plan/user-gate.md`.
  - **Open owner choice D3:** desktop Word vs LibreOffice as the check engine. Not implied by approving the plan.
  - **Pending owner tasks:** manual USPTO search and a registrar re-check for StyleSteady (agents were
    blocked), and a PO box (needed before Phase 2 sends; the owner refuses to use the home address).
  - **After plan approval:** the owner's setup sitting (domain on Vercel, mailbox, Vercel token, creds in
    `~/.config/validation-1/`), then the 2–3 week warm-up.
- **Shared rules:** `SHARED-RULES.md` is at v1.3. The operator must keep installed copies in
  `~/openrig/briefs/`, together with `JOBS.md` and `NICHES-SCHEMA.md`.
- **Infrastructure:**
  - Rig Console runs as systemd `rig-dashboard`; the snapshot logger as `rig-snapshots` (every 10 s, into the
    OneDrive folder).
  - Phone access through Tailscale Serve (`https://prometheus.<tailnet>.ts.net`, token in
    `~/.config/rig-console.env`); push through ntfy (topic in the same file).
- **Repo:** `prometheus-rig` on GitHub, private, history cleaned once (PD-012). Going public is pending:
  - the Model Architect confirms its committed cards are safe to publish;
  - delete `_to_delete/`.
- **Plans:** Claude Max (upgraded 2026-10-12) and ChatGPT Pro ($100) for Codex. Local models (Ollama
  gemma4:12b, qwen3-coder:30b) are parked: their tool calls fail in agent loops.

## 3. Open items
| Item | Waiting on | Next step | Where it's recorded |
|---|---|---|---|
| validation-1 plan gate and D3 | Owner | After D3: add the check engine as an explicit prerequisite in `validation-brief-1.md` (PD-011 miss) | `research/validation-1/plan/user-gate.md` |
| PO box, USPTO, registrar | Owner | None until done; Phase 2 blocked | validation.json `waiting_on_user` |
| R-003 validation view | Platform | Should land before Phase 2 sends | `dashboard/REQUESTS.md` |
| R-005 security checks (interop, sudo) | Owner runs two commands | Platform decides step 3 | `models/reviews/R-005-R-006-security.md` |
| First use of answerability and checkpoint gates | Next research run | Grade the outcome in PD-014 and PD-016 | My log |
| Usage reading noting the Max switch | Owner | Run report page, usage form | — |
| A02 watch list | 2027-03-15 | One cheap re-check run | run-2 `lead-watchlist.md` |

## 4. Decisions that matter and why
- **Never name the owner's interests in a research brief** (PD-002 → PD-003). They anchored 7 of 25 ideas in run 1.
- **Honest zero over a padded shortlist,** and the answerability check: "no" questions become market tests
  (PD-003, PD-004, PD-014).
- **Web access rule v2** (PD-005), approved by the owner: built-in tools → official APIs → Exa → a logged-out
  browser at human pace. Never logged in, no CAPTCHAs, no proxies, no bulk scraping. Log every fallback.
- **Owner impersonation** (PD-017):
  - only `decisions/<id>.json` counts;
  - pushes come only from the console;
  - seats never edit the project folder (architects excepted, in their own files).
- **Validation guardrails** (the validation brief), which the owner accepted:
  - CAN-SPAM, US business contacts only, no fake personas, honest AI disclosure;
  - $0 agent spend, a separate sending domain;
  - staged autonomy (calibration batch → spot-check → autonomous), with automatic stops.
- **Alerts need corroboration** (PD-007). OpenRig's `agentActivity` alone is not evidence.

## 5. The owner: how they like to work
- **Goals:** a hobby and a way to learn AI engineering, with the ambition of a "factory" of income creation.
  Wants honest opinions and pushback ("don't be modest"). Agrees research has a ceiling and that real
  validation matters.
- **Communication:**
  - reads on a phone a lot (GrapheneOS);
  - wants short, plain-English replies, and exact commands to paste, with where to run them (Ubuntu or PowerShell);
  - asked for "who to tell + a snippet" for cross-role messages, then switched to notes in logs, and now
    to this rig because relaying was tiring. **Don't make them a message bus.**
- **Taste:**
  - loves watching systems work (animations, replay, feed);
  - wants a professional, minimal UI with a consistent nav across pages;
  - wants 125% zoom on wide screens without text overflowing;
  - hates repeated or false notifications.
- **Limits and values:**
  - **Interests out of research** ("I don't want my interests to poison their search").
  - **Web blocks:** OK with routing around them within the v2 tiers.
  - **Money and identity:** $0 budget beyond a domain, mailbox and PO box; no home address in emails; no business
    registration yet (Washington trade-name rule noted for when payments start).
  - **Outreach:** wants it fully automated, but accepted the staged-autonomy path.
- **Git:** the owner commits and pushes from Ubuntu (SSH key with a passphrase; `ssh-agent` tip given).
  Their commits carry no AI attribution lines, by their request.

## 6. Working knowledge
- **Paths:**
  - the repo is `/mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig` (in WSL);
  - the rig home is `~/openrig` (`research/`, `jobs/`, installed `briefs/`, `launches/`);
  - secrets live in `~/.config/` (`rig-console.env`, `exa.env`, `validation-1/`).
- **OpenRig commands:**
  - `rig ps --nodes -A --json`, `rig queue list -a -A --json`;
  - `rig send <seat> "<text>"`, `rig up ./rig.yaml --plan`, `rig down`, `rig capture`;
  - `tmux attach -t '<seat>'`, detach with Ctrl+B then D.
- **Things that broke before:**
  - **`agentActivity`:** shows `unknown` for idle Claude seats, and `running` when text sits typed but unsent
    in the input box.
  - **Shell prompts:** `$` inside double-quoted shell text triggers approval prompts, hence the shell rule.
  - **Codex seats:** sometimes get EPERM on `rig send`.
  - **Long sessions:** a Claude lead once stalled at "Usage limit reached" with about 374k context. Use fresh
    sessions and handoff notes.
- **Snapshot mirrors:** `snapshots/` (screens and JSON), `research-mirror/` and `jobs-mirror/` are copied
  with `cp -ru` every 10 s, so their mtimes are copy times, not real write times.
- **Web blocks:** Etsy, Fiverr, Medium and Zendesk help centers block bots; Exa reads many of them
  (free $10 credit, no card on file).
- **Phone:** Android allows one VPN at a time. Tailscale replaced DNSNet on the owner's phone.

## 7. Read first
1. `architects/brief.md`, `ROLES.md`, `briefs/SHARED-RULES.md`
2. `ARCHITECTURE-LOG.md` (PD entries, then Notes for other roles)
3. `briefs/validation-brief-1.md` and `~/openrig/research/validation-1/validation.json`
4. `briefs/research-brief-run-2.md` (the current research template)
5. `models/roles/rig-architect.md` (how I'm graded) and `models/LOG.md` "Notes for the Rig Architect"
6. `dashboard/REQUESTS.md` (what I've asked of the Platform Architect)

## 8. Don't
- Edit console code, `studio/`, `models/` or another architect's log. Request it instead.
- Write a rule in more than one place, or let seats keep rule copies in their memory.
- Send the operator anything without an approved gate.
- Give agents payment details, account creation or platform automation (LinkedIn, Reddit, Upwork,
  Fiverr bots).
- Let a research brief demand something public evidence can't show.
- Trust a single OpenRig signal for an alert, or ask the owner to relay messages.
