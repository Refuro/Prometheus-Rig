# Platform Architect · assessment

**Who:** a Claude Code session in the repo (`PLATFORM-ARCHITECT.md`). **Owns:** `dashboard/`, `setup/`, tests, README/docs, `.gitignore`.
**Assessment:** outcome pending. It started 2026-10-12 (PD-013), and the logged work so far is an assessment plus one feature. **Confidence:** low. [O067]

## Recorded so far
- **PL-001, handover assessment:**
  - **Baseline:** 45/45 smoke checks green, measured on a copy outside WSL.
  - **Top risks named:**
    - loopback requests count as the owner, so a seat could answer its own gate;
    - `/play/` builds run on the console's origin;
    - the most-fixed alert logic has almost no tests.
  - **Smaller items found:**
    - a hard-coded briefs path;
    - a username in setup scripts;
    - a stale `0.0.0.0` hint.

  These are inherited risks: evidence to assess, not failures it introduced.
- **PL-002, a System page:**
  - smoke checks raised to 47;
  - checked in a headless browser at desktop and phone widths;
  - one self-reported miss: it first built only the docs version.

## Since then (PL-003 to PL-007, 2026-10-12)
- **PL-003:** built the Models page. It changed the proposal with reasons: its own module, skipping bad lines, no merging of models.
- **PL-004, PL-005:** a Play builds page and new navigation. A miss in PL-005 (a redirect loop before restart) was logged with a lesson and a test.
- **PL-006:** a platform checkup.
- **PL-007:** quick wins (alert heartbeat, quieter health, the briefs path).
- **R-005/R-006:** a plan, sent for outside review before building. My review: `reviews/R-005-R-006-security.md`.

## Response to MA-007 (PL-008 to PL-010)
- **All 7 findings accepted,** with a threat model.
- **Done and tested** (smoke checks 83/83):
  - a Host allowlist;
  - gate text quoted in decision records (5b);
  - job, rig and lead taken from trusted sources (5c);
  - honest tripwire wording;
  - the suggested tests.
- **Models page:** shows each line's `status` and `written_by`, reads leads' notes from job folders (PD-015), and its own event format is withdrawn.
- **Pending the owner:** the WSL interop and sudo checks, and R-005 step 3.
- I haven't re-checked the code since. The next assessment should test the claimed protections, not just read the log.

## Assessed later
- **Inherited risks:** whether the PL-001 risks get resolved, the gate-trust risk first.
- **Request handling:** how `REQUESTS.md` items are handled and logged.
- **Test coverage:** coverage of the alert logic.
- **Repo hygiene:** nothing private gets committed.

## Since MA-012 (PL-011, PL-012)
- **R-006 built to the three conditions,** confirmed in a real browser.
- **The owner's checks confirmed root via interop and sudo.** It then set out options A, B and C, with a recommendation, instead of building step 3 on a weak boundary. Good judgment.
- **PL-012:** a soft gate maximum, `harvest_hash` matching, and per-seat models in launch records.
- **My re-test (MA-013):** 97/97 reproduced, and my probes held. Three gaps found: builds-port scope (any job file is served), a `*.ts.net` wildcard, and an unchecked `X-Forwarded-Host`. Plus: confirm a token is set.

## Option A and the re-tests (2026-10-13, MA-014 to MA-021)
- **Takes review seriously and fast:**
  - all MA-014 findings fixed or deferred with reasons (PL-027);
  - the four MA-016 findings and Codex's cross-check addressed within about half an hour (PL-030), adopting the
    stronger boundary Codex proposed;
  - my MA-020 hole fixed within the hour (PL-031).
  - It pulled the owner's cards itself while fixes were pending.
- **Re-tested, not just read:** `probe_console.py` 12/12 after PL-031 (the MA-013 gaps closed).
- **Pushed back with reasons where it disagreed:** carrying the fingerprint ledger over (PL-030). I agreed.
- **Misses:**
  - the first round put the owner in front of uncommitted, unreviewed setup scripts (MA-016 finding 2);
  - round 2 still sends the owner to plain git in the agents' repo, and doesn't refuse symlinks (MA-021, R2-1 to
    R2-3);
  - it fixed MA-014 only after the owner's go-ahead, a day after the review (its own words, PL-027).
- **Confidence:** medium.

## Open (as of MA-021)
- **R2-1 to R2-3,** then the owner's two option A cards.
- **Option B** (agents not running as the owner) remains the real boundary; PL-030 says so plainly.
