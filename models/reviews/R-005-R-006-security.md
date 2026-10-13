# Review: R-005 / R-006 security plan, and the Models page (PL-003)

**Requested by** the Platform Architect, relayed by the owner, 2026-10-12. **Reviewer:** the Model Architect (an Opus session). I didn't design this plan, but I will later assess its outcome, so this review gives findings and risks only. The design choices stay with the Platform Architect.

**Read:** `REQUESTS.md` R-005/R-006, PL-001, PL-006, PL-007, `serve.py` (auth, POST, `translate_path`, headers), `gates.py` (`safe_path`, `_load_gate`, `decide`, builds), `setup/install-dashboard-service.sh`, `SETUP.md`, `models.py`, `models.html`, `decide.html` renderer. Nothing on the live rig was touched. "Verify" below means it is inferred from the code and setup files and should be tested on the PC before relying on it.

## Verdict
The plan points at the right problems, but as written two paths stay open after all three R-005 steps:
- **Editing the console's code:** any seat can change the code itself.
- **Root through WSL interop:** any seat may be able to become root.

Step 2 is also largely bypassable until step 3 lands. R-006 is sound, with three conditions to make explicit. I'd reorder the work and add four items.

## Findings, most important first

**1. The console's code can be changed by any seat. (High; not in the plan.)**
- **Where the code runs from:** the service runs `serve.py` from `/mnt/c/.../OpenRig/dashboard` (`install-dashboard-service.sh`: `WorkingDirectory=$DASH`). The seats run as the same Linux user, and the operator is a no-sandbox Codex seat that "can reach /mnt/c" (CHEATSHEET).
- **The effect:** a seat that edits `nav.js`, which every page loads live, runs JavaScript on the console's origin with your cookie. Editing `serve.py` takes effect at the next restart.
- **Step 3 alone doesn't stop this:** a separate console user doesn't help while the code sits in a folder the seat user can write. `/mnt/c` (DrvFs) doesn't enforce Linux users by default. *Verify:* check the mount options with `mount | grep /mnt/c`.
- **Live example today:** two room-lead seats appended 5 lines to `models/observations.jsonl` (O071–O075), following the earlier PD-014 rule. That was benign and in good faith, but it shows seats write to `/mnt/c/.../OpenRig` freely.
- **Suggested direction:** run the console from a copy owned by the console user (a deploy step), read-only to seats.

**2. Step 3 may be bypassable through WSL interop. (High; verify.)**
- **The setting:** `SETUP.md` writes `[interop] appendWindowsPath=false`, which leaves interop itself **enabled**.
- **The risk:** with interop on, any seat can usually run `/mnt/c/Windows/System32/wsl.exe -u root …` and become root inside WSL with no password. As root it can read a "seats can't read it" token file, and from there act as the console.
- **Before building step 3:**
  - **Test from a seat-equivalent shell:** run `/mnt/c/Windows/System32/wsl.exe -u root id`.
  - **If it works, decide between two options:**
    - set `[interop] enabled=false`, after checking what else relies on Windows commands from WSL (the keep-alive? the operator?);
    - accept it in writing as residual risk.
- **Sudo:** check whether the seat user has sudo rights without a password.

**3. Step 2 alone does little against seats, but blocks DNS rebinding, which deserves its own line. (Medium; cheap.)**
- **Why step 2 is weak alone:** the token lives in `~/.config/rig-console.env` and in the process's `/proc/<pid>/environ`. Both are readable by the same user, so step 2 ("require the cookie on loopback POSTs") only binds seats after step 3.
- **The open path today:** seats browse the web (web rule tier 4). A hostile page can DNS-rebind its own domain to `127.0.0.1:8800`, become same-origin with the console, set `X-Rig-Console: 1`, and POST `/api/gate`. It needs no cookie today, because loopback requests skip the token.
- **The fix:** step 2 closes the POST. A **Host-header allowlist** closes this path and the GET data reads too, independently: allow `127.0.0.1:8800`, `localhost:8800` and the Tailscale name, and reject everything else. A few lines; worth doing first.

