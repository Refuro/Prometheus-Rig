# Briefs: observed results and plausible contributions (draft)

**"Worked":** seats did what the brief intended, without workarounds. **"Mixed":** partly. **"Miss":** an important outcome traces plausibly to a gap in the brief. These are observations across different cards, people and criteria, not controlled tests. The owner of each brief is in brackets.

| Brief (version, date) | Result | Observed result / plausible contribution | Evidence |
|---|---|---|---|
| Pitch room v1, pitch-1 (2026-10-11) [Studio] | mixed | Dispatches substantially matched across models (not a clean control: hands and seeds differed); no late-game question, so the ideas were two-minute toys | O002, AD-002 |
| Depth room v1, depth-1 (2026-10-12) [Studio] | mixed | Blind judging held. The critic passed 24/24 with mainly a top anchor (plausible anchor effect). The rubric favoured closed puzzles. No retitle step for revised cards | O007, O015, O036 |
| Friend room v1, friends-1 (2026-10-12) [Studio] | mixed | With an extra low anchor, the critic cut 6 (plausible anchor effect). The retro asks whether voice pairings drove the gate failures | O009, O006 |
| Deck (both rooms) [Studio] | miss | Free pitches 15/18 vs hands 8/45 on boards, for both models. Supports revisiting the deck; which feature matters is unknown | O004, O005 |
| Proto sprint v1, proto-1 (2026-10-11/12) [Studio template, Claude lead dispatch] | mixed | Narrow stop rule: 0 spurious stops. No retry policy: 3 owner gates. One-send-back cap: a known exploit shipped. No on-screen goal or explanation criteria. The 4 fidelity send-backs remain builder execution, not a brief defect | O022, O029, O018, O016, AD-003 |
| Proto sprint v2 lead dispatch, proto-2 (2026-10-12) [Claude lead; wording from the operator's dry-run rows, MA-015] | miss → fixed | "Stop on any tool failure" turned 2 caller errors into stops; clarified | O023 |
| Co-op proto dry-run dispatch, coop-1 (2026-10-12) [Claude lead; same origin] | miss → fixed | The same wording turned a malformed patch into a stop | O024 |
| Design team, bridge-design (2026-10-13) [Studio] | mixed | Measurable specs and cross-review catches. No one-writer-per-file rule: the director overwrote a seat's file. Doc caps exceeded twice. No reference play-view frame for art | O127–O141 |
| Production, bridge-prod m1 (2026-10-13/14) [Studio] | plausible contribution → rule revised | Tests drove the sim and fixtures, not the booted scene. Green builds, soaks and three screenshot rounds passed while mouse clicks couldn't reach the legs, and the owner found it. No named real-input test before AD-032 plausibly contributed. The split between brief, implementation and acceptance is unresolved, and the pre-AD-032 text isn't preserved. AD-032 revised the rule and T-054 reportedly fixed the bug; later builds aren't yet checked. Player-eyes judges screenshots only, by design | O211, O215 |
| assets-1 (2026-10-13) [Rig] | mixed | Whole-phase stops on one failed tool led to SHARED-RULES v1.9 §2 ("stop only the work that needs the failed tool") | O142–O154, MA-019 |
| SHARED-RULES v1.7 / v1.9 (2026-10-13) [Rig] | not yet measured | v1.7 makes "Daemon did not respond" a retry (O136). v1.9 narrows stops. No run since has recorded spurious-stop counts (bridge-prod metrics say "unknown") | O136, MA-019 |
| Diplomacy game 1 (2026-10-13/14) [Rig, lab] | mixed | Game completed with full records. First-turn stops had mixed causes (refused press, prompts). Promise breaks are game play, not a brief gap | `reviews/diplomacy-1/report.md` |
| Revise-cards README, depth-1 [Studio] | mixed | Answered the owner's notes; titles leaked provenance | O015 |
| Research v1, run-1 (2026-10-11) [Rig] | miss | Interests anchored the longlist; no opened-page rule, then an unverified citation | O043, PD-002 |
| Research v2, run-2 (2026-10-11/12) [Rig] | mixed | Required screen-stage overturn searches produced useful evidence. The deep-dive bar was beyond public evidence. No shell rules for Claude seats | O040, O068, PD-003 |
| Money-1 (2026-10-12) [Rig] | miss | Question unanswerable from public evidence; economics' deep-dive weight missing; web route-around unclear | PD-004, O046 |
| Validation v1 (2026-10-12) [Rig] | worked so far | The evidence-review step produced page-verified evidence. The skeptic had to correct the brief's price comparability, bidder range and implied segment. Word/LibreOffice prerequisite missing | O047, PD-011 |

The gaps are different kinds of problem: score anchors, stop lists, interest anchoring, answerability, titles, deck composition, delivery prerequisites, file ownership and tests that skip the real input path. No single fix covers them. Last updated MA-029 (2026-10-14).
