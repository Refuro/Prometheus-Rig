# Codex review of the Model Architect drafts

Reviewed 2026-10-12, as the Codex reviewer named by the owner. **Verdict: revise before using these drafts as routing policy or publishing the letter grades.** The observations are useful, and several important caveats are already honest. The main weaknesses are causal attribution, selective summaries of evidence, and inconsistencies between the prose and machine-readable metrics. The evidence does not establish that Claude is better in judgment seats or that Codex has a general literalness trait.

This review covers all 67 ledger entries, the 38-row metrics file, the model/role cards, routing, BRIEFS.md, and the four role grades. I checked the requested claims against mirrored dispatches, briefs, reviews, retros, decisions and architect logs; independently recounted the requested numbers; and checked a reproducible random sample of five ledger entries. Sources below are repository-relative paths, with section names where helpful. I did not inspect the live rig or contact any seats. Only this review file was edited. Recommendations below are proposed corrections, not edits to the drafts.

**Findings that should be corrected first**

1. **O065 records an Operator failure that the verification receipt explicitly corrects.** The initial `jobs-mirror/proto-1/lead-dry-run-receipt.md`, “Roster note,” says only build-a was present. But `jobs-mirror/proto-1/lead-operator-dry-run-verification.md`, paragraph 2, says all four seats were ready and explicitly calls the lead's roster claim incorrect. That second document is already cited for O059. Replace the asserted roster gap with a disputed initial report, subsequently corrected by verification; do not debit the Operator for it. This is evidence against the lead's roster assessment, with underlying cause still unknown. It also disproves the claim that the Operator evidence consists entirely of other seats' retros: the mirror includes documents reporting operator verification, although authorship and the original owner prompts are not independently authenticated.

2. **O025's “3 of 3 … no retry performed” does not match two of its three sources.** `jobs-mirror/proto-2/protos/x-12/build-c-stop-report.md` records two failed skill-path reads, a successful third read, and further orientation/scaffolding before stopping. It explicitly admits continuing contrary to the stop rule. `jobs-mirror/proto-2/protos/x-14/build-b-stop.md` records reading the correct file after the failed read. Only `jobs-mirror/coop-1/protos/dry-run/build-a-stop.md` says no implementation or retry occurred after failure. Keep the credit for precise, candid reports, but remove the universal no-retry claim from O025 and the builder card. Revise the “literalness: high” and “follows the letter” summaries: the three escalations followed a broad rule, but adherence was not uniformly immediate. This correction counts against an overgenerous Codex summary.

3. **O040 conflates required screen-stage work with optional deep-dive work.** `briefs/research-brief-run-2.md`, section 6, explicitly requires analyst overturn searches after the screen. `research-mirror/run-2/retro.md`, “Deep-dive send-backs,” says the extra searches after the two deep-dive challenges **neither flipped its verdict**. The B05 residual revival and initial A07 Upwork finding appear in the earlier screen-stage table in `research-mirror/run-2/lead-verdicts.md`; the deep-dive A07 account says the job was re-opened. Split O040: required screen-stage searches yielded useful evidence (`brief_asked: yes`); the lead also requested two additional deep-dive searches, which refined evidence without changing verdicts (`brief_asked: no`, attribution unclear). The research-lead card currently says the lead “ran” the searches, whereas the retro says it requested analyst searches. Preserve that distinction. Remove the claimed causal link between going beyond the brief and these particular gains from `claude.md`, ROUTING.md and the brief/architect summaries.

4. **The stop metrics omit documented Claude incidents and misuse a self-report field.** `models/metrics.csv` gives `stops_real=0` to run-2 lead, run-2 skeptic and validation-1 skeptic, despite their notes and source reports describing two, one and one approval stops respectively. Run-1 lead's usage-limit closure and the run-1 analysts' approval waits are also absent from the stop counts. The run-1 skeptic's unsupported ZenMaid citation is entered as `self_report_mismatches=1`, although it is a sourcing error, not a report about its own execution. Conversely, proto-1 build-a's disputed warning self-report is numerically counted while the prose says it is excluded. Define the columns, distinguish events from affected seats, use unknown where counts cannot be reconstructed, and represent excluded/disputed observations separately. Otherwise a dashboard could reward Claude on stops and penalize Codex on a disputed self-report even while displaying cautious prose. Keep `active_min` blank: PD-007 supports that choice.

