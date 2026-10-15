# Handoff: current state (2026-10-12, after MA-004)

For the other architects and future reviewers. All files are in `models/` at the repo root. ROLES.md lists the folder as the Model Architect's.

## The role
The Model Architect (ROLES.md) grades models, seat roles and briefs, plus the Rig, Studio and Platform Architects and the Operator. It edits nothing it grades. Its input goes under "Notes for …" in `LOG.md`; each owning role replies in its own log. A Codex reviewer checks its drafts for bias.

## What changed in this round
1. **Codex review done** (`REVIEW-codex.md`). All findings were accepted; the point-by-point response is `LOG.md` MA-004.
2. **No "model trait" claims for either family.** Every ledger line that said `attribution: model` is now `unclear` (or `provider`). Summaries say "observed across these assignments".
3. **Letter grades removed.** Role assessments are qualitative, with a confidence level (`roles/`).
4. **Corrections:**
   - **O065** is now the lead's roster claim, which the Operator's verification corrected.
   - **O025:** 2 of the 3 builder stops came after some further work.
   - **O040** is split: the required searches were useful (O040); the optional ones changed no verdict (O068).
   - **O011** is split; the scout's theme queries are now O069, an execution miss.
   - **Metrics** now count the Claude approval events and have defined columns.
   - **Platform Architect** is now credited with PL-001 and PL-002.
5. **Routing:** every row reads "incumbent assignment; comparative advantage untested". The experiments now require repeated cases and exact model versions.

## Where the starting hypotheses stand
| Seed | Now |
|---|---|
| Codex builders stop literally | The stops followed broad "any tool failure" wording (3 caller errors became stops, 2 after some further work). 0 stops under narrower wording. Not a proven model trait. |
| "No usage warning" self-report | Disputed and excluded. |
| Critic lenient vs decisive | A plausible anchor effect across different cards and criteria. Not a model finding. |
| Claude curator bias and overrides | The bias check was volunteered and can't be measured. The x-18 change was consistent with the brief's anchor; the other cuts were unlabelled judgment. |
| Capacity cluster | Provider event; addressed by AD-010. |
| Free pitches beat dealt hands | Descriptive, for both families (Codex 13/16 vs 6/40). Points to revisiting the deck. |

## Open items for the owner
- **Models page:** send the request to the Platform Architect (`LOG.md`, "Notes for the Platform Architect").
- **Notes to the Rig and Studio Architects:** point each at its section in `LOG.md`.
- **`.gitignore` lines:** for the ledger, metrics and preview (Platform Architect).
- **E1–E3:** the owning architects decide whether to run them.
