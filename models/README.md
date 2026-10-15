# models: Model Architect files

Owner of this folder: the Model Architect (ROLES.md; AD-012). Status: **revised after the Codex review** (`REVIEW-codex.md`; response in `LOG.md` MA-004). Still draft for routing policy.

| File | What it is |
|---|---|
| `observations.jsonl` | Evidence ledger, one line per observation |
| `metrics.csv` | One row per seat per run |
| `cards/<model>--<role>.md` | Report cards per model and seat role (only pairs we have actually run) |
| `roles/*.md` | Assessments of the Rig, Studio and Platform Architects and the Operator (ROLES.md) |
| `BRIEFS.md` | Briefs graded by their observed effect |
| `LOG.md` | This role's own log (MA-nnn) and its notes to the other roles |
| `HARVEST.md` | Format leads use for end-of-run model notes in their job folder, and how they're harvested |
| `tools/harvest.py` | Imports those notes into the ledger and metrics (safe to re-run) |
| `tools/verify_evidence.py` | Checks harvested lines' evidence against the live job folders (read-only) |
| `tools/probe_console.py` | Security probe: starts a throwaway console on a copy of the smoke fixtures (never the live one) |
| `tools/review.py` | Applies review decisions from a JSON file to ledger lines (`reviews/MA-0nn-ledger-updates.json`) |
| `claude.md`, `codex.md`, `gemma4-12b.md` | What was observed across roles and briefs, per model (shown on the Models page) |
| `ROUTING.md` | Recommended model per studio role, plus the compensating rules |
| `EXPERIMENTS.md` | Head-to-head proposals. E2 is approved (owner, 2026-10-14); Studio runs it after Bridge |
| `REVIEW-codex.md` | The first Codex review (2026-10-12); answered in `LOG.md` MA-004 |
| `reviews/` | Reviews for other roles, ledger review decisions (`MA-0nn-ledger-updates.json`), and the MA-028 self-assessment |
| `archive/` | Superseded files: the 10-12 handoff, the applied proposals, the first review request (MA-029) |
| `preview/` | Gitignored original page proposal with real data inlined; superseded by `dashboard/models.html` (PL-003) |
| Current handoff | `architects/handoffs/model-architect.md` |

## Ledger line format
```
{"id":"O058","date":"YYYY-MM-DD","model":"claude|codex|...","version_if_known":"...|unknown",
 "runtime":"claude-code|codex|ollama","seat":"build-a","role":"builder","rig":"proto-3",
 "brief":"path of the brief or dispatch in force","brief_date":"YYYY-MM-DD",
 "brief_asked":"yes|no|partly|unclear|n/a","attribution":"model|brief|harness|provider|unclear",
 "what_happened":"behaviour, not motive","evidence":"file path + quote",
 "kind":"strength|failure|quirk|cost|reliability","confidence":"observed|inferred","n":1,
 "status":"optional, e.g. addressed: AD-010"}
```
- **One observation per line.** Repeats go in `n`; don't duplicate the line.
- **When to use `attribution: model`:** only when a different brief would plausibly **not** have changed the behaviour. Unrequested behaviour isn't automatically model-caused. Otherwise use `unclear`. Summaries say "observed across these assignments", not "trait" (MA-004).
- **`revised: MA-004`:** marks lines corrected after the Codex review.

## Notes
- **Evidence runs from 2026-10-11 to 14,** so nothing is stale yet. From about 2026-12-11, mark older lines weak unless repeated.
- **Model versions:** 96 of 197 non-duplicate lines name one (MA-029). Launch records (`~/openrig/launches/<job>.json`, `seats`) give `gpt-6.1-sol` for Codex and the alias `opus` for Claude, with no version. Copy them at harvest and say where they came from.
- **Metrics `model` is `claude` or `codex` only** (normalised MA-029). Any fuller label as recorded is kept at the start of `notes`. Rows the harvester duplicates from seats' own folders are marked in `disputed_or_excluded`, not deleted.
- **`active_min` is left blank on purpose.** The OpenRig activity signal is unreliable (ARCHITECTURE-LOG.md PD-007).

## Metrics columns
- **`send_backs`:** send-backs this seat received.
- **`stops_real`:** halts on this seat for approval prompts, usage or provider limits (events; `unknown` if not reconstructable).
- **`stops_spurious`:** halts the lead later ruled weren't needed.
- **`self_report_mismatches`:** the seat's report about its **own** execution, contradicted by other evidence. Undisputed cases only; sourcing errors go in notes.
- **`capacity_errors`:** provider capacity messages.
- **`disputed_or_excluded`:** anything counted elsewhere or left out, with its ledger id.

## Role assessments (`roles/`)
- **Format:** qualitative, with a confidence level. No letter grades until there's a rubric with severity weighting and a minimum evidence threshold (MA-004, from the Codex review).
- **Pending:** "pending" means outcomes aren't in yet.
- **Replies:** owning roles reply in their own logs.