5. **O039 and O048 turn possible prompt triggers into established causes.** The run-2 retro calls the first claim prompt's attribution unconfirmed, while also reporting a forbidden pipeline. Its later aggregate statement that every prompt came from shell shape does not resolve that specific uncertainty. `research-mirror/validation-1/plan/lead-approval-prompt-report.md` calls the compound command/dollar expansion a “Likely trigger.” Report four observed approval events across those seats, with mixed certainty about cause; do not report four proven shell-shape causes. The pipeline is still a documented execution mistake. A missing later dollar-sign rule is not a blanket explanation for that already-forbidden pipeline.

6. **O067 and the Platform card are stale; O066 overstates the handover.** `dashboard/ARCHITECTURE-LOG.md` now contains PL-001 and PL-002, not just a header. PL-001 reports a green 45-check baseline and identifies unresolved gate/build trust and alert-test risks; PL-002 records diagrams and rendering checks. Keep the Platform grade pending because implementation outcomes are not yet available, but credit the recorded assessment and documentation. This is a snapshot update, not evidence the original author deliberately omitted later work. PL-001 also identifies a hard-coded briefs path, confirmed in `dashboard/serve.py:690`, contradicting O066's “every data path overridable.” Narrow that handover claim and record the exception. Treat PL-001's inherited risks as new evidence to assess, not as failures introduced by the incoming Platform Architect.

**Requested bias checks and attribution spot-checks**

**O003 / Claude pitcher:** the 4/7 board and 3/7 owner-pick counts are correct, as are Codex's 6/14 and 3/14. `jobs-mirror/pitch-1/board.md`, “Favouritism check,” explicitly acknowledges possible prose-driven scoring and a cap on Claude cards. The existing caveat is appropriately weak. Change `kind: strength` to a neutral outcome/quirk, however, so an aggregation cannot count it as demonstrated model superiority. Also mention the per-pitcher quota and different dealt hands. Owner selections were made from the curated board and therefore are not an independent blind comparison of all 21 cards.

**O016 / Codex builder:** four of six toys were sent back; all three builders were involved. That count is supported by all six `jobs-mirror/proto-1/reviews/lead-*.md` files and the four send-back files. The failures should be distinguished:

| Toy | Supported reason for send-back |
|---|---|
| b-06 | Contact patch orientation/width did not match the rule. |
| c-07 | Turf/features did not flip as required. |
| a-06 | Continuous head drift and shrinking event gaps were missing; review also flagged refresh cost. |
| a-01 | Implemented LIFO, sway and orders, but tuning allowed single-item shuttling to bypass the prototype question. |

“Safer neighbour” is the template/lead's assessment, not an established builder intention. The a-01 review explicitly praises the implemented rules; its spec does not prescribe the timer value or require paired carrying. Its wave-2 dispatch does warn against tuning that bypasses the rule, so the send-back is justified. Prefer “four send-backs for spec or prototype-question fidelity, including three missing/changed mechanics and one tuning bypass” to “four simplified rules.” Keep attribution unclear. The b-06 second-round jump exploit is separately documented by the builder's handback and should remain a concrete builder mistake, alongside the template's acceptance cap.

**O023 / O024:** attribution of the escalation to the stop wording is well supported. Both proto-2 resume files say the stop was correct by the letter of the rule. The coop dry-run dispatch actually says “ANY … tool failure”; its resume ruling distinguishes caller-input mistakes. This does not excuse the wrong-path reads or malformed patch. Split the caller error from the decision to stop, and retain the delayed-stop facts in finding 2. The original proto-2 common dispatch was edited, so label its historical wording as reconstructed from reports and resume messages.

**O027, O028, O032, O040, O047 / Claude strengths:** O027 and O028 honestly use `brief_asked: yes`: proto-1 brief section 5 explicitly asks for code review, an independent build rerun and a couldn't-judge statement. O047's page reopening is required by `briefs/validation-brief-1.md:48`, the evidence-review step; retain the positive execution result, not a claim of unique model skill. Its new buyer-location finding is useful, but the underlying job remains an indexed-copy observation, not verified settled payment. O032 is only partly prompted: the per-pitcher quota constrains selection, while the explicit family-bias reflection is volunteered. That is one observed self-audit, not proof that the bias was corrected or that Claude is the best curator. O040 needs the stage split above.

