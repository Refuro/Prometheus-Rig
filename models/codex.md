# Codex: what was observed across these assignments

**Coverage (2026-10-11 to 14, updated MA-029/029b):**
- seat roles: pitcher, critic, scout, reviser, builder, researcher, research lead;
- three bridge-design seats (balance, brevity editor, art and audio director);
- three Diplomacy powers;
- bridge-prod's developers and playtest bot;
- the Operator (graded in `roles/operator.md`).

That's 106 non-duplicate ledger lines with model "codex": observations, not independent trials or equal exposure.

**Version, by run:**
- **Diplomacy game 1:** gpt-6-astra for all three powers (report and ledger). One seat's own vaguer "GPT-6" note
  doesn't override that.
- **bridge-design, assets-1 and bridge-prod:** gpt-6.1-sol, per the launch records. Don't carry that over to
  Diplomacy.
- **Earlier runs:** unknown.

**Framing:** Codex seats work under prescriptive dispatches. A pattern that repeats across those assignments is
described as "observed across these assignments", not as a model trait (MA-004). Most role assignments have no
cross-family comparison; pitcher and research lead are the only exceptions (ROUTING). So none of this ranks models.

## Repeated across roles
- **Follows stop and format rules as written:**
  - it stopped under "any tool failure" wording (3 stops, attribution brief);
  - under narrower wording it had 0 such stops across 6 proto-1 toys (O022). Later runs under v1.9 aren't measured;
  - it kept to search caps and card shape;
  - assets-1 had whole-phase stops on one failed tool; v1.9 narrowed that rule.

  [O022, O023, O024, O011, O001]
- **Candid reports:** states limits, withdraws stale results, gives exact errors. Balance reported 24 checks as
  NOT_READY rather than claim passes. [O017, O025, O008, O130]
- **First versions miss the spec's intent; revisions land:** 13 of 16 first builds were sent back. Revisions
  mostly passed first time. [O016, O078–O114, O122–O124]
- **Tests what it fixes:**
  - builders wrote tests that reproduce each reviewed exploit before fixing it;
  - in bridge-prod, dev-a found why mouse clicks couldn't reach the legs and added tests that push real events
    through the viewport. That's the lead's report: T-054 is the task, and the fix is reported in the packet, not
    re-run by me.

  [O110, O111, O212]

## Seen in one role only
- **Playtest bot (bridge-prod):** the final soak passed on the bot's own terms. The limits:
  - nine ten-minute **sim** cases at three rates, plus CPU rewind timings;
  - not a soak of the playable scene, rendered performance, or the playable traveler schedule;
  - zero WAITING observations means recovery wasn't exercised in these logs.

  The lead's report, bounded method. [O214]
- **Score calibration (critic):** consistent with the anchors it was given. With cards and criteria also
  changing, that's a plausible explanation, not proven. [O007, O009]
- **Framing misses in art directions,** fixed in one revision. [O138, O139]

## Not counted against it
- **Capacity errors:** a provider event. [O019]
- **The proto-1 self-report:** disputed, and excluded from the counts. [O020]
- **Diplomacy game 1:** outcomes and latency describe one game, not the model (`reviews/diplomacy-1/report.md` §6).
