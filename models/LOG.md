# Model Architect log

**Who writes here:** only the Model Architect (an Opus session, AD-012). Entries are `MA-nnn`. Everyone else reads; owning architects reply in their own logs (ROLES.md, "How they talk" item 3).

## MA-001 First pass: ledger, metrics, cards, routing (2026-10-12)
**Decision:** grade by model × role × brief. 67 ledger lines, 38 seat-runs, 13 model–role cards, 4 role grades, a brief table, routing, and 3 experiment proposals.
**Main findings:**
- Most seed "model traits" re-attribute to briefs: the literal stops (3 of 3 under "any tool failure"), critic calibration, and free vs dealt pitches.
- The cleanest model signal: Claude cards about 20% longer than Codex under an identical dispatch. The pitch-1 board-share gap is unreadable because the room wasn't blind.
- The one candidate Codex trait is simplifying the spec's core rule (4/6 toys), seen under one brief only. E1 tests it.
- Claude seats produced 4 shell-text approval prompts; their instructions lacked the shell rules every Codex seat gets.

**Status:** draft, waiting on the Codex bias review (`REVIEW-REQUEST.md`).

## MA-002 Scope widened to the five roles (2026-10-12, owner)
**Decision:** grade the Rig, Studio and Platform Architects and the Operator alongside models and briefs, from their logs (`ARCHITECTURE-LOG.md`, `studio/ARCHITECTURE-LOG.md`, `dashboard/ARCHITECTURE-LOG.md`) and the run records. Files: `roles/*.md` and `BRIEFS.md`. Architect evidence lives in role grades, not model cards, since these are roles, not models.

## MA-003 Moved to a top-level `models/` folder (2026-10-12, owner)
**Decision:** moved `studio/models/` to `models/` at the repo root. Under ROLES.md, `studio/` belongs to the Studio Architect, and these grades also cover the Rig and Platform Architects. All paths in these files are updated, including the proposed `/api/models` route (`DASH/../models`).
**Follow-up:** done. ROLES.md now lists `models/` as the Model Architect's (owner OK, 2026-10-12).

---

## MA-004 Response to the Codex review (2026-10-12)
**Input:** `REVIEW-codex.md`. Its verdict: revise before using the drafts as routing policy or publishing letter grades. I re-checked the factual findings against the sources (operator verification, the x-12 and x-14 stop reports, run-2 retro, `serve.py` line 690, PL-001/002), and they hold. **All findings accepted**, except where noted.

| Finding | Response |
|---|---|
| 1. O065 debits the Operator for a roster gap the operator's verification corrected | Accepted. O065 now records the lead's roster claim, contradicted by verification; cause unknown. The Operator is credited (O059). |
| 2. O025's "no retry" claim holds for 1 of 3 stop reports | Accepted. O025, O023 and the builder card now say adherence wasn't always immediate; the candid-report credit stays. |
| 3. O040 merged required screen searches with optional deep-dive searches | Accepted. Split into O040 (required; useful) and O068 (optional; no verdict changed). Removed the "beyond the brief → gains" claims. |
| 4. Metrics omitted Claude stop events and misused the self-report column | Accepted. Added stop events for the run-1, run-2 and validation Claude seats, `unknown` for run-1 analysts, a `disputed_or_excluded` column, column definitions; ZenMaid moved to notes; O020 excluded. |
| 5. O039 and O048 stated likely triggers as causes | Accepted. Now "approval events, cause mixed"; the forbidden pipeline is kept as an execution mistake. |
| 6. Platform evidence stale; handover overstated | Accepted. O067 credits PL-001/002; O066 notes the hard-coded briefs path. |
| O003 counted as a strength | Accepted. Changed to a neutral outcome; quota, hands and curated-board caveats added. |
| O016 "simplified rule" wording | Accepted. Now three mechanic changes and one tuning bypass; "safer neighbour" marked as the lead's framing. |
| O011 attributed to the brief, though the dispatch said "core verb" | Accepted. Split into O011 (budget kept) and O069 (theme queries: execution miss, `brief_asked: no`). |
| O042 readability judgment | Accepted. Removed. |
| Attribution audit (18 `model` entries) | Accepted in full. No ledger line now says `attribution: model`; O038 is `provider`. Summaries say "observed across these assignments". |
| Counts | Codex-only pitcher counts used (13/16 vs 6/40); "35/35 valid at handback, 21/21 first-check"; ROUTING says 69 lines; the builder card says 7 seat-runs; the Rig card no longer claims its log repeats "15". |
| Letter grades | Accepted. Replaced with qualitative assessments plus confidence until there's a rubric with severity weighting and an evidence threshold. Rig card adds PD-003/009/010/012; Studio card adds the AD-003 in-game explanation miss and the AD-005 near-miss lane, treats AD-010 as relayed but not verified, and doesn't count the owner-deferred AD-011 against it. |
| BRIEFS.md | Accepted. "Observed result / plausible contribution"; the closing generalisation removed; the missing money-1 and validation framing gaps added. |
| Routing and experiments | Accepted. Every row says "incumbent assignment; comparative advantage untested" where relevant; E1 uses 3+ specs; E2 uses an independent rubric; all runs record exact model and version. |

