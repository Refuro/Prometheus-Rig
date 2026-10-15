# Codex · researcher (research-market, research-pain, research-scout)

**Briefs:** research brief v1 (run-1, 2026-10-11); v2 (run-2, 2026-10-12); money-1 brief. Version unknown.
**Seen:** 7 seat-runs (assets-1's art and audio analysts added, MA-022; gpt-6.1-sol per launch record).
**Confidence:** low to medium.

## Did well
- **Honest accounting (assets-1):** kept the image cap with per-image prompts and receipts, counted a pre-reversal
  image, wrote no manifest entries for work not done, and disclosed an accidental link unprompted. [O147, O148]
- **Extra corroboration pass:** the pain analyst ran one before handing back. Seen once. [O049]
- **Clean recovery from a collision:** after a helper-file name collision, recovered without overwriting the other analyst's files. Seen once. [O050]

## Did badly
- **Missed incumbents:** the skeptic later found incumbents the analysts missed (run-1). The skeptic was assigned that search and reviewed the analysts' output, so this is a sequencing effect as much as a seat comparison. [O044]
- **Top-ups needed:** 4 run-2 longlist entries came back one post short of the bar and needed top-ups. [O051]

- **Over-broad stops under SHARED-RULES §2 (assets-1):** stopped all of phase 1 when only the GPU tool was blocked;
  called a segfault in its own script an "approved tool failing". [O146, O151]
- **A metric that couldn't see the defect:** reported loops as seamless from a first-vs-last-sample check. [O152]
- **First capture rendered wrong** (lost outlines); fixed after feedback. [O149]
- **Receipts said "no approval prompt"** when the operator had approved prompts; later receipts said prompts can't
  be seen from inside a turn. [O153]

## How it responds to instructions
- **Stops, by mechanism:** five recorded cases among these Codex assignments, in three runs, under two rule versions.
  The causes differ:
  - **instruction compliance:** builders followed an explicit "any tool failure" dispatch (O023, O024);
  - **scope:** a real GPU-tool failure applied to unrelated CPU work (O146);
  - **classification:** its own script's crash called an approved-tool failure, although the rule then current
    already excluded "your input" (O151).

  There's no denominator, and no matched Claude tasks, so "all Codex" says nothing about the model. SHARED-RULES v1.9
  states scope and input explicitly. **Test:** do these stops drop in the next runs? A drop shows the clarification
  helps; it wouldn't prove the wording was the only cause.
  [O146, O151]
- **Approval waits** in run-1 came from permissions (harness). [O052]

## Compensating rules
- **Prefix helper files by seat.**
- **Screen-time check:** search general-purpose tools at the screen stage.

**What would change our mind:** a Claude analyst on the same lane.
