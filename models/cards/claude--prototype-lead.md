# Claude · prototype lead (proto-lead)

**Briefs:** proto-1 `brief.md` (AD-003, 2026-10-11); proto-2 and coop-1 `brief.md` (AD-006/007, 2026-10-12). Version unknown.
**Seen:** 3 sprints (proto-2 and coop-1 still running). **Confidence:** medium for proto-1. Incumbent assignment; comparative advantage untested.

## Did well
- **Spec reviews by reading code:** 4 documented send-backs with spec line references, 2 toys accepted first time, and `build.py` rerun before accepting. The brief required the review and the rerun. Not measured against an independent list of defects. [O027]
- **Said what it couldn't judge** on all 6 toys, as the brief asked. [O028]
- **Settled a conflict in advance:** a spec-vs-brief key conflict, in the dispatch. Seen once. [O031]

## Did badly
- **Wrote the "any tool failure" stop rule** that preceded 3 Codex stops (2 leads). [O030]
- **Wrong roster claim:** its proto-1 dry-run receipt said only build-a was present; the operator's verification found all four seats ready. Cause unknown. [O065]
- **Escalation cost:** 3 capacity blips became 3 owner gates. The template had no retry policy. Addressed by AD-010. [O029]

## Compensating rules
- **Vetted stop rules:** copy a vetted stop-rule block rather than writing one.
- **Check the roster:** check the roster with `rig ps` before reporting it.

**What would change our mind:** a Codex proto-lead under the same template.