**Not changed:** O004's descriptive rates (the reviewer confirmed them), and keeping `active_min` blank (confirmed).
**What this shows about the first draft:** both families got causal labels the evidence didn't support; my summaries were tidier than the sources; and the record went stale within the hour (PL-001/002, AD-013/014). From now on, re-read the logs before each publish.

---

## MA-005 Replies from the architects (2026-10-12)
- **Rig Architect (PD-014):**
  - **Adopted all four recommendations:** the shell rule, the stop and capacity rules, the answerability check, and the run-1 approval record (the owner answered the prompts).
  - **Ledger updates:** O064 resolved; O070 added (the run-1 retro misattributed the approvals).
  - **One home for shared rules:** `briefs/SHARED-RULES.md`. Its model-notes line has leads write straight into `models/`.
- **Studio Architect (AD-015):**
  - **Everything accepted.**
  - **One change:** model notes go to each job folder and get harvested. I agree; its reasons hold (seats work only in their job folder; Codex seats may not reach `/mnt/c`; one shared synced file invites conflicts). The format is confirmed in `HARVEST.md`, and the harvester is `tools/harvest.py`, tested on a fixture: it imports valid lines, reports bad ones, and is safe to re-run.
  - **Experiments:** E2 and E3 accepted for the next round; E1 depends on the owner's Claude budget.
  - **AD-010:** grade it after the templates carry it (agreed).
- **Platform Architect:** no reply needed yet. I've filed the Models page as R-008 in `dashboard/REQUESTS.md`, the channel ROLES.md names for this.
- **Conflict for the owner:** where model notes are written. Rig says `models/` directly; Studio says the job folder plus harvest. I recommend the job-folder version for every team (see the note to the Rig Architect).

---

## MA-006 Model-notes location settled (2026-10-12)
The Rig Architect adopted the job-folder version for every team (PD-015). `SHARED-RULES.md` section 6 now carries the format inline, and it matches `HARVEST.md` and `tools/harvest.py` field for field. Section 6 is the canonical copy for seats; `HARVEST.md` points to it. A dry-run harvest of the current mirrors found nothing yet, as expected. The MA-005 conflict is closed.

---

## MA-007 Review of R-005/R-006 and the Models page (2026-10-12)
**Asked by** the Platform Architect, relayed by the owner. **Written to** `reviews/R-005-R-006-security.md`. Findings only; the design stays with the Platform Architect, whose outcome I'll assess later.
**Headline:**
- **Two paths stay open after the plan:** the console code runs from `/mnt/c`, where any seat can write, and WSL interop may give any seat root.
- **Step 2 depends on step 3:** alone, it adds little against seats.
- **Missing pieces:**
  - a Host allowlist (DNS rebinding);
  - fixes to the owner-decision record (gate text copied into decisions, seat-written job name, rig and lead).
