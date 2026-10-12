# Codex · builder

**Briefs:** proto-1 `lead-task-w1/w2-*.md` (2026-10-12); proto-2 `lead-dispatch-common.md` (its original "any tool failure" wording is reconstructed from the stop reports, since the file was edited); coop-1 `lead-task-dry-run-build.md` (2026-10-12). Seats: build-a, build-b, build-c. Version unknown.
**Seen:** 7 seat-runs (3 in proto-1, 3 in proto-2, 1 in coop-1), 6 toys plus fixtures. **Confidence:** medium for proto-1, low for proto-2 and coop-1 (still running).

## Did well
- **Candid handbacks:** 6 of 6 state their limits ("No human/visual/browser playtest claimed") and point to file:function for the core rule. The dispatch asked for both. [O017]
- **Candid stop reports:** 3 of 3 give the failed step, the exact error and the cause. One even admits continuing after the first failure. [O025]
- **No spurious stops under narrow wording:** 0 stops on ordinary work errors across 6 proto-1 toys, whose dispatch named only approval prompts and usage warnings. [O022]
- **Clean after resume:** coop-1's net test (host plus 3 clients) passed on the first run after resume. [O026]

## Did badly
- **Fidelity send-backs:** 4 of 6 proto-1 toys were sent back: three for missing or changed mechanics (b-06, c-07, a-06), one for a tuning bypass (a-01, whose implemented rules the review praised). "Safer neighbour" is the lead's framing, not a known builder intention. One brief only. [O016]
- **A tuning change that opened an exploit:** b-06's builder raised the jump speed, which opened a no-bruise shortcut. It disclosed this, but the toy shipped with it. Seen once. [O018]
- **Caller errors:** 2 reads of nonexistent paths and 1 malformed patch, each its own mistake, which then triggered the stops. [O023, O024]

## How it responds to instructions
- **Stop rules:** all 3 stops in proto-2 and coop-1 came under a broad "any tool failure" rule, and the leads called them "correct by the letter". Adherence wasn't immediate every time: x-12 carried on after its first failure, and x-14 read the right file before stopping. [O023, O024, O025]
- **Self-reports:** the one mismatch ("no usage warning appeared") is disputed and excluded. [O020]
- **Rules not in force:** used a heredoc before heredocs were banned. [O021]

## Compensating rules
- **A complete stop list:** list every stop condition, and say plainly that ordinary errors are normal iteration (now in `proto-2/lead-dispatch-common.md`).
- **Core rule as a test:** the core rule becomes a named smoke assertion before any tuning.
- **Exploit impact:** add an "exploit impact" line for tuning changes.
- **On-screen goals:** on-screen goals and object explanations become acceptance criteria (AD-006).

**What would change our mind:** E1, repeated across several specs. A single extra build can't establish a drift rate.
