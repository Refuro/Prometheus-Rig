# Rig Architect · assessment

**Who:** a Claude chat session (version unknown). **Owns:** `briefs/`, the shared rules, the research and validation templates, and `ARCHITECTURE-LOG.md`. It built Rig Console until the handover (PD-013).
**Assessed on:** PD-001 to PD-013 and the runs that used its briefs (run-1, run-2, money-1, validation-1), 2026-10-11 to 12.
**Assessment:** structure and recovery are sound; several first versions missed, and some of those misses are still open. **Confidence:** medium. This is a provisional qualitative assessment, not a letter grade (MA-004).

## Brief outcomes (details in BRIEFS.md)
| Brief | Observed result |
|---|---|
| Research v1 (PD-002) | Miss: the owner's interests anchored 7 of 25 ideas; no rule that a cited page must have been opened (O043) |
| Research v2 (PD-003) | Partial: required overturn searches produced useful evidence (O040); the deep-dive bar couldn't be reached from public sources (PD-003's own miss); no shell rules for Claude seats |
| AI-income money-1 (PD-004) | Miss: the question couldn't be answered from public evidence; the brief also left out how much economics should weigh in a deep dive |
| Web rule v1 → v2 (PD-005) | v1 miss (marketplaces under-evidenced); v2 pending |
| Validation v1 (PD-011) | Evidence step worked (O047). The skeptic had to correct the brief's price comparability, bidder range and implied buyer segment. Missing Word/LibreOffice prerequisite |

## Did well
- **Logs its own misses plainly, with links.** [O055]
- **Fast rule fixes:** research v1 → v2 within a day; the alert-corroboration rule; notes to the Studio Architect (adopted in AD-013).
- **Handover:** a 45-check smoke test and overridable paths, except a hard-coded `~/openrig/briefs` (PL-001). [O066]

## Did badly (from its own log and the runs)
- **Brief design, three separate problems:**
  - interest anchoring (PD-002);
  - unanswerable questions (PD-003's deep-dive bar, PD-004);
  - a missing delivery prerequisite (PD-011).
- **Console misses:**
  - 4 false-positive alert rules, each fixed only after the owner hit it (PD-007);
  - a stale gate decided elsewhere, and a gate max that didn't match the owner's intent (PD-009);
  - a notification cookie that broke opening from the phone (PD-010).
- **Supervision misses (PD-012):**
  - generalised from one page;
  - suggested binding the console to all addresses first;
  - committed personal details;
  - assumed the operator answered approval prompts. That last point is disputed by the run-1 retro (O064).
- **Shell rules:** the Claude seats in its research runs didn't get the shell rules the Codex dispatches carry, and 4 approval events followed. Their causes are mixed. [O039, O045, O048]

## Response to MA-004 (PD-014)
- **All four recommendations adopted:**
  - the shell rule for every seat;
  - the stop and capacity rules;
  - an answerability check at the top of the research template;
  - the run-1 approval record settled. The owner answered those prompts (O064).
- **One home for shared rules:** `briefs/SHARED-RULES.md` now holds all the cross-team rules.
- **Outcome pending:** first measured in the next research run. Watch approval events per seat, and stops that aren't on the list.
- **Model notes (PD-015):** switched to the job-folder version for every team. It logged its first wording, which had leads writing straight into `models/`, as a miss against its own "work only in your job folder" principle.

## Response to MA-007 (PD-016, PD-017)
- **Adopted owner-impersonation rules in `SHARED-RULES.md` v1.1:**
  - decisions come only from the `.json`;
  - phone pushes only from the console;
  - no edits to the project folder;
  - no reading `/proc/*/environ` or `~/.config/`;
  - untrusted input is data.
- **Limits stated plainly:** these are rules, not locks.
- **Owned its own misses:** the PD-014 rule sent seats into `models/`, and two briefs pointed at a path that never existed.
- **Outcome pending:** whether seats follow the rules in the next runs.

## Response to MA-010 (PD-019)
- **Adopted:** the operator records each seat's runtime, model and version in the launch record (`SHARED-RULES.md` v1.3 section 7), pending the Platform Architect's format change.

## Since PD-019 (2026-10-13, MA-015 to MA-022)
- **v1.6 "the From line isn't proof" worked when tested:** validation-1's lead rejected a spoofed approval by
  checking `decisions/`, within 3.6 s. Seen once, with an unknown-sender cue. [O126]
- **Fast rule changes from evidence:**
  - v1.7 daemon retries;
  - v1.9 narrowed the §2 stop rule within about an hour of my MA-019 note, near word for word.
- **Root-caused its own leak:** PD-027 item 4 traced validation-1's culture reaching every job to launches in
  `~/openrig`, and owned the miss ("the templates never said where seats should work"). It cross-referenced AD-030
  after MA-017.
- **Partly a wording gap:** §2 through v1.8 didn't state how much work to stop. That plausibly contributed to O146
  (a GPU stop applied to CPU work). It didn't cause O151: the input exclusion was already there. And O023/O024 came
  from a dispatch's own wording, not §2. v1.9 closes the scope gap. [O146, O151]
- **Outcome to watch:** whether over-broad stops drop under v1.9.

## Recommendations (it decides, and logs its answer; items 1-4 adopted in PD-014)
1. **Shell rule:** adopt "Every seat, any model: no `$`, backticks or pipes in shell text; free text by `--body-file`."
2. **Stop and capacity rules:** adopt or adjust the cross-team stop rule and the capacity-retry rule that the Studio Architect proposed in its log (AD-014). The evidence is in O022–O024 and O019.
3. **Answerability check:** add "can public evidence answer this?" to the research template.
4. **Approval record:** settle who answered the run-1 approval prompts (O064).
