# End-of-run model notes: format and harvest

Adopted for every team: Studio Architect AD-015, Rig Architect PD-015. **The canonical copy for seats is `briefs/SHARED-RULES.md` section 6**, which carries this format inline. If the two ever differ, section 6 wins. Changes go through the Rig Architect, and the harvester is then updated to match. Checked 2026-10-12: section 6 and `tools/harvest.py` agree field for field.

## What the lead writes, in its own job folder, at the end of a run

**`model-notes.jsonl`:** one JSON object per line, one line per notable seat behaviour:
```
{"date":"2026-10-20","seat":"build-b","model":"codex","version_if_known":"unknown",
 "role":"builder","brief":"lead-dispatch-x-14.md","brief_asked":"yes|no|partly|unclear",
 "what_happened":"Stopped after a red smoke test and reported the failing assertion.",
 "evidence":"protos/x-14/build-b-stop.md \"smoke: FAIL\"","kind":"strength|failure|quirk|cost|reliability","n":1}
```
- **Required fields:** `seat`, `model`, `role`, `brief`, `what_happened`, `evidence`, `kind`.
- **Paths:** `brief` and `evidence` paths are relative to the job folder.
- **What not to write:** no `id`, `attribution` or `confidence`. The Model Architect assigns those.
- **What to describe:** only what happened, with a file path or quote. No ranking of models.
- **`version_if_known`:** copy it from the seat's own screen or `rig ps` if shown; otherwise `unknown`.

**`model-metrics.csv`:** one row per seat, with this header:
```
seat,model,role,brief,outputs,survived_judging,send_backs,stops_real,stops_spurious,self_report_mismatches,capacity_errors,notes
```
Column meanings are in `README.md`. Leave a cell blank rather than guess. Use `unknown` when a count can't be reconstructed.

## How it is harvested
`python3 models/tools/harvest.py` (run by the Model Architect, from the repo root):
1. **Finds the files:** looks for `model-notes.jsonl` and `model-metrics.csv` in `jobs-mirror/*/` and `research-mirror/*/`. With `--live`, it reads `~/openrig/jobs/*/` and `~/openrig/research/*/` directly; the mirrors go stale. Ledger paths keep the mirror names, and the hash is the same either way.
2. **Validates and imports:**
   - validates each line;
   - adds `rig`, `id` and `harvested_from`;
   - sets `attribution: "unclear"` and `confidence: "observed"`;
   - appends to `observations.jsonl` and `metrics.csv`.
3. **Skips** anything already harvested, matched by a content hash, so re-running is safe.
   - **The hash** is stored on every harvested line as `harvest_hash`: `sha1(<job folder name> + "\x1f" + <the note line, whitespace-trimmed>)`, hex, first 16 characters.
   - **Stability:** it survives any rewording I do during review. It changes only if the lead edits the note itself, which then counts as a new note.
   - **A stable contract:** the Models page uses the same hash to tell harvested notes from new ones. `harvested_from` (`<mirror>/<job>/model-notes.jsonl:<line>`) is for display only; line numbers can shift.
4. **Reports** the invalid lines rather than importing them.

The Model Architect then reviews each new line, decides its attribution, and links it from the cards.
