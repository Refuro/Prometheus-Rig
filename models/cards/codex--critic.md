# Codex · critic (depth-critic)

**Briefs:** card review: depth-1 and friends-1 `brief.md` §2/§5 plus `agents/critic/guidance/role.md` (2026-10-12).
Code review: coop-1 `lead-task-critic-*.md`, proto-2 `lead-critic-*.md` (2026-10-12/13). Model gpt-6.1-sol where
recorded; version unknown.
**Seen:** 2 card rooms (45 cards) and 2 code-review sprints (10 prototypes, about 30 review rounds).
**Confidence:** medium on code review, low on card calibration. Updated MA-022.

## Did well
- **Finds the shortcut in code:** bypasses in 9 of 10 first builds it reviewed: a question-defeating bypass in 4
  of 4 in coop-1, and code-traced beat-skipping routes the builders' smoke tests missed in 5 of 6 in proto-2. File:line locations; labels
  source-derived arithmetic as such. [O085, O115]
- **Re-reviews catch what fixes introduce:** a new frame-tight bypass after coop-1's fixes, and a consent skip in a
  revision lesson. [O086, O089]
- **Fast, narrow checks when asked:** six four-beat checks, each about a minute; no false findings identified in
  that round's records (not a measured false-positive rate). [O125]
- **Card rooms:** concrete gate cuts in friends-1 (6 of 21), named open exploits per card, didn't pad. [O008, O009, O096]

## Calibration uncertain
- **Passed all 24 in depth-1 card review.** That's an outcome, not proof of bad judging. No false pass has been shown
  against the rubric, and its summary says it judged written cards, with exploit tests unresolved. [O007]

## Did badly
- **One false blocker:** misread GDScript indentation and reported a blocking route; withdrew it in the next round
  as its own error. Seen once. [O116]

## How it responds to instructions
The task, more than the model, seems to set its strictness. The same seat type passed every card in a card review
with only a top anchor, yet found bypasses in 9 of 10 first builds in code review. Same model, different brief and
task, so this points at the brief. Not proven: different content too. [O007, O085, O115]

## Compensating rules
- **Anchor every score** and force a bottom-third ranking in card rooms.
- **For code review:** ask for one executed repro per blocking finding, which would have caught the indentation misread.

**What would change our mind:** E2, scored against an independently specified rubric.