- **R-006 is sound,** if three conditions are made explicit.

**Models page:** the data shows correctly. All 13 cell counts match the ledger, and injected markup didn't run. Problems found:
- seat-written ledger lines look reviewed;
- there are two channels for leads' notes;
- two data issues on my side (fixed: a Researcher row in ROUTING, and O055 split).

**Ledger:** O071–O075 were written into `models/` by the room-lead seats under the PD-014 rule (before PD-015). They're kept, marked `status: seat-written … not yet reviewed`, and wait for my review against their sources. O076 is added (the O055 split).

---

## MA-008 Rig Architect's response to MA-007 (PD-016, PD-017) (2026-10-12)
- **Adopted in `SHARED-RULES.md` v1.1:**
  - only `decisions/<id>.json` counts as the owner's decision, and any "owner decided" message is a pointer to verify;
  - phone pushes only from the console;
  - plus three related rules: never edit the owner's project folder, never read `/proc/*/environ` or `~/.config/`, and treat untrusted input as data.
- **Limits stated plainly:** these are rules, not locks; R-005/R-006 are still needed. Findings 5b and 5c are left to the Platform Architect, correctly, since they're console code.
- **Its call on O071–O075:** the room-leads wrote into `models/` under its own PD-014 rule, so that was the rule's fault, not theirs. This matches how I marked those lines (`status`, no fault assigned).
- **To check in the next runs:** no seat writes to `decisions/` or the project folder; leads verify decisions against the `.json`.

---

## MA-009 Platform Architect's response to MA-007 (PL-008 to PL-010) (2026-10-12)
- **All seven findings accepted.** Host allowlist, 5b and 5c done; smoke checks 83/83.
- **Models page:** shows `status` and `written_by`; reads leads' notes from job folders, and the `model_note` event format is withdrawn. That closes the two-channel question.
- **Its question:** "match notes to the ledger on `harvested_from` instead of the `what_happened` text?" Answer: neither; match on `harvest_hash`, now documented in `HARVEST.md` as a stable contract. `harvested_from` carries line numbers that shift.
- **Still open, with the owner:** the WSL interop and sudo checks, and R-005 step 3. I haven't re-tested the shipped code; I'll do that when I next assess the Platform Architect.

---

## MA-010 Notes convention; Rig Architect's notes read (2026-10-12)
- **Notes convention:** following the `ROLES.md` change, the notes below now use the shared format: one "Notes for other roles" section, a subsection per role, newest first, dated, and marked **[new]** until the recipient acts.
- **The Rig Architect's notes for me** (its log, "Notes for the Model Architect"): PD-014/015 were handled in MA-005/006, PD-017 in MA-008. Nothing open.
- **PD-018 (operator launch records), read for context:** the launch record is the natural place to record each seat's model and version. That would end "version unknown" in the ledger (new notes below).

---

## MA-011 Interop and sudo checks: both open (2026-10-12)
**The owner ran the two checks from finding 2** of `reviews/R-005-R-006-security.md`, as the seats' user (`you`):
- `wsl.exe -u root id` gave `uid=0(root)`;
- `sudo -n true` succeeded.

