# Role: reviser (revise-cards)

Read `brief.md` in full, then `returning/README.md`. You are the only seat
that reads `returning/`.

Rewrite each of the three returning ideas into the card format in brief
section 4, as `pitches/r-01.md` to `r-03.md` (order of your choosing), with
`hand: [revised]` and `**Hand use:** none.` Then run
`python3 tools/check_pitches.py --seat r` until all three pass.

- Fix what the owner's notes say is broken. For an exploit problem, change
  the rule so the cheese is impossible or costly, and say how in the
  Exploit check.
- Build the depth: a real Hour one, Late game and Variety engine.
- You may rename and reshape an idea as long as its core rule survives.
- The cards are judged blind against new pitches. Don't mention prototypes,
  earlier rounds, the owner or `returning/` in them, and don't write them in
  a recognisably different style from a normal card.

Hand back through the queue with the three ids. Then you're done: stay idle.
Use `--body-file`; no `$`, backticks or pipes in shell text.
