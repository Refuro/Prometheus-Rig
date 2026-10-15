# Claude · prototype lead (proto-lead)

**Briefs:** proto-1 `brief.md` (AD-003, 2026-10-11); proto-2 and coop-1 `brief.md` (AD-006/007, 2026-10-12), plus
owner revisions. Opus 5.5 per the leads' own notes; launch records missing or "unknown".
**Seen:** 3 sprints. **Confidence:** medium. Incumbent assignment; comparative advantage untested. Updated MA-022.

## Did well
- **Spec reviews by reading code,** with send-back lists by spec line and `build.py` reruns before accepting.
  Not measured against an independent defect list. [O027]
- **Said what it couldn't judge** on every toy. [O028]
- **Settled conflicts in advance,** and owned its mistakes in writing. When its own send-back suggestion created a
  dominant branch, it recorded that. [O031, O087]

## Did badly
- **Reused a dry-run stop rule for real builds:** the operator's dry-run "any tool failure: STOP" wording went into
  both leads' build dispatches and caused 3 spurious stops. The rule wasn't theirs (MA-015); the carry-over was.
  Seen twice. [O030]
- **Accepted on a green rerun that didn't prove the claim:** x-19's usability revision was accepted without
  checking that its new text file was in the web export; the builder caught it. Seen once. [O121]
- **Untested permission concern from a stale memory note:** predicted a `/mnt/c` approval prompt as an end-of-run
  blocker while other work continued; the later read succeeded after grants. Whether it would have prompted without
  them is unknown. Similar in friends-1 (O075). [O117]
- **Earlier:** a wrong roster claim; capacity blips turned into owner gates (since fixed by AD-010). [O029, O065]

## Compensating rules
- **Vetted stop-rule block,** and never reuse dry-run rules for real work.
- **Acceptance means checking the shipped artifact** (the web build), not just a green rerun.
- **Try the action before reporting it as a blocker;** a memory note about a past prompt is a reason to check, not
  evidence.

**What would change our mind:** a Codex proto-lead under the same template.
