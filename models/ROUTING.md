# Routing guide (revised after Codex review, MA-004)

These are recommendations only. Per ROLES.md, the owning architect decides routing for its own team, and the owner settles disagreements.

**Basis:** observations.jsonl (69 lines) and metrics.csv (38 seat-runs), 2026-10-11 to 12. Every role has been run by **one model only**, except pitcher (one non-blind room) and research lead (one Codex run). Each row is therefore an **incumbent assignment; comparative advantage untested**. Keeping incumbents is an operational baseline, not evidence that either model is better. Codex already holds one judgment seat (the critic). The prior guide (`GameProjects/AVAILABLE_AGENTS.md`, 2026-07-27, older versions, Cursor) is a hypothesis, not evidence.

| Role | Keep (incumbent) | What we saw | Risk | Rules to put in the brief |
|---|---|---|---|---|
| **Pitcher** | Codex; try Claude once, blind (E3) | 35/35 valid at handback; free > hand for both models (O004); Claude untested blind (O003) | Convergence on shared settings | Settings without replacement; 4 hands + 3 free |
| **Critic** | Codex. *Incumbent; comparative advantage untested.* | Decisive with an extra low anchor (O009); passed everything without one (O007) | Calibration may follow the anchors | Anchor every score; bottom-third ranking; gate threshold in the critic's own file |
| **Scout** | Codex | Kept to the budget (O011); theme-instead-of-verb queries (O069) | "Fresh" overclaims under a 3-search cap | Core-verb search first; a 4th search on conflict |
| **Curator** | Claude. *Incumbent; comparative advantage untested.* | Blind discipline (O036); uneven unlabelled cuts (O033) | Own-family preference when not blind | Always blind; "lead judgment" labels (AD-010); same reason, same score |
| **Reviser** | Codex (seen once) | 1/3 picked blind (O015) | Provenance leaks | Retitle in the first dispatch |
| **Builder** | Codex, pending E1 | Candid reports (O017, O025); 4/6 fidelity send-backs (O016) | Mechanic changes; caller errors; literal stops | Exhaustive stop list; core rule as a smoke assertion; "exploit impact" line; on-screen goal criteria |
| **Prototype lead** | Claude. *Incumbent; comparative advantage untested.* | 4 documented send-backs (O027); wrote the broad stop rule (O030); wrong roster claim (O065) | Rules too broad for literal followers | Copy a vetted stop block; check the roster with `rig ps` |
| **Research lead** | Claude. *Incumbent; comparative advantage untested.* A Codex lead also ran money-1 cleanly (O042) | Required overturn searches done (O040); approval events (O039) | Approval events; usage limits | Shell rules in startup; pre-approved validators |
| **Skeptic** | Claude. *Incumbent; comparative advantage untested.* | Required verification done (O047); one unverified cite under v1 (O043) | Unverified citation if the rule lapses | Cite opened pages only; found/inferred labels |
| **Design seats** | No evidence (team not launched) | — | — | Log the first run |

## Rules for every seat
1. **Shell text:** "No `$`, backticks or pipes in shell text; free text by `--body-file`." Codex dispatches already say this. 4 approval events occurred on Claude seats, which lacked it (causes mixed).
2. **Stop rules:** written once (the Studio Architect's AD-014 proposal to the Rig Architect) and copied verbatim. Leads don't improvise them.
3. **Blind judging:** wherever the author's model would be visible to the judge.
4. **Record model per seat:** record the model and version for each seat, so routing evidence can name what actually ran.
