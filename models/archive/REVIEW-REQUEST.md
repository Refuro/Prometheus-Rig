# Review request for a Codex reviewer

**Status:** done. The review is in `REVIEW-codex.md`, and the response is in `LOG.md` MA-004.

The author is a Claude model (Opus 5.5 session). Please check these drafts for bias before anything here becomes routing policy. Files: `observations.jsonl`, `metrics.csv`, `cards/*.md`, `claude.md`, `codex.md`, `ROUTING.md`.

## 1. Claims that favour Claude: check these first
- **O003 / claude--pitcher:** "4 of 7 Claude cards on the board". The room was not blind and the curator was Claude. Is it framed weakly enough?
- **Attribution to the brief:** many Codex lines are attributed to the brief (18 of 36 Codex lines). Did that excuse Codex, or did it just move Codex's faults onto the Claude architect? Spot-check O016, O023, O024.
- **Claude "strengths":** O027, O028, O032, O040 and O047 are partly the briefs asking for that behaviour. Is `brief_asked` set honestly?
- **ROUTING.md** keeps Claude in every judgment seat. Is that supported, or just carrying over STUDIO-PLAN "Claude for judgment"? The only cross-model evidence is O044 (the skeptic found incumbents the analysts missed): one run.

## 2. Claims that may be unfair to Codex
- **O016 (rule drift 4/6):** only one brief. Is "safer neighbour" the lead's framing, not the builder's? Read `proto-1/reviews/lead-*.md`.
- **O042 (money-1 lead):** "dense retro prose" is a reader's judgment. Remove it if it can't be supported.

## 3. Evidence quality
- Open 5 random ledger lines and check that the quoted text is in the named file.
- Check the counts: free vs hand (O004), Depth-5 = 16 (O007, O034), word counts (O002).
- `active_min` is blank on purpose: the OpenRig activity signal is unreliable (ARCHITECTURE-LOG.md PD-007).

## 4. Prompt vs model attribution
For each line marked `attribution: model`, ask whether a different brief would plausibly have changed the behaviour. If yes, change the line to `unclear`.

## 5. Role grades (`roles/*.md`, `BRIEFS.md`)
- The three architects are Claude sessions; the Operator is Codex. Check that the Operator grade (B+) is not lifted or lowered by the author's family, given its thin, second-hand record.
- Check that the Studio and Rig Architect grades are not softened because the author shares their model family. Are the "Did badly" tables complete against their own logs?
- `BRIEFS.md`: check that each "miss" names the brief's gap, not a seat's fault.

Write findings to `models/REVIEW-codex.md`. Please don't edit the drafts directly.