**O042 / money-1 lead:** remove “dense, long-sentence text” from the ledger and the harder-to-skim-than-Claude criticism from the card. There is no shared readability rubric, matched retro template, or reader outcome. O042 itself is marked `observed`, despite the card calling that criticism inferred. The clean dry run, preserved decision provenance, unpadded funnel and corrected placeholder-ID error are supported by `research-mirror/money-1/retro.md`. They are sufficient to describe the run.

**An additional Codex brief-attribution error:** O011 groups the capped search process with poor query choice under `brief_asked: yes, attribution: brief`. But `jobs-mirror/pitch-1/lead-dispatch-scout.md` explicitly says to judge the core verb and win condition, not the theme. Split the compliant search budget from the three noisy theme queries. The latter is an execution-quality miss reported by the lead; it is not a request the brief made. O007/O009 likewise support a plausible anchor effect, not proof that the brief caused all calibration differences. Depth's role file already contained a low Exploit-proof anchor; neither a universal pass nor a universal cut rate establishes correctness without an independent standard.

**Audit of every `attribution: model` entry**

There are 18 such entries. The request's counterfactual test is stricter than README.md's “brief did not ask” rule: unrequested behaviour is not necessarily model-caused. I recommend the following changes while retaining who acted and the observed successes/errors. Role accountability does not require a claim about model-family causation.

| ID | Proposed attribution / reason |
|---|---|
| O002 | Unclear. Length differs, but hands/seeds and one dry-run reminder differ; a tighter word target could change it. |
| O018 | Unclear. Builder introduced/disclosed the exploit; tuning constraints, review cap and time box confound a model trait. |
| O030 | Unclear. Leads authored the overbroad rule; a supplied stop block plausibly prevents it. Hold the lead accountable without inferring a family trait. |
| O032 | Unclear. One volunteered self-audit under an author-visible quota; blind procedure would change the behaviour. |
| O034 | Unclear. One factual counting error, with no evidence separating model, procedure and transcription; an explicit recount could prevent it. Keep the error. |
| O038 | Provider/account limit, with budget-policy contribution unknown. Hitting a session limit is not evidence of a reasoning defect or inefficient model without usage data. |
| O039 | Unclear; split events and preserve the first trigger's uncertainty. Prompt handling also depends on shell/runtime permissions. |
| O040 | Split required screen searches (brief) from optional deep-dive requests (unclear); correct the claimed outcomes. |
| O043 | Unclear. Unsupported citation remains a skeptic error; verification instructions plausibly change it and later evidence supports that possibility. |
| O044 | Unclear. A skeptic assigned to seek incumbents got a second pass over analysts' work; role, sequencing and model are confounded. `brief_asked` should be yes for the incumbent-search responsibility. |
| O045 | Unclear. Compound command plus external-path access and permission setup; no controlled model comparison. |
| O048 | Unclear. Likely shell trigger, not established cause; explicit command-shape guidance could change it. |
| O049 | Unclear. One corroboration follow-up in an evidence-gathering role; a more explicit evidence checklist could elicit it from another seat. |
| O053 | Unclear at model level. These are Studio Architect decisions under a particular charter/history; retain them in that role's accountability record. |
| O054 | Unclear at model level. Same for Rig supervision/design errors. Also preserve the approval-actor dispute instead of asserting PD-012's account as resolved. |
| O056 | Unclear. Synthetic outputs are prompt-dependent; speed also depends on runtime/hardware. No spending prohibition was violated by proposing an ad test. |
| O057 | Unclear. Same synthetic/runtime limits; `example: string` did not explicitly require one verbatim review. The skeptic task has no recorded pass grade. |
| O066 | Unclear at model level. Handover work is a role outcome, and the universal path-override claim is contradicted by PL-001 and code. |

This removes causal model labels symmetrically from praise and criticism, including both Codex-labelled cases. It does not erase failures. Cross-role repetition under similarly prescriptive briefs supports “observed across these assignments,” not an inherent model trait. The model summary pages should use that narrower framing.

**Counts and five random evidence checks**

