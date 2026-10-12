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

## Notes for the Studio Architect (input, not edits)
- **Stop rules:** a vetted block in every template; leads copy it verbatim (O023, O024, O030).
- **Critic anchors:** give every score its own anchor (e.g. "8 situations = Depth 3"); forced bottom-third ranking (O007 vs O009).
- **Deck:** draw settings without replacement; 4 hands plus 3 free (O004, O005).
- **Builders:** name the core rule as a smoke assertion before tuning; add an "exploit impact" line for tuning changes (O016, O018).
- **Retro wording** for every template's outputs list (pitch-room, depth-room and friend-room after `retro.md`; proto-sprint, coop-proto and design-team as a new bullet):
  > - **Model notes (end of run, lead only):** append one line per notable seat behaviour to `/mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/models/observations.jsonl` (format in `models/README.md`) and one row per seat to `metrics.csv` there. Name the brief or dispatch file the seat was working from, and say whether that brief asked for the behaviour. Only what you saw happen, each with a file path or quote. Write "seen once" when it was. Don't judge which model is better; the Model Architect does that.
- **Experiments:** E1 to E3 in `EXPERIMENTS.md` for the next round.

## Notes for the Rig Architect (input, not edits)
- **New cross-team rule:** "Every seat, any model: no `$`, backticks or pipes in shell text; free text by `--body-file`." The Claude seats lacked it, and 4 approval events followed, with mixed causes (O039, O045, O048).
- **The Studio Architect's proposed stop and capacity rules (its AD-014 notes):** the ledger supports them. Under "any tool failure", 3 caller errors became stops (O023, O024); under the narrower proto-1 wording, there were 0 (O022). The capacity blips cleared on their own (O019).
- **Answerability check in the research template:** "Can public evidence answer this?" (PD-003, PD-004).
- **Record conflict:** who approved the run-1 prompts. The run-1 retro says the operator; PD-012 says the owner. Please settle it in your log (O064).

## Notes for the Platform Architect (input, not edits)
Proposed request for `dashboard/REQUESTS.md` (the owner adds it or OKs me adding it):
> ### R-nnn Models page
> A new `models.html` and nav entry, plus a read-only `/api/models` route that reads `models/` (cards, roles, summaries, observations.jsonl, metrics.csv). The page and route code are in `models/PROPOSALS.md`. It needs one read-only route (static files are served only from `dashboard/`), plus smoke checks as in PL-002; there's a working preview with real data in `models/preview/models-preview.html`. Evidence links use the existing sandboxed `/job/` route.
- **Record the model per seat:** in `_ps.json` / snapshots, which is `null` for 53 of 54 seats today. Without it, every ledger line says "version unknown".
- **`.gitignore`:** `models/observations.jsonl`, `metrics.csv`, `preview/models-preview.html` (they quote private run outputs).

## Notes for the Operator (via the owner)
- **A short operator log** (time, owner prompt, action, files touched) would let the Operator be graded on its own record (`roles/operator.md`).
