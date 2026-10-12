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