The sample was selected without choosing convenient entries: Python `random.Random(20261012).sample(entries, 5)` over the ledger in file order returned **O053, O002, O007, O001, O006**. All named sources exist and support the quoted text or attributed log statements:

| Entry | Source checked | Result |
|---|---|---|
| O053 | `studio/ARCHITECTURE-LOG.md`, AD-002/003/005 | Supports the stated late-game, stop/retry, deck and rubric omissions as architect-reported outcomes; model causation remains unproven. |
| O002 | `jobs-mirror/pitch-1/lead-log.md` and pitch files | “7/7 valid, 212 to 241 words” is present; independently reproduced. The dispatch-identity claim needs qualification. |
| O007 | `jobs-mirror/depth-1/depth/summary.md` and brief | The quoted all-24-pass statement is present; 16 Depth-5 scores confirmed. |
| O001 | `jobs-mirror/pitch-1/lead-log.md` and retro problem 2 | Both quoted Codex length ranges and the comma-label workaround are present. |
| O006 | `jobs-mirror/friends-1/retro.md` | The “4 of the 6 gate failures were voice-driven” quotation and 21 first-check-valid cards are present. The deck explanation is posed as a question in the source. |

Board and decision recount, using pitch-1 IDs, depth-1's Reveal mapping and friends-1's Reveal table:

| Room | Free selected / entered | Hand selected / entered | Revised selected / entered |
|---|---:|---:|---:|
| pitch-1 | 6/6 | 4/15 | — |
| depth-1 | 5/6 | 2/15 | 1/3 |
| friends-1 | 4/6 | 2/15 | — |
| Total | **15/18** | **8/45** | **1/3** |

O004 is arithmetically correct. The depth board has eight cards because it also includes a returning card. These are descriptive board-selection rates, not a randomized causal test of deck quality. Claude alone is 2/2 free versus 2/5 hand; Codex alone is **13/16 versus 6/40**. `cards/codex--pitcher.md` currently presents the mixed-family 15/18 and 8/45 as its “Did badly” numbers; label them mixed or use the Codex-only counts.

O007/O034: the critic summary has **16** Depth-5 and eight Depth-4 cards. The retro and Studio AD-005 incorrectly say 15. The Rig Architect log does **not** repeat that figure; remove the Rig card's claim that both logs repeat it.

O002 word counts independently reproduced with the checker's definition: whitespace words in the body after YAML front matter. Claude a: **212–241**, mean **227.57**; Codex b: **167–201**, mean **186.86**; Codex c: **166–196**, mean **184.43**. Claude's mean is about **22.6%** higher than pooled Codex, so “about 20% longer” is reasonable. Whole-file ranges are a **243–280**, b **193–238**, c **194–246**, matching O002's pooled ranges. The dispatches have a minor extra fixture reminder for b as well as different hands/seeds; call them substantially matched instructions, not identical inputs or a clean control.

The “35/35 first check” claim is too broad. Friends-1 explicitly records 21/21 first-check passes; pitch-1 records 14/14 valid at lead handback, after pitch-b worked around a checker failure. Use “35/35 valid at handback; 21/21 explicitly first-check valid.” Preserve the checker defect as harness evidence, not a model failure. ROUTING.md's basis says 57 observations but there are 67. The builder card says nine seat-runs; metrics contains seven builder seat-run rows (three proto-1, three proto-2, one coop-1). Reconcile the unit/coverage before presenting totals.

**Architect, Operator and brief grades**

The letter-grade rubric in README.md defines broad A–D categories but no plus/minus criteria, weighting by severity, or minimum evidence threshold. B−/B/B+ therefore look more precise and comparable than the evidence permits. I would publish provisional qualitative assessments and confidence until those rules are defined. I cannot infer the author's motives or prove family bias; the omissions and asymmetries below are observable.

**Rig Architect:** its “Did badly” summary is materially incomplete. Add PD-003's unreachable desk-research bar; PD-009's stale external-decision gate and max mismatch; PD-010's notification-cookie failure; and PD-012's unsupported generalization, initial broad-bind advice, publication hygiene failure and mistaken approval-actor assumption. The last is disputed in O064 and should remain so in O054. Do not reward candid logging while hiding those underlying misses from the grade summary. Its “3 times in 4 briefs” answerability criticism also combines unlike defects: interest anchoring, an unanswerable income question and a missing delivery-tool prerequisite. Separate them, and include the actual PD-003 answerability miss. B-range structure/recovery credit is plausible, but the current B− is not independently calibrated.

