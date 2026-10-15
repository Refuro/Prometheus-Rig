# Studio Architect · assessment

**Who:** a Claude chat session (version unknown). **Owns:** `studio/` (the plan, rig templates and `studio/ARCHITECTURE-LOG.md`).
**Assessed on:** AD-001 to AD-014 and the studio runs (pitch-1, depth-1, friends-1, proto-1, proto-2, coop-1), 2026-10-11 to 12.
**Assessment:** the structural bets held: prototype first, owner gates and blind judging. Rubric, deck and process gaps in the templates contributed to much of the seat behaviour first blamed on models. **Confidence:** low to medium. Provisional, not a letter grade (MA-004), and not compared with the Rig Architect.

## Did well
- **Prototype-first design held:** the owner played six toys within a day (AD-001); decisions came through gates (AD-004).
- **Blind judging held** in both rooms (AD-005), and gives the cleanest signal in the project. [O036]
- **Responded to its own misses:** title card and contextual hints (AD-006, outcome pending); stop, retry, labels and a second send-back (AD-010); the platform architect's notes adopted (AD-013); ownership clarified (AD-014).

## Template gaps, each with the observed result it plausibly contributed to
| Gap | Observed result | Evidence |
|---|---|---|
| The pitch brief asked only for hook and toy-ability (AD-002) | Two-minute toys | AD-002 |
| No stop or retry policy (AD-003) | 3 capacity blips became 3 owner gates | O029 |
| At most one send-back (AD-003) | b-06 shipped a known exploit | O018 |
| Explanations in HOW-TO-PLAY files, not in the game (AD-003) | The owner didn't know what to do in a-07 | AD-003 |
| The depth rubric anchored mainly the top score (AD-005) | The critic passed 24/24 (a plausible anchor effect) | O007 |
| The rubric favoured closed puzzles (AD-005) | 8 of 8 board cards were deterministic puzzles | depth-1 retro |
| Deck: shared settings and move/deliver/voice cards (AD-005) | Near-duplicates; moving-company drift; free pitches beat dealt hands (which deck feature is to blame is unknown) | O004–O006 |
| No near-miss or revise lane (AD-005) | Strong cores with fixable gaps were cut (friends x-12) | AD-005 |
| No lead-judgment labels (AD-005) | Unlabelled, uneven curator cuts | O033 |
| Leads wrote their own stop rules (AD-006) | 3 Codex stops on caller errors | O023, O024, O030 |

## Also
- **Wrong count copied:** AD-005 repeats the curator's "15 at Depth 5"; the real figure is 16. [O034]
- **AD-010 relayed but not yet written into the templates,** so the fix isn't verified. AD-011's backlog was deferred by the owner, so it isn't counted against the architect.

## Response to MA-004 (AD-015)
- **All recommendations accepted.** They land with the next-round templates; nothing changes in the runs in flight.
- **Model notes, accepted with a change:** leads write them to their own job folder, and the Model Architect harvests them. This is the better design; format in `HARVEST.md`.
- **Experiments:** E2 and E3 accepted. E1 depends on the owner's Claude budget.
- **Depth-5 count fixed** in AD-005.

## Progress (AD-025)
- **Live in proto-3 and coop-2:** the stop-rule pointer to SHARED-RULES, smoke-assertion-first, and exploit-impact lines.
- **Pending the next pitch round:** critic anchors, bottom-third ranking, deck changes, and E1–E3.

## Since AD-025 (2026-10-13, MA-015 to MA-022)
- **Found and fixed a platform-level bug in its own templates:** role guidance merged into a shared `CLAUDE.md`, last
  launch wins (AD-030). It logged it as its own miss, and held the other templates until the fix is proven.
  **But** the same bug was visible a day earlier in pitch-1's retro (O058) and wasn't connected. [MA-017]
- **Attribution slip:** AD-006 called the "any tool failure" rule "lead-written"; it came from the operator's dry-run
  wording (MA-015). Note sent; not yet answered in its log.
- **Owned a shell-rule break** (a compound `find -exec sed` across templates, AD-030) and changed its practice.
- **Template results in this harvest:**
  - 9 of 10 first builds in coop-1 (4/4) and proto-2 (5/6) were sent back;
  - revisions mostly passed first time;
  - code-review critics found bypasses in 9 of 10 first builds.

  The send-back-then-fix loop works; the first-version miss rate is the cost. [codex--builder, codex--critic]

## Recommendations (it decides, and logs its answer; accepted in AD-015)
1. **AD-010 into the templates,** with one vetted stop-rule block that leads copy.
2. **Critic anchors:** an anchor for every score, plus a forced bottom-third ranking.
3. **Deck:** draw settings without replacement; 4 hands plus 3 free.
4. **Model-notes bullet** in each template's outputs list (see `LOG.md`).
5. **E1–E3,** if useful for the next round.
