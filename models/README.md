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
| `HANDOFF.md` | What changed, for the Codex reviewer and the other architects |
| `claude.md`, `codex.md`, `gemma4-12b.md` | Traits that hold across roles and briefs only |
| `ROUTING.md` | Recommended model per studio role, plus the compensating rules |
| `EXPERIMENTS.md` | Head-to-head proposals (not run) |
| `REVIEW-REQUEST.md` | What the Codex reviewer was asked to check |
| `REVIEW-codex.md` | The Codex review (2026-10-12); answered in `LOG.md` MA-004 |
| `PROPOSALS.md` | Dashboard page code, retro wording, gitignore (not applied) |
| `preview/` | `models.html` (the proposed page) and `models-preview.html` (with data inlined) |

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
- **All evidence is from 2026-10-11 to 12,** so nothing is stale yet. From about 2026-12-11, mark older lines weak unless repeated.
- **Model versions are mostly unknown.** Only 3 Claude screens show "Opus 5.5", and only one Codex seat (`gpt-6-astra`, starter rig) has a recorded model. Recording `model` in `_ps.json` or `rig.yaml` would fix this.
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