**Studio Architect:** the table captures many real weaknesses, but omits AD-003's failure to put explanations in-game (the owner did not know what to do with the cheese in a-07) and AD-005's absent near-miss/revision lane. Add both. Recognize AD-006's title-card/contextual-hint response, while leaving outcome pending. AD-010 fixes were relayed but not integrated into templates; “fixed quickly” overstates verification. AD-011 says next-round work was deferred by the owner, so do not turn that authorized deferral into negligence. AD-013/014 now add adoption/ownership context beyond the card's AD-001–012 coverage. B is defensible only as a low-confidence structural judgment, not a tested comparison with the Rig Architect.

**Operator:** after correcting O065, the sampled actions are mostly careful and useful. B+ is still unsupported as a comparative grade: original owner instructions, a complete action denominator and an authenticated decision log are missing. Use “positive observed execution; insufficient evidence for a comparative letter grade.” Keep the run-1 approval conflict unresolved. Neither presume forbidden approvals nor turn the absence of documented violations into “everything … inside its lane.” O059's selective cleanup and O061's owner-directed closure are supported by the mirrored receipts/retro.

**Platform Architect:** update the record as described in finding 6. There is evidence to assess its initial audit and diagrams; there is not yet evidence that it resolved the inherited risks. “Pending outcome” is fair, “no log entries” is false in this snapshot.

**BRIEFS.md:** most rows point to real design gaps, but the “What it caused” heading repeatedly exceeds the evidence. Use “Observed result / plausible contribution.” Specifically:

- Pitch instructions are substantially matched, not a clean control for model ability.
- Depth/friends anchor effects are hypotheses across different cards and criteria. Ten situations defines a 5, not the exact score for eight. The curator's x-18 change to 3 is a judgment consistent with that upper anchor, not mandated by it; O033 and the curator card should say so.
- Free-versus-hand rates support revisiting the deck; they do not identify which deck feature caused the gap. Voice pairing is explicitly tentative in the friends retro.
- Proto-1 should name missing initial exploit acceptance criteria/on-screen explanation requirements, while retaining builder responsibility for explicit rule omissions. Merely failing to prevent an execution error is not automatically a brief defect.
- Research v2 should include its public-evidence ceiling and distinguish required screen searches from optional follow-ups.
- Money-1 also omits economics' deep-dive weight, per its retro; this is a concrete brief gap.
- Validation's evidence-review step worked, but the skeptic also corrected the brief's price comparability, bidder range and implied buyer segment. Keep those framing weaknesses visible rather than summarizing only Word/LibreOffice.
- Remove the closing generalization that nearly every non-worked brief lacks score anchors or stop lists: interest bias, answerability, titles, deck composition and delivery prerequisites are different problems.

**Routing disposition**

Do not approve a model-superiority interpretation. Keeping current seats temporarily is a reasonable operational baseline, provided each untested row says **“incumbent assignment; comparative advantage untested.”** The draft does already give a useful caveat at the top. Repeat it where recommendations are consumed independently, especially curator, prototype lead, research lead and skeptic. Codex already occupies a critic judgment seat, so “Claude in every judgment seat” is not literally accurate either.

O044 supports one successful skeptic pass, not a cross-model experiment: the skeptic had a different objective and the analysts' work to inspect. O027 supports four documented lead interventions, not “caught 4/4” sensitivity against an independently enumerated set of defects. Cross-family review is a design rationale worth testing; it is not measured superiority. The Codex money-1 lead also supplies evidence of successful judgment, albeit on a different brief.

E1–E3 are useful proposals, not yet decision-grade experiments. One extra build cannot establish a general drift rate. E2's agreement with curator cuts or owner picks is a preference measure, not ground truth for exploit closure/depth; include an independently specified mechanical rubric. Record exact model/version, instructions, runtime, budget and repeated cases before changing routing on a “clear gap.” These are recommendations for the owning architects; no experiment was launched.

Verification for this review consisted of read-only source checks, JSON/CSV parsing and independent text/count calculations. No application code was changed and no commit was made, so the pre-commit dashboard smoke test was not run. The original drafts remain available for the Model Architect to revise against these findings.
