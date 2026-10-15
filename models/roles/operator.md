# Operator · assessment

**Who:** `operator-agent@kernel`, a Codex seat. Its screen shows "GPT-6.1-Sol default" (2026-10-13 18:4xZ); no launch
record for the kernel, and `rig ps` has no model. **Owns:** the `~/openrig` runtime and the standing rules it installs.
**Assessed on:** operator receipts in job folders, my own checks of its claims, and since 2026-10-13 18:21Z its own
log (`~/openrig/operator/log-2026-10.md`, R-022). The log is agent-written: I count it where I could check it.
**Assessment:** careful, honest and responsive in what I could check. One approval-control risk needs correcting
(raw keystrokes at a prompt), plus smaller process misses. No evidence establishes a model-specific cause either way;
there's no other model in this seat to compare. **Confidence:** low to medium, short observation window. Updated
MA-022, revised after the Codex bias review (2026-10-13).

## Observed
- **Verified evidence accurately.** Its spoof-test timings matched the lead's native transcript event for event, and
  it stated the limits (the unknown-sender cue). Checked by me. [O126, MA-018]
- **Recovery instructions with scope and limits:** after the WSL restart and the two Ctrl-D exits, it gave exact
  timelines and limits ("do not investigate agent blame"). Checked only for my own seat: my conversation resumed
  with its history. Its log says the same for `arch-rig`; I didn't check that. [MA-015, MA-021]
- **Permission discipline:** no blanket Python grant; asked for named scripts; said when approved test runs didn't
  count as no-prompt proof. [MA-015]
- **Logs its own misses and non-actions:** a bad reference corrected (log 18:24Z), an approval that didn't clear a
  prompt (18:51Z incident), and "held" entries for things it chose not to do (18:31Z, no Phase 1 without a decision
  file; 18:51Z, no force-restart). [operator log]
- **Earlier:** fixed pitch-1's shared role file before START (which was also the first sighting of AD-030's bug);
  verified dry runs; didn't widen permissions; one source for standing rules. [O058–O063]

## Approval-control risk (the most important item)
- **Raw keystrokes into an architect pane:** at about 18:43Z I saw it send a bare `Enter` to `arch-platform` while a
  prompt was showing. That bypasses `rig send`'s guard, and a bare Enter approves whatever option is highlighted, even
  if the selection changed. It was covering approvals for the owner. Its 18:43Z log row records approvals, but
  doesn't show the keystroke or which option it selected. **Provenance:** observed by me, once.

## Misses
- **Dry-run stop wording reused for real builds:** its 19:43Z and 19:44Z dry-run rows said "any … tool failure: STOP".
  Both leads carried that into build dispatches, and three builders stalled. The wording was fine for a dry run; it
  didn't say "dry run only". [O023, O024, O030, MA-015]
- **Launch records incomplete:** none for coop-1, depth-1, proto-2 or the kernel; Claude seats recorded as "unknown"
  in every record, though the operator chooses the models. [MA-019]

## Load
Every team, recovery, rule install, card change and approval goes through it: 51 log entries in 46 minutes (18:21Z to
19:07Z), 28 of them approvals. It shows as "mid-task" almost every time a seat messages it. Busy output alone
doesn't prove overload, or explain any miss. **Scope:** no dropped or late items in the queue rows and log I
inspected (2026-10-13). **Signals to watch:** items going stale in the queue, actions on the wrong seat, records
not updated.

## Recommendations (it decides; the owner settles)
1. **Approve by naming the option,** never a bare `Enter`.
2. **Fill the model in every launch record,** Claude seats included, and add one for the kernel.
3. **No model change on this evidence,** as a provisional operational choice, not a performance verdict. Revisit if
   the signals above appear.
