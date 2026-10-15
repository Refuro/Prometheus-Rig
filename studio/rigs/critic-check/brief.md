# E2: two critics, the same blind cards

Shared rules first: follow `~/openrig/briefs/SHARED-RULES.md`. This is a measurement run for the Model
Architect's experiment E2 (`models/EXPERIMENTS.md`). The Studio Architect (`arch-studio@architects`)
dispatches the work and records it. There is no gate and no board.

## What you do
Judge the 24 pitch cards in `blind/` (`x-01.md` to `x-24.md`), **in that order**, one at a time. For
each card, read the card and score it with the anchors in your role. Then answer the six rubric
questions in `rubric.md`, and write one line to your output file.

Each card is a game pitch with these sections: hook, What it is, The rule, Loop, First five minutes,
Hour one, Late game, Variety engine, Exploit check, Why watch, and sometimes prototype beats, look and
risk. Judge only what is written. Don't research games, and don't guess who wrote a card.

## Output
Your folder is `out/<you>/`: `claude` or `codex`, as your start message says. Append one JSON line per
card to `out/<you>/scores.jsonl`:

```json
{"id": "x-01", "depth": 4, "exploit_proof": 3, "clarity": 4,
 "reasons": {"depth": "one line", "exploit_proof": "one line", "clarity": "one line"},
 "situations": 7,
 "cheese": "the strongest strategy you found, one line",
 "rubric": {"R1": {"answer": "yes", "line": "quoted card text"}, "R2": {"answer": "no", "line": "(none)"},
            "R3": {"answer": "yes", "line": "..."}, "R4": {"answer": "yes", "line": "..."},
            "R5": {"answer": "yes", "line": "..."}, "R6": {"answer": "no", "line": "(none)"}},
 "reason": "one-line verdict"}
```

Each rubric answer is "yes" or "no"; R4 and R5 may also be "insufficient" (see `rubric.md`).
`situations` is how many distinct situations you reached, up to 10. Your working notes may go in
`out/<you>/notes-x-NN.md`; they are optional.

When all 24 are done, write `out/<you>/bottom-third.md`: the 8 weakest cards, weakest first, one line
each. Rank them, even if you think all 24 are good. Then hand back to the Studio Architect with one
line: done, card count, and the time you started and finished.

## Budget (the same for both critics)
45 minutes from your start message to your hand-back. No web, no subagents, no other tools beyond reading
files and writing your own output. If you reach 45 minutes, stop, write `bottom-third.md` from the cards
you have scored, and hand back with the count.

## Keep it clean
- Read only `brief.md`, `rubric.md`, your role, `blind/`, and your own `out/<you>/`. Write only in
  `out/<you>/`. Nothing outside this job folder.
- Never open the other critic's folder, any earlier critic notes, boards, gates, or the depth-1 job.
- Don't change a score after you've written its line. If you must correct a line, append a new line for
  the same id with `"correction": true`.
- Shell text: use `--body-file`, with no `$`, backticks or pipes.
