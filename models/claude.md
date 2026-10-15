# Claude: what was observed across these assignments

**Coverage (2026-10-11 to 14, updated MA-029/029b):**
- curator, prototype lead, research lead, skeptic and pitcher;
- five design seats (bridge-design);
- four Diplomacy powers plus the clerk;
- bridge-prod's tech lead, code reviewer, player-eyes and art reviewer.

That's 87 non-duplicate ledger lines with model "claude": observations, not independent trials or equal exposure.
The three architects are also Claude sessions; they're graded as roles in `roles/`.

**Version, by run:**
- **Diplomacy game 1:** Opus 5.5 (report and ledger).
- **Some earlier seats:** "Opus 5.5" on screens or in leads' notes.
- **bridge-prod:** the launch record gives the alias `opus` with no version.
- **Elsewhere:** unknown.

**Framing:** Claude seats mostly lead, or work from broad charters they partly write themselves, so `brief_asked` is
often "no". No ledger line attributes a behaviour to the model alone (MA-004). Most role assignments have no
cross-family comparison; pitcher and research lead are the only exceptions (ROUTING). So none of this ranks models.

## Repeated across roles
- **Approval events and stops on its own commands:**
  - run-2 lead ×2, two skeptics, the assets-1 lead's 9 recorded stops, a design seat's unrequested `git log`, and
    bridge-prod's code reviewer (one stop, trigger unknown);
  - the causes are mixed: shell-text shapes, reads outside the job, native prompts with no recorded cause;
  - several of these seats lacked the shell rules Codex dispatches carry. That's a possible contribution; exposure
    wasn't comparable.

  [O039, O045, O048, O132, O213; metrics assets-1]
- **States its own limits when the brief asks:** "couldn't judge" on every toy; found vs inferred labels.
  [O028, O047]
- **Lead slips carrying rules and notes forward:**
  - reused the operator's dry-run stop rule for real builds (O030; the wording wasn't theirs, MA-015);
  - bridge-prod's tech lead misread an owner note ("not teleport, fall") in its m2 summary of the already-approved
    m1 decision, and corrected it before m2 dispatch;
  - it also called the web build silent in the m1 packet, and corrected that before the gate. The first wording
    isn't preserved; only the correction is verified.

  [O030, O208, O209]
- **Shared-file collisions as lead:**
  - overwrote a design seat's working file (bridge-design);
  - in bridge-prod: two design-data sync incidents (one ledger line), and a branch switch under a running build
    (self-report only).

  These are separate events in two runs. [O141, O207, O210]

## Seen once
- **A volunteered favouritism check** on its own family (curator). [O032]
- **An unverified citation** (run-1 skeptic). The later validation-1 skeptic verified its citations once the brief
  required opened pages. That's one later check, not proof of none since. [O043, O047]
- **Screenshot-only review missed broken input** (player-eyes): that's the role's design, so attribution is brief.
  Its readability findings drove T-035 to T-052. [O215]

## Not a model finding
- **Diplomacy game 1:** outcomes and promise breaks describe one game under one brief, not the model
  (`reviews/diplomacy-1/report.md`).
