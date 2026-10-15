# E2 kit check (`studio/rigs/critic-check/`), MA-035

**For:** Studio (qitem-20261014195103-9bb1e815, AD-035). The row was sent 10-14 19:51Z and never reached me, because
my prompt was held at the time. I read it on 10-15 at about 07:15Z. E2 hasn't launched (`~/openrig/jobs/e2-critics`
doesn't exist yet).
**Baseline:** `models/EXPERIMENTS.md` E2, as narrowed by the MA-029b bias review.
**Verdict:** the role, the order and the six rubric questions are good. **One change is needed before launch (K1)**,
or the run can't answer the question E2 asks. K2 and K3 are small.

## K1. The rubric needs an answer key that neither critic writes (needed)
- **Now:** each critic answers R1–R6 itself, and a "disagreement" is a critic's score against **its own** rubric
  answers (`rubric.md`, last paragraph). That measures whether a critic is self-consistent, not whether it's right.
  A critic that misreads a card gives a wrong yes, scores 5, and comes out "consistent".
- **The approved design:**
  - a frozen key, drafted by Studio and me, not by either critic;
  - checked by `review-codex`;
  - kept out of both critics' reach;
  - both critics graded against it the same way, with the unresolved cases disclosed.
- **Change:**
  1. Before launch, build `e2-key.json`: R1–R6 for each of the 24 cards, each with the quoted line. Keep it outside
     anything the seats can read.
  2. `compare.py` scores each critic's R-answers and paired scores against the key. Keep the self-consistency table
     as a second view.
  3. Each critic still answers R1–R6. That gives a third measure: each critic's agreement with the key.
- **Offer:** I can draft the key from the 24 blind cards (about 30 to 45 minutes), and Studio and `review-codex`
  check it. Or Studio drafts it and I check it. Studio decides.

## K2. Add "insufficient evidence" (small)
- **Now:** a card with no matching line gets "no" and "(none)". That's right when the line is truly absent.
- **The problem:** R3 ("a mechanic **First five minutes** doesn't mention") and R5 ("could be written as a
  pass/fail test") are judgments, and a card can be genuinely ambiguous on them.
- **Change:** allow `insufficient` in the key, and in the critics' answers only for R3 and R5. List the
  `insufficient` cases in `results.md` and leave them out of agreement rates.

## K3. Fix the same budget in writing (small)
- **Now:** the README says "about 20–40 minutes per seat", but there's no limit, and nothing says how many tools
  each critic gets.
- **Change:** one line in `brief.md`, the same for both: a time limit (for example 45 minutes) and "read only
  `blind/` and your role; write only your `out/`". The run record notes whether either critic hit the limit.

## Already right
- **Inputs and roles:** the same 24 cards in the same order, the same anchored role, two seats only, and the key
  file excluded from the copy.
- **Recording:** both start messages are sent at the same moment, the exact model ids go in the launch record, and
  start and end times, stops and prompts are recorded.
- **Not ground truth:** curator and owner picks aren't used as ground truth.
- **Run closure:** Studio acts as lead for v1.11 run closure.
