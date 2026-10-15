# Codex · builder

**Briefs:** proto-1 `lead-task-w1/w2-*.md` (2026-10-11/12); proto-2 `lead-dispatch-*.md` and `lead-dispatch-4beat-*.md`;
coop-1 `lead-task-*.md` (2026-10-12). Seats: build-a, build-b, build-c. Model gpt-6.1-sol where recorded; version unknown.
**Seen:** 9 seat-runs (3 proto-1, 3 proto-2, 3 coop-1): 16 first builds, their send-back fix rounds, and 10
owner-requested revisions (4 coop-1 "rev1", 6 proto-2 four-beat), counted separately from the fix rounds. **Confidence:** medium on
process, low on design fidelity (one model per seat type, so nothing comparative). Updated MA-022.

## Did well
- **Second rounds land:** after send-backs, revisions mostly passed first time. All six proto-2 four-beat revisions
  had zero blocking findings; coop-1 x-03 fixed 7 of 7 send-back items in one round. [O082, O122, O123, O124]
- **Tests the shortcut before fixing it:** wrote regression tests that reproduce each reviewed exploit (RED), then
  fixed it (GREEN). 4 prototypes, 2 seats. [O110, O111]
- **Raises spec problems instead of guessing:** asked for rulings on an exploit the spec left open, a physics
  contradiction and a gate rule that would ban a legitimate route, and showed a critic finding rested on a misread.
  Seen 4 times. [O106, O107, O108, O109]
- **Catches its own misses after acceptance:** found that its accepted x-19's welcome text wasn't in the web export,
  and reported it unprompted. Seen once. [O119]
- **Candid reports:** handbacks state their limits; self-reports matched the critic's later findings. One premature
  "check passed" claim was corrected by the seat within a minute. [O017, O025, O079, O088]
- **No spurious stops under narrow wording:** 0 stops on ordinary errors across 6 proto-1 toys. [O022]

## Did badly
- **First versions often miss the spec's intent:** 13 of 16 first builds were sent back (proto-1 4/6, coop-1 4/4,
  proto-2 5/6). A first-round fidelity problem in these assignments, not shown to be a property of the model. Typical shapes: the core verb could be skipped, a beat reused an earlier mechanism, or
  invented numbers broke the economy. [O016, O078, O080, O081, O083, O112, O113, O114]
- **Fast hand-backs on long time boxes:** first versions came back 9 to 40 minutes after dispatch against 4–6 hour
  boxes. Whether more time would have caught the misses is untested. [O084, O118]
- **Small carry-over slips:** an x-19 help line left in x-12's UI; a tuning change that opened an exploit. Each
  seen once. [O018, O120]

## How it responds to instructions
- **Followed an explicit stop instruction:** three stops on its own caller errors came under an "any tool failure"
  rule that the dispatch stated outright. It originated in the operator's dry-run wording and was reused for real
  builds (attribution brief). This is instruction compliance, a different mechanism from the assets-1 stops on the
  researcher card. [O023, O024]
- **Rules not in force aren't followed:** used a heredoc before heredocs were banned. [O021]

## Compensating rules
- **Narrow stop list:** name the stop conditions and say ordinary errors are normal iteration (SHARED-RULES §2; v1.9
  adds "stop only the work that needs the failed tool" and "your own scripts are your input").
- **Make intent testable:** the core rule, and "each beat needs its own mechanism", as named smoke assertions before
  the first hand-back. The first-version misses are exactly what a critic later finds by reading code.
- **Exploit impact line** for tuning changes.

**What would change our mind:** E1 (a Claude builder on the same specs). Also cheap: give one builder a "self-review
against the spec's questions before handing back" step and see whether first-round send-backs drop.
