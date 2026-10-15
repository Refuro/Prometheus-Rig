# Head-to-head proposals (proposals only; not run)

These are recommendations for the owning architects. Before any result changes routing, each run must record:
- the exact model and version;
- the instructions, runtime and budget;
- **repeated cases**, since one comparison isn't decision-grade.

## E1 · Claude builder vs Codex builder, same specs
- **Question:** are the 4 of 6 proto-1 fidelity send-backs (O016) specific to the model, or to the spec, time box and template?
- **Setup:**
  - At least 3 specs. Each is built twice, by a Claude Code builder and a Codex builder, under the same common dispatch and stop block.
  - Folders are named x and y, so the lead reviews blind.
- **Yardstick:**
  - per spec clause, whether the mechanic matches on the first handback;
  - send-backs;
  - stops, split into real and caller errors;
  - time to green;
  - whether limits are disclosed.
- **Cost:** about 3 extra builder sessions (Claude usage) plus reviews.
- **Would change routing if:** across all 3+ specs, one family is consistently more faithful at similar cost.

## E2 · Two critics, same blind cards
- **Question:** is critic calibration about the model or the anchors (O007 vs O009)?
- **Setup:**
  - Re-judge depth-1's 24 blind cards with a Codex critic and a Claude critic. Both use a new role file that anchors every score.
  - Fix an independent mechanical rubric before scoring, e.g. "the exploit named in the card's own check is closed: yes/no".
- **Yardstick:**
  - agreement with the rubric, and between the two critics;
  - score spread.
  - Agreement with the curator's cuts or the owner's picks is a preference signal only, not ground truth.
- **Cost:** 2 critic sessions, about 20 min each.
- **Would change routing if:** under full anchors, the critics diverge and one tracks the rubric clearly better.
- **Status:** approved by the owner, 2026-10-14, with a budget of two critic sessions. Studio owns the run and
  schedules it after Bridge. The operator launches the seats.
- **The narrower question for this run (MA-029b, from the Codex bias review):**
  - With only two approved sessions and one anchor condition, E2 compares two critics under the same anchors.
  - It can't separate model effects from anchor effects; that needs an anchor/no-anchor control, which would be a
    later, separately approved run.
- **Answer key, frozen before scoring:**
  - **Definitions:** criterion definitions and per-card labels for the mechanical rubric, with
    "insufficient evidence / ambiguous" allowed where a written card can't settle it.
  - **Who builds it:** neither critic. Studio and the Model Architect draft it, and a reader from the other family
    (`review-codex`) checks it.
  - **Storage:** kept out of both critics' reach, with the unresolved cases listed.
  - **Grading:** both critics are graded against it the same way afterwards, with the unresolved cases disclosed.
- **Same conditions:**
  - the same time and tool budget;
  - fresh contexts;
  - no access to prior or each other's outputs;
  - the exact model and harness version recorded for both.
- **What the Model Architect needs from the run (for grading; Studio decides how):**
  - **Seats:**
    - one `claude-code` seat and one `codex` seat;
    - each launch record names the model (`gpt-6.1-sol`, and the Claude model as shown);
    - nothing else changes, so there's no full-team restart.
  - **Same inputs:**
    - the 24 cards in `~/openrig/jobs/depth-1/blind/` (copied into the new job), in the same order;
    - the same anchored critic role file;
    - the same rubric, fixed before scoring.
  - **Kept from each critic:** the old `depth/` notes, `board.md`, the gate files and the other critic's output.
  - **Per card, each critic writes:**
    - each criterion's score;
    - the mechanical rubric answer (yes / no / insufficient evidence) with the line it rests on;
    - a one-line reason.
  - **Recorded by the lead:**
    - start and end times;
    - stops (real or spurious);
    - prompts.
  - **Not ground truth:** agreement with the original curator or the owner's picks is reported as a preference
    signal only.
  - **One run is not decision-grade:**
    - the result is "consistent with" or "not consistent with" a model difference;
    - a routing change needs a repeat, as in the rules at the top of this file.

## E3 · One pitch room, mixed models, identical hands, judged blind
- **Question:** does the pitcher's model matter once judging is blind (O003)?
- **Setup:**
  - 2 Codex and 2 Claude pitchers; each cross-family pair gets identical hands.
  - Blind ids, with the key closed until the gate.
  - Repeat over 2 rooms if possible.
- **Yardstick:**
  - board share and owner picks by model on identical hands;
  - word counts;
  - checker passes.
- **Cost:** 2 Claude pitcher seats (about 3 min each) per room.
- **Would change routing if:** a gap repeats across rooms. If there's no gap, Codex pitchers stay, which saves Claude usage.
