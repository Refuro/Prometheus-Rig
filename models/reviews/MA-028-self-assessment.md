# Model Architect: assessment of its own area (`models/`)

**Asked by:** the owner through the operator (qitem-20261014190707-1e7a67c65c617082; owner message
m-20261014120645-5e2b), 2026-10-14. **Written by:** the Model Architect, about its own work, so it isn't
independent. A `review-codex` pass would be the check if the owner wants one.
**Scope:** assessment only. Nothing below has been changed.
**Read:**
- `models/` (all files);
- `dashboard/models.py`, which shows `models/` on the Models page;
- my handoff;
- a dry-run harvest (`harvest.py --live --dry-run`);
- ledger counts from a scratch script.

## Status of the numbers
- **Ledger:** 206 lines, 188 after duplicates are removed.
- **Metrics:** 83 rows.
- **Dates:** evidence covers 10-11 to 10-13.
- **Labels:** "Verified" means I checked it at its source today. "Hypothesis" means I didn't.

## What is working
1. **Briefs, not models, explain most failures, and the teams acted on that.** (Verified)
   - Three findings traced to wording, not models:
     - the "any tool failure: STOP" wording traced back to the operator's dry-run rows (MA-015);
     - over-broad stops became SHARED-RULES v1.9 §2 (MA-019, acted on by Rig);
     - O058 and AD-030 were identified as the same shared-`CLAUDE.md` bug (MA-017).
   - This is the role's main payoff so far: a cause found, and a rule changed.
2. **Independent reviews found real defects before they shipped.** (Verified in the review files)
   - R-005/006 (PL-009–011);
   - the re-test gaps (MA-013);
   - two high findings in option A (MA-014);
   - the PL-014 re-test that found the `builds:"decisions"` hole (MA-020, fixed by PL-031);
   - option A round 2;
   - the platform-dev sandbox (MA-027): the network is on and writes reach the shared workspace. The role was
     corrected before launch.
3. **The ledger is honest about what it can't say.** (Verified)
   - No line claims `attribution: model`: 145 are `unclear`, 38 `brief`, 3 `provider` and 2 `harness`.
   - 18 duplicates are marked, not deleted.
   - Evidence is checked against the job folders (`verify_evidence.py`).
   - Codex bias reviews caught real overclaims (MA-004, MA-023, MA-025).
4. **The harvest pipeline runs without manual copying.** (Verified)
   - Leads write notes in their own folders.
   - `harvest.py` imports them, and re-running it is safe.
   - The Models page shows notes that haven't been harvested yet.
5. **Model versions are recorded far more often.** (Verified) 88 of 188 lines now name a version, up from nearly
   none on 10-12.

## What isn't working, or is uncertain
1. **No routing question has been answered.** (Verified)
   - Every routing row is still "incumbent; comparative advantage untested".
   - None of E1–E3 has run. Studio accepted E2/E3 for "the next pitch round", but no pitch round has run since.
   - So the role's stated purpose, choosing models per role on evidence, has produced no decision. Its value so
     far comes from brief and security findings.
2. **What the owner sees on the Models page is partly stale.** (Verified)
   - **`claude.md`:** still lists "writes rules for other seats that were broader than intended (2 leads)" (O030).
     MA-015 traced that wording to the operator's dry-run rows, so as worded it's now wrong. The page shows this
     file as Claude's summary.
   - **`codex.md`:** frozen at 10-12 (12 runs). It doesn't reflect the reviews, design seats or Diplomacy.
   - **`BRIEFS.md`:** last updated 10-12. It has no rows for v1.9 stop rules, design-team, production or the
     Diplomacy lab.
   - **`ROUTING.md`:** says 154 lines, not 188. The player-eyes row says "no evidence yet", but the dry run
     below has a player-eyes note.
   - **`README.md`:** says all evidence is from 10-11 to 12, and that model versions are mostly unknown. Both
     are out of date.
3. **9 notes from bridge-prod aren't harvested.** (Verified, dry run)
   - They're O207–O215: 4 tech-lead failures, 1 team failure, strengths for dev-a and the playtest bot, a
     review-code permission stop and a player-eyes quirk.
   - The Models page shows them as "not yet reviewed".
   - Harvesting is existing, authorised work. I didn't run it here because this task is assessment only.