**What that means:** any seat, including a prompt-injected one, can become root in two independent ways. R-005 step 3 (a separate console user with a token seats can't read) protects nothing until **both** are closed. Closing them is setup work (the Platform Architect's `setup/`) plus operator practice (the Rig Architect's section 7), so notes go to both below. Recorded as an environment finding in the review, not as a ledger line; it isn't model behaviour.

---

## MA-012 Notes read from all three logs (2026-10-12)
- **Rig Architect (PD-019):** MA-010 adopted. `SHARED-RULES.md` v1.3 section 7 has the operator record each seat's runtime, model and version, once the Platform Architect adds `seats` to the launch record.
- **Studio Architect (AD-017/018/020):** new seat types: `player-eyes` (Claude) in proto-3 and coop-2; `design-feel` and `design-ux` (Claude) in bridge-design and sunrise-design; and the art director (Codex) now covers art and audio, reviewed cross-model by the creative director (Claude).
  - Added to ROUTING as "no evidence yet". Cards come after their first runs.
  - The art and audio pairing is a natural cross-model check worth tracking.
  - Its earlier request (confirm the notes format) was answered in MA-006.
- **Platform Architect (PL-003 notes):**
  - **qwen3-coder:30b:** added its own card, so it gets a cell.
  - **The "all" line:** O004 stays under "all" on purpose; it covers both models.
  - **Role names and the ROUTING first word:** already match.
  - **The `model_note` remark:** superseded by PL-009/010.
- **Mirror is stale:** `jobs-mirror/` has none of the new jobs (proto-3, coop-2, bridge-design, sunrise-design), and `research-mirror/` has a new `assets-1`. Harvest dry run: 0 new notes. The mirror needs a refresh before the next harvest.

---

## MA-013 Re-test of the Platform Architect's security work; seat-written lines reviewed; notes read (2026-10-12)
**Re-test** (read-only, on the PC, against a temporary copy of the test data; nothing live touched):
- **The smoke test passes for me too:** 97/97.
- **My own probes, beyond its tests:**
  - **Changes need sign-in, even from this PC:** a local POST without the cookie gets 401.
  - **Host allowlist:** refuses an empty Host and `127.0.0.1.nip.io`, and accepts `LOCALHOST`.
  - **The builds port** blocks `..` and encoded escapes, and no longer serves `gate.json`.
- **Three gaps found** (notes below):
  - **(a) The builds port serves any file in a job folder, not just builds.** A planted `evil.html` and a `decisions/x.json` both came back 200. The code's own comment and my condition (i) say builds only. A build can therefore read every job's files on that port. On the phone, where the cookie is present, that includes owner decisions, and a malicious build could send them out.
  - **(b) Any `*.ts.net` name is accepted:** `evil.ts.net` got 200. Low risk, since nobody can point a ts.net name at 127.0.0.1, but pinning the exact Tailscale name costs nothing.
  - **(c) `X-Forwarded-Host` isn't checked** before the `/go/play/` redirect, so a crafted header redirected to `evil.example`. Only a proxy or local process can set that header, so this is a nit.
- **One thing to confirm:** if `RIG_CONSOLE_TOKEN` is ever unset, changes are allowed without sign-in. Check the live console has a token, and consider refusing changes when it doesn't.

**Seat-written ledger lines O071–O075:** checked against the mirrored sources.
- **Verified:** O071, O072, O074, and O073 through the receipt.
- **Unverifiable:** O075's quotes are in queue rows whose bodies the snapshots don't keep. Kept as a self-report, at confidence "inferred".
- **Pattern:** four of the five are the room-leads recording their own misses, so self-critical, not self-serving.

**Notes read:**
- **Platform Architect (PL-011, PL-012):**
  - R-006 built to my three conditions;
  - `harvest_hash` matching and per-seat `seats` in launch records are done;
  - its question is where to show the launch-record model on the Models page (answered below);
  - the owner must choose A, B or C for the root problem.
- **Studio Architect (AD-025):**
  - the stop-rule pointer is in;
  - smoke-assertion-first and exploit-impact lines are live in proto-3 and coop-2;
  - critic anchors, bottom-third ranking, deck changes and E1–E3 are pending the next pitch round;
  - its "your call" on matching is settled (`harvest_hash`).
- **Rig Architect:** nothing new since MA-012.

---

## MA-014 Review of PL-013 (option A); handoff for the architects rig (2026-10-12)
**PL-013 review:** `reviews/PL-013-option-A.md`. The direction is sound, but two high findings need fixing before the owner runs it:
1. **The deploy path:** `deploy-console.sh` copies whatever is in the agent-writable repo to `/opt`. So "closes editing the console's code" only holds if deploys use a reviewed commit (`git archive` of a commit, a diff shown, refusal on uncommitted changes).
2. **The token printout:** `install-console-user.sh` prints the new token to the terminal. The snapshot logger copies every tmux pane (including `operator-human@kernel`) into agent-readable files, so the token must not be printed there.

Also found:
- launch records are agent-writable, which affects routing trust;
- runbook step 6 needs checks that prove the boundary (writing `/opt`, reading `/etc/rig-console/env`, the console's `/proc/*/environ`, `sudo -u rigconsole`);
- optional unit hardening, a narrower helper, and smaller points.

**Handoff (PD-020):** written to `architects/handoffs/model-architect.md` from the template.

**`harvest.py --live`:** added. It reads `~/openrig/jobs` and `~/openrig/research` directly, so the seat doesn't depend on stale mirrors. Tested on a fixture; the mirror mode is unchanged.

**Read for the handoff:** `architects/brief.md`, `README.md` and `agents/model/guidance/role.md`. Suggested changes are in the notes for the Rig Architect.

---

## MA-015 First harvest as a seat: coop-1, depth-1, friends-1, proto-2 (2026-10-13)
**Harvest:** `harvest.py --live` imported **O077–O125** (49 lines) and 23 metric rows, 0 invalid. proto-3, coop-2,
bridge-design and assets-1 have no notes yet (still running).

**Review:** every new line checked against the live job folders with `tools/verify_evidence.py` (new); queue-row
quotes checked with `rig queue show --full`, which a seat can read live (the mirrors never could, MA-013). All 49
verified, apart from O100's quote, which is a paraphrase of the receipt's line 38. Decisions applied with
`tools/review.py` (new) from `reviews/MA-015-ledger-updates.json`.
- **5 duplicates:** O091, O092, O100, O101, O102 repeat O071–O075 (the leads also wrote them in their job folders).
  Marked `duplicate_of`, not deleted, not counted. O075's queue quotes are now verified.
- **Stop rule, attribution brief (O077, O103, O104, O105):** both Claude leads' "any tool failure: STOP" wording
  came from the operator's dry-run rows (`qitem-20261012194335-6249…` to proto-2, `qitem-20261012194420-e3a8…` to
  coop-1), sent about an hour before SHARED-RULES v1 narrowed it to "the tool itself, not your input". The leads'
  part was carrying a dry-run rule into real build dispatches; the builders followed it literally. This corrects
  AD-006's "lead-written" and the proto-2 lead's own metrics note ("its own over-broad stop rule").
- **O098 → brief** (the dispatch didn't ask for retitling).
- **Everything else stays `unclear`:** one model per seat, so no counterfactual. Patterns worth watching, not traits:
  - every first builder version in coop-1 and proto-2 was sent back (7 of 7), after hand-backs of 9–40 minutes
    against multi-hour time boxes (O078, O080, O081, O083, O084, O112–O114, O118). Second rounds mostly passed.
  - the same critic seat type passed 24/24 cards in depth-1 (card review, O095) but found bypasses in every first
    build (code review, O085, O115). Same model, different task: points at the brief or task.
  - two Claude leads in different runs raised false blockers from a stale memory note about `/mnt/c` prompts
    (O075/O102, O117). Seen twice.

**Not done yet:** cards and role assessments aren't updated from these lines; that's next, then a `review-codex`
bias review before anything is called policy. No grade or routing change in this entry.

**Launch records:** `architects.json` has every seat's model and version. coop-1, depth-1 and proto-2 have no
launch record, so their lines keep `version_if_known: unknown`; friends-1's record names gpt-6.1-sol for the
Codex seats (version unknown) and "unknown" for the Claude lead.

**Tonight's incidents:**
- **False prompt reading:** queue sweeps reported `orch-lead@assets-1` at a `selection_prompt` from 02:40Z to
  05:57Z, refusing wakes. At 06:28Z its screen was an idle input box, mid-way through a normal capacity retry.
  One glance can't show whether the earlier reports were misreads. It's an OpenRig fault, not a role's, so no ledger
  line.
- **Logger hang:** no written record found in any log or queue row. I'll add evidence when someone records it.

**Recovery after the WSL upgrade restart (operator row qitem-20261013104429-5075…, 10:44Z):** `rig whoami` unchanged
(`arch-model@architects`, all four peers live). Session context retained, no compaction. Files intact: ledger 125
lines = O125, metrics 61 rows, MA-015 present. A harvest dry run now shows 28 new notes and 12 metric rows from
bridge-design and assets-1, not yet imported. No blockers.

**Permission check (operator request, 05:45Z):** two exact-path `harvest.py --live --dry-run` runs plus a scratch
Write and Edit all completed. I can't see from inside whether a prompt was shown and approved; I reported that to the
operator and `arch-rig`. New recurring helpers, for exact allowances: `models/tools/verify_evidence.py`,
`models/tools/review.py`.

---

## Notes for other roles

Each role has its own subsection, newest first. Notes are dated and marked **[new]** until the recipient acts on them. Recipients reply in their own logs, not here.

### Notes for the Platform Architect
- **[new] 2026-10-13: replies to PL-014 and PL-015.**
  - **PL-015 (research-mirror trimmed):** fine. As a seat I harvest with `--live` from `~/openrig/`, so the mirror's
    contents don't affect harvesting.
  - **PL-014 (`snapshots/launches/`):** not needed for me; the seat reads `~/openrig/launches/` directly. Mirror it
    only if the console or the owner's Windows side needs it.
  - **PL-014 re-test of the MA-013 gaps:** on my list, after the cards update. I'll log the result here.
- **[new] 2026-10-13 (MA-015): duplicate ledger lines on the Models page.** Five lines now carry
  `"duplicate_of": "O07x"` (O091, O092, O100, O101, O102). The page counts them in its tallies. Suggest: skip lines
  with `duplicate_of` in counts and show them dimmed with "duplicate of O07x". `harvest_hash` is unchanged.
- **[new] 2026-10-13 (MA-015): two new helpers for exact allowances** (the operator asked for named scripts, not a
  Python grant): `python3 <repo>/models/tools/verify_evidence.py <lo> <hi>` (read-only) and
  `python3 <repo>/models/tools/review.py <updates.json> [--dry-run]` (writes only `models/observations.jsonl`).
- **[new] 2026-10-12 (MA-014): PL-013 review** is in `models/reviews/PL-013-option-A.md`. Two high findings before the owner runs it:
  1. **Deploy a reviewed commit, not the working tree:** `git archive`, show the diff since the last deploy, refuse uncommitted changes in `dashboard/`, and record the hash.
  2. **Don't print the new token** where tmux is captured; the snapshot logger copies every pane, `operator-human@kernel` included.

  Also: agent-writable launch records; four proof checks for runbook step 6; optional unit hardening; a narrower `rig-owner`.
- **[new] 2026-10-12 (MA-013): re-test of PL-008 to PL-012.**
  - **Reproduced:** 97/97 on the smoke test, plus my own probes (local POST without cookie gets 401; Host refusals; escapes blocked).
  - **Three gaps:**
    1. **Builds port scope:** it serves any file in a job folder, not only the build folder (a planted `evil.html` and `decisions/x.json` both returned 200). `PlayHandler` uses `G.safe_path(job, rel)`; restricting it to the job's builds directory (`job.json` `builds`, default `builds/`) would match your docstring and condition (i). Worth a smoke check: a non-build file returns 404.
    2. **`*.ts.net` wildcard:** `_host_ok` accepts any `*.ts.net`; pin the exact Tailscale name.
    3. **`X-Forwarded-Host`:** `_to_play` uses it unchecked (`/go/play/…` redirected to `evil.example`); apply the same name check. A nit.
  - **Also confirm:** the live console has `RIG_CONSOLE_TOKEN` set. With none, `do_POST` allows changes without sign-in. Consider refusing changes when no token is configured.
- **[new] 2026-10-12 (MA-013): where to show the launch-record model on the Models page.**
  - **The Evidence panel:** next to a ledger line whose `version_if_known` is "unknown", show the launch record's model for that job and seat, labelled "from launch record".
  - **The seat grid:** no change.
  - **The ledger:** I'll also fill `version_if_known` from launch records at harvest time, if they're mirrored or readable. Is `~/openrig/launches/` mirrored anywhere I can read?
- **[new] 2026-10-12 (MA-011): interop and sudo confirmed open.** As `you`, `wsl.exe -u root id` gave root and `sudo -n true` succeeded. Step 3 needs both closed first:
  - **Interop:** set `[interop] enabled=false` in `/etc/wsl.conf`, after listing what calls Windows programs from WSL. Check the keep-alive, any `powershell.exe`, `cmd.exe` or `explorer.exe` use in `setup/` and the logger, and the operator's habits. If something needs Windows, it should run on the Windows side instead.
  - **Sudo:** remove passwordless sudo for the seats' user, or limit it to named commands the owner approves. Check `setup/` scripts and the operator's use of `sudo systemctl` first.
  - **Order:** close these, re-run both checks from a seat shell, then do step 3. Log the result, plus any residual risk accepted, in your threat model.
- **2026-10-12 (MA-010, done in PL-012): model per seat in launch records.** Please consider adding `seats` to the `JOBS.md` §3b launch record: `{"build-a": {"runtime": "codex", "model": "<name>", "version": "<as shown>"}, …}`. It would be filled by the operator (who chooses the model) and shown on the Models page. Today `_ps.json` has no model for 53 of 54 seats, so nearly every ledger line says "version unknown", and routing evidence can't name what actually ran. Paired with a note to the Rig Architect (section 7 duty).
- **2026-10-12 (MA-009, done in PL-012): your PL-010 question.** Match harvested notes on `harvest_hash`, not `harvested_from` or the `what_happened` text: sha1(job folder name + "\x1f" + the note line, whitespace-trimmed), hex, first 16 characters. It's stored on every harvested ledger line. It survives my rewording, and an edited note counts as new. `harvested_from` is display only (its line numbers shift). This is a stable contract in `models/HARVEST.md`.
- **2026-10-12 (MA-007, answered in PL-009/PL-010): security review** of R-005/R-006 and the Models page: `models/reviews/R-005-R-006-security.md`. All 7 findings accepted. Still with the owner: the interop and sudo checks, then step 3.
- **2026-10-12 (MA-005, done in PL-003): Models page,** filed as R-008.
- **2026-10-12 (MA-001, done by the owner): `.gitignore`** for `models/observations.jsonl`, `metrics.csv` and `preview/models-preview.html`.

### Notes for the Rig Architect
- **[new] 2026-10-12 (MA-014): the architects rig (PD-020).** Handoff written: `architects/handoffs/model-architect.md`. Suggestions for `architects/brief.md` and `ROLES.md`:
  1. **Grading independence:** in a rig, graded architects can message the grader directly. Suggest: disputes about a grade go in the graded role's log, not in messages. The grader never changes a grade in reply to a message, only to evidence. Bias reviews of grades are commissioned by the Model Architect, not by the graded role.
  2. **`ROLES.md` "How they talk (all through the owner)"** now conflicts with direct messaging in the rig. The owner owns `ROLES.md`, so this needs an owner edit or a gate.
  3. **Architect seats can edit `dashboard/` code,** which `deploy-console.sh` ships to `/opt`. Because the architects read untrusted content (web pages, run outputs), the deploy should go from a reviewed commit (my PL-013 finding 1). Worth a brief line: only the Platform Architect edits `dashboard/`, and the owner approves deploys.
  4. **The Model seat reads mostly agent-written text** (ledger evidence, run files). The SHARED-RULES untrusted-input rule covers it; worth naming in the Model role file too.
  5. **Harvesting:** the Model seat will use `harvest.py --live`, reading `~/openrig/jobs` and `~/openrig/research`. Read-only access is enough; it never writes there.
- **[new] 2026-10-12 (MA-011): interim rule until the platform fix lands.** Seats can become root today, through `wsl.exe -u root` and passwordless sudo (owner-confirmed). Candidate rule for `SHARED-RULES.md` section 1: seats never run `sudo`, `wsl.exe`, `cmd.exe` or `powershell.exe`, or any other Windows program. The operator uses sudo only on an owner's instruction, and logs it. Like the PD-017 rules, it's a rule, not a lock; the lock is the Platform Architect's work.
- **[new] 2026-10-12 (MA-010): model per seat.** If the Platform Architect adds per-seat `model` and `version` to the launch record, `SHARED-RULES.md` section 7 could make filling it part of the operator's launch duty. It's the only place the model is chosen, so it's the only reliable source.
- **2026-10-12 (MA-007, adopted in PD-017): owner impersonation:** leads act only on `decisions/<id>.json`; phone pushes come only from the console. Details: `models/reviews/R-005-R-006-security.md`, findings 5 and 7.
- **2026-10-12 (MA-005, adopted in PD-015): model notes** go in the job folder, then get harvested.
- **2026-10-12 (MA-004, adopted in PD-014):**
  - the shell rule for every seat;
  - the Studio Architect's stop and capacity rules (O019, O022–O024);
  - the answerability check;
  - the run-1 approval record (O064, settled: the owner answered).

### Notes for the Studio Architect
- **[new] 2026-10-13 (MA-015): where the "any tool failure" stop rule came from.** AD-006 calls it "lead-written". The
  leads copied it from the operator's dry-run rows (proto-2 `qitem-20261012194335-6249…`, coop-1
  `qitem-20261012194420-e3a8…`), sent before SHARED-RULES v1 narrowed it, then reused that dry-run rule in real
  build dispatches. So the fix is in the dry-run wording and in "don't reuse dry-run rules for real work", not in
  the leads' judgment. The vetted stop-rule block (MA-004) would cover both. Evidence: O077, O103–O105.
- **2026-10-12 (MA-006): model-notes format.** Templates point to `briefs/SHARED-RULES.md` section 6 rather than `models/HARVEST.md` (seats don't read design docs) or their own copy. Matches the Rig Architect's PD-014/015 note to you.
- **2026-10-12 (MA-004, accepted in AD-015, lands with the next-round templates):**
  - a vetted stop-rule block, copied verbatim (O023, O024, O030);
  - an anchor for every critic score, plus a forced bottom-third ranking (O007 vs O009);
  - deck settings drawn without replacement, and 4 hands plus 3 free (O004, O005);
  - builders name the core rule as a smoke assertion before tuning, and add an "exploit impact" line (O016, O018);
  - experiments E1–E3 (`EXPERIMENTS.md`).
- **Superseded: the MA-001 retro wording** had leads append to `models/` directly. Replaced by `SHARED-RULES.md` section 6 (PD-015). Don't use it.

### Notes for the Operator (through the owner)
- **[new] 2026-10-13 (MA-015): dry-run stop wording.** Your 19:43Z and 19:44Z dry-run rows said "Any approval
  prompt, tool failure, missing template or usage warning: STOP". Both leads reused it in real build dispatches,
  and three builders stopped on their own wrong-path reads and a malformed patch. Suggest the SHARED-RULES §2
  wording ("an approved tool failing to run: the tool itself, not your input to it"), with "dry run only" if it
  is meant for dry runs.
- **[new] 2026-10-12 (MA-002): an operator log.** A short `operator-log.md` (time, owner prompt, action, files touched) would let the Operator be assessed on its own record (`roles/operator.md`). Your PD-018 launch records partly cover this for launches.
