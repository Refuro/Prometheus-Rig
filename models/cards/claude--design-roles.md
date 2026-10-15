# Claude · design-team roles (creative director, feel, systems, UX, narrative)

**Briefs:** bridge-design `brief.md` and `director-dispatch-*.md` (2026-10-13). Model: the leads' notes say Opus 5.5
for the creative director; the launch record says "unknown" for every Claude seat.
**Provenance:** these lines are the lead's account (MA-019). The cited files exist, but their content wasn't checked,
except O132 (verified) and O141 (partly). O133 and O134 cite queue rows only; unchecked.
**Seen:** one run, one seat per role. **Confidence:** low; everything here is seen once. Incumbent assignment;
comparative advantage untested. Written MA-022.

## Feel designer (design-feel)
- **Did well:** a deterministic beam solve with measurable acceptance checks, backed by an unrequested reference
  solve it re-ran after changes. In cross-review, caught sim-vs-content conflicts others missed. [O127, O128]

## Systems designer (design-systems)
- **Did well:** design, store doc, content data and achievements in one pass; folded every accepted review item into
  its own files without disputes. [O129]

## UX designer (design-ux)
- **Did well:** measured contrast ratios and a 16:9 framing collision, and flagged them to the owning seats rather
  than editing their files. [O133]
- **Did badly:** ran an unrequested `git log`, which raised a prompt the operator cancelled. Its doc went over the
  ~1,500-word cap twice until asked to move tables to data files. [O132, O134]

## Narrative designer (words-narrative)
- **Did well:** recommended a small ambient story over a fuller one, and caught stale achievement strings outside
  its own files. [O135]

## Creative director (lead)
- **Did badly:** overwrote design-feel's working file with its own summary while feel was writing it; feel re-added
  the exact values. Partly verified (the lead's account plus feel's re-append row). [O141]

## Compensating rules
- **One writer per file:** say which seat owns each working file; the lead summarises in its own file.
- **Read-only git** gets a pre-approval or a "don't".

**What would change our mind:** a second design run, or a Codex seat in one of these roles.