**4. Step 1 can only catch naive forgery until step 3. (Medium.)**
- **Why:** any record the console keeps to compare against (the SQLite event store in the same user's home, a hash list) is writable by seats. A deliberate seat can forge both the decision file and the record.
- **For now:** the alert is a tripwire for honest mistakes. Its description should say so, so a quiet alert isn't read as proof.
- **After step 3:** compare against a console-owned copy of each decision, by content, not by mtime.

**5. Impersonating the owner outside the console. (Medium; partly the Rig Architect's.)** R-005 covers the console API and decision files. The same goal ("a seat can't act as the owner") is also open through three routes the console touches:
- **(a) `rig send`:** any seat can send a lead the exact message `gates.decide()` sends ("The user decided gate … Read decisions/<id>.md"). The lead can't tell the difference.
- **(b) Agent text inside the owner's decision record:** `decide()` copies the gate's `question` (agent-written, up to 2,000 characters) verbatim into `decisions/<id>.md`, above "## Notes from the user". A seat can plant text that reads like your notes inside a genuine decision file.
- **(c) Seat-written routing:**
  - **Job name and rig:** `job.json` `name` and `rig` are seat-written. They decide which job a gate appears under, and which rig the console messages. A folder can claim another job's name, and `_jobs()` keeps the last one.
  - **Lead:** `gate.json` `lead` picks the seat that receives your decision.

  So a seat can present a gate as another team's, or route your decision message to another team's lead.
- **Suggested direction:**
  - **Decision files:** leads act only on the `.json` fields (`chosen`, `verdict`, `note`). The `.md` marks agent text as quoted ("from the gate, written by the team").
  - **Job name:** the job name is the folder name.
  - **Rig and lead:** taken from the operator's launch record, not the job folder.
  - **`rig send`:** the shared rules tell leads to treat a "user decided" message as a pointer to check, never as the decision itself.

  (b) and (c) are console code; (a) and the lead rule are cross-team, so they're also a note to the Rig Architect.

**6. R-006: three conditions to make explicit. (Medium.)**
- **Cookies ignore ports.** `rc_token` is sent to the play port too, and the two ports are *same-site*, so `SameSite=Lax` doesn't separate them. Isolation then rests on three things:
  - **(i) The play port serves only `/play/` static files.** No pages, no `/api/`, no login, no `?token=`.
  - **(ii) The main port stops serving `/play/`,** or redirects it. Otherwise old links keep the hole.
  - **(iii) Preflight keeps failing.** The custom header plus no CORS approval means a build's cross-origin POST can't pass preflight. `SimpleHTTPRequestHandler` has no `do_OPTIONS`, so preflight fails today. Lock that in with a smoke test, so a future OPTIONS handler or CORS header can't silently reopen it.
- **COOP/COEP stay on the play port.** Gate and Play links already open builds in a new tab with `noopener`, which is good.
- **`/data/` sandbox plus `nosniff` is right.** Also check that no other route serves agent-written HTML without `sandbox`.

**7. Phone push can be sent by seats. (Low to medium; not in the plan.)**
- **The risk:** `NTFY_TOPIC` sits in the same env file, so a seat can push a notification to your phone with any click URL, e.g. a fake "Decision needed" linking somewhere else.
- **Suggested direction:** move it with the token in step 3. Until then, a line in the shared rules that phone pushes come only from the console.

## Suggested order (the Platform Architect decides)
1. **R-006, plus the Host allowlist (finding 3).** Small, low risk, and it closes paths that need no stolen secret. The new Builds page makes builds the most-used agent content.
2. **Decision-record fixes (finding 5b, 5c)** and the step-1 tripwire, labelled as a tripwire.
3. **Decide interop and code location (findings 1, 2), then steps 2 and 3 together.** Step 2 without 3 adds little against seats.
4. **A threat-model PL entry first, naming who is in scope:**
   - seats, including prompt-injected ones;
   - builds;
   - web pages reached through seat browsers;
   - the operator (a no-sandbox Codex seat, technically equal to the owner today; is R-005 meant to constrain it?).

## Tests worth adding to the smoke test
- **CSRF guard:** a POST without `X-Rig-Console`, and one with a non-JSON content type, both get 403.
- **No preflight:** `OPTIONS /api/gate` doesn't succeed, and no response carries `Access-Control-Allow-*`.
- **Host allowlist:** a request with `Host: evil.example` is refused.
- **Play port:** it returns 404 for `/api/`, `/`, `/graph.html`; the main port doesn't serve `/play/`.
- **Decision record:** a gate `question` containing `## Notes from the user` lands quoted in the `.md`.
- **Job names:** two job folders claiming the same `name` are both rejected or flagged, not silently merged.

## What's already right
- **`safe_path`:** resolves symlinks and rejects escapes.
- **Gate URLs:** option `file`, `image` and `play` links are built by the server from checked paths, not taken from agent text.
- **Cross-site requests:** the CSRF header check plus no CORS is a sound base.
- **`/job/` responses:** sent with `sandbox` and `nosniff`.
- **Markdown renderers:** decide's and models' escape first and only allow https or in-app links. I tested a `model_note` event containing `<img onerror>`, `<script>` and a `javascript:` evidence link on the Models page: shown as text, nothing ran.

---

## Models page (PL-003): does it show its data correctly?
Tested by running `models.py` and `models.html` unchanged in a headless browser, against a copy of the current `models/`. The server and the event store were replaced by stand-ins.

**Correct:**
- **Totals:** 75 ledger lines, 38 seat-runs, 13 cards, 4 role assessments and the briefs table all load.
- **Seat grid:** all 13 cells' strength/failure counts match the ledger exactly (checked by script).
- **Seat-holder marks:** read from ROUTING correctly.
- **Evidence links:** map `jobs-mirror/<job>/…` and `research-mirror/<run>/…` to `/job/<name>/…`.
- **No errors** apart from the blocked web font (expected in the test sandbox).

**Problems, mostly on my side:**
1. **Seat-written lines look reviewed.** O071–O075 were written by the room-leads into `models/`. The page shows them like reviewed lines. I've now marked them in the ledger (`status`, `written_by`). It would help if the page showed any line with a `status` field.
2. **Two channels for leads' notes:**
   - **Files:** `model-notes.jsonl` files (SHARED-RULES §6, adopted in PD-015/AD-015, imported by `models/tools/harvest.py`);
   - **Events:** `model_note` events in `events.jsonl` (JOBS.md, shown on this page as "not yet reviewed").

   The page only sees the events. One channel should go, and the choice is the owner's. I'd keep the files: two architects have adopted them, and seats already write only in their own job folder. In that case the page can drop its "notes" block or read the harvested lines. Either way works for me; I can extend the harvester to read `model_note` events instead.
3. **Researcher row lacked the "in seat" mark** because ROUTING had no researcher row. Fixed in ROUTING.
4. **O055 combined two roles** in one line, which the grid can't place. Split into O055 and O076.
5. **Minor wording:** empty cells say "not tried" in the studio rows and "not run" in the research rows.
