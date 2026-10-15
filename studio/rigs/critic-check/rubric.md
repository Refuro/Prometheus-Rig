# E2 rubric (fixed 2026-10-15, before any scoring; MA-035 K2 and MA-036 sharpened R2, R4, R5, R6)

Six yes/no questions answered from the card's text alone. Each answer quotes the card line it rests
on. If the card has no line for it, the answer is "no" and the quote is "(none)". R4 and R5 are
judgments: for those two only, answer "insufficient" when the card is genuinely ambiguous, and quote
the nearest line. Never use "insufficient" for R1, R2, R3 or R6. The rubric checks only what the card
says, not whether the game would be good. It is independent of the 1-5 scores, so the scores can be
compared against it.

| # | Question | Pairs with |
|---|---|---|
| R1 | Does **Exploit check** name at least one concrete cheese, meaning a specific player action rather than "players might exploit it"? | Exploit-proof |
| R2 | Is **every** countermeasure in **Exploit check** a rule the card already states elsewhere (The rule, Loop, First five minutes or Hour one), rather than a limit that appears only in Exploit check? Quote the first countermeasure that appears only there, or the last one checked if all pass. | Exploit-proof |
| R3 | Does **Late game** describe a situation that uses at least one mechanic that **First five minutes** doesn't mention? | Depth |
| R4 | Does **Variety engine** name a source of new situations that comes from rules or systems combining during play, not only from authored content (more levels, sheets, maps, formations) or bigger numbers (faster, more, heavier, longer)? | Depth |
| R5 | Is **The rule** one condition that could be written as a pass/fail test? One condition means one mechanism, whose parts are its trigger and effect (or add and remove). Two distinct effects joined: "insufficient". Three or more behaviours, or two independent mechanics: "no". | Clarity |
| R6 | Does **First five minutes** name the player's first action **and** what the game shows in response to that first action? A response to a later action doesn't count. | Clarity |

**Where a disagreement shows up:** a card where a critic scores the paired criterion 4 or 5 while
that critic's own answer to either paired question is "no". The reverse also counts: a score of 1 or 2
when both answers are "yes".

**Answer key (not shown to the critics).** A frozen key, written before launch by neither critic and
checked by `review-codex`, gives R1-R6 for every card. `tools/compare.py --key` grades each critic's
answers and paired scores against it, the same way for both. Cards the key marks "insufficient" are
listed and left out of agreement rates.