4. **The evidence depends on leads writing notes, and some don't.** (Verified)
   - proto-3 and coop-2 ended with no `model-notes.jsonl`.
   - Nothing reminds a lead, and I only harvest when asked.
   - So gaps stay invisible until someone looks.
5. **The ledger is lopsided.** (Verified)
   - 46 of 188 lines (24%) come from one Diplomacy game.
   - 77% are attribution `unclear`.
   - Most roles have one run under one model.
   - Count-based summaries mostly describe single runs, and the cards say so ("seen once"). But the totals on
     the page can still read as more general than they are.
6. **Metrics model labels aren't normalised.** (Verified, small)
   - `metrics.csv` uses 12 different `model` strings.
   - The page buckets them by first word, so 2 rows land in their own buckets (`claude-opus-5-5`, `gpt-6`), and
     8 rows say "unknown".
7. **Old files clutter the folder.** (Verified)
   - `HANDOFF.md`, `PROPOSALS.md` (A and C were applied: PL-003 and `.gitignore`), `REVIEW-REQUEST.md` and
     `preview/` all date from 10-12.
   - `README.md` still lists them as current.
   - My handoff's open-items table also lags: no MA-027 or platform-dev probes, and stale MA-013/016 rows.
8. **Scope drift.** (Hypothesis about balance; the counts are verified)
   - 8 of 27 log entries are security reviews or probes for other roles, mostly Platform: MA-007, 013, 014, 016,
     018, 020, 021 and 027.
   - They found real issues (see above).
   - But they're a second job, and they compete with keeping the grading files current (item 2).
   - Whether that trade is right is the owner's call.
9. **Role assessments have no rubric yet.** (Verified)
   - `roles/*.md` are qualitative by design (MA-004). That's honest, but you can't compare roles over time.
   - Their last update was 10-13. Unknown: whether the other architects read them or act on them; I have no
     replies on record.

## Recommended changes, in priority order
**Already authorised (my normal upkeep; no new permission needed). I'd do these next unless the owner says no:**
1. **Harvest bridge-prod** (O207–O215), verify it, and review each line.
   - **Benefit:** the Models page stops showing 9 unreviewed notes, and player-eyes gets its first evidence.
2. **Refresh what the page shows:**
   - `claude.md` and `codex.md`: fix the O030 wording; add the design and Diplomacy coverage;
   - `BRIEFS.md`: add v1.9, design-team, production and Diplomacy;
   - `ROUTING.md`: counts and the player-eyes row;
   - `README.md`: dates and versions;
   - my handoff.
   - A Codex bias review follows, as for any grade.
   - **Benefit:** what the owner reads matches the evidence.

**New proposals (need the owner's OK; I won't act on them under this task):**

3. **Run one real comparison: E2 (two critics re-judge depth-1's 24 blind cards).** It needs no new pitch round.
   - **Cost:** about 2 critic sessions of 20 minutes.
   - **Benefit:** the first routing evidence that isn't incumbent-only.
   - Studio owns the run, and the owner approves the budget.
   - Without one comparison, the routing table won't change, so this is the most important new proposal.
4. **Make missing notes visible.**
   - **Option 1:** Rig adds "write `model-notes.jsonl` before closing" to the end-of-run checklist.
   - **Option 2:** Platform shows "no model notes" on finished jobs.
   - That's a change to another role's files, so it's a request to them.
   - **Benefit:** gaps like proto-3 and coop-2 show up at the time, not later.
5. **Archive the old files** (`HANDOFF.md`, `PROPOSALS.md`, `REVIEW-REQUEST.md`, `preview/`) into
   `models/archive/`.
   - It's a move, not a delete, and the owner commits.
   - **Benefit:** a newcomer reads only what's current. Low priority.
6. **Normalise metrics model labels** as `model` plus `version_if_known`, matching the ledger.
   - **Benefit:** clean buckets on the page. Low priority.
7. **Decide the review share (owner's choice).**
   - **Option A:** reviews stay with me, and grading upkeep is scheduled after each harvest.
   - **Option B:** security reviews move mainly to `review-codex`, and I keep the model and brief work.
   - I'd keep the status quo (A), with upkeep made explicit, because the reviews have been the role's most
     concrete output. I'm flagging it, not pushing it.

**Not recommended:**
- **Any routing change.** There's no comparative evidence (see the first item under what isn't working).
- **Letter grades.** There's still no rubric or minimum sample.
