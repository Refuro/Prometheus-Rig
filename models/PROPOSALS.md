# Proposals awaiting the owner's OK (nothing below has been applied)

Under ROLES.md these go through the owners: A is a request to the Platform Architect, B is input for the Studio Architect, C belongs to the Platform Architect. The short versions are in `LOG.md`, "Notes for ...".

## A. Models page in Rig Console

**Preview:** `models/preview/models-preview.html` is the real page with the real data inlined. Open it in a browser to try it.

**Changes (3 files in `dashboard/`, one restart of serve.py):**

1. **New `dashboard/models.html`:** a copy of `models/preview/models.html`. It reads `/api/models` and uses the same tokens, fonts and light/dark themes as play.html. Layout: one tab per model plus a "Roles & briefs" tab (role grades and the brief table). Each model tab shows the summary and an attribution bar (model / brief / unclear), role cards (one strength and one failure, a confidence chip, the full card on expand), a seat-run table, and filterable observations with evidence links through the existing `/job/<job>/<path>` route (sandboxed).
2. **`dashboard/nav.js`:** add `["/models.html", "Models"]` to `PAGES`.
3. **`dashboard/serve.py`:** one read-only route.

```python
# near the top, with the other paths
MODELS = os.path.join(DASH, "..", "models")

def load_models():
    import csv, glob, json
    cards = []
    for f in sorted(glob.glob(os.path.join(MODELS, "cards", "*.md"))):
        model, role = os.path.basename(f)[:-3].split("--", 1)
        cards.append({"file": "cards/" + os.path.basename(f), "model": model,
                      "role": role.replace("-", " "), "md": open(f, encoding="utf-8").read()})
    summaries = {m: open(p, encoding="utf-8").read() for m in {c["model"] for c in cards}
                 if os.path.exists(p := os.path.join(MODELS, m + ".md"))}
    obs = [json.loads(l) for l in open(os.path.join(MODELS, "observations.jsonl"), encoding="utf-8") if l.strip()]
    for o in obs:
        if o["model"] in ("gemma4:12b", "qwen3-coder:30b"): o["model"] = "gemma4-12b"
    metrics = list(csv.DictReader(open(os.path.join(MODELS, "metrics.csv"), encoding="utf-8")))
    roles = [{"file": "roles/" + os.path.basename(f), "role": os.path.basename(f)[:-3].replace("-", " "),
              "md": open(f, encoding="utf-8").read()} for f in sorted(glob.glob(os.path.join(MODELS, "roles", "*.md")))]
    bp = os.path.join(MODELS, "BRIEFS.md")
    briefs = open(bp, encoding="utf-8").read() if os.path.exists(bp) else ""
    return {"cards": cards, "summaries": summaries, "observations": obs, "metrics": metrics,
            "roles": roles, "briefs": briefs}

# in do_GET, beside the other /api/ routes
if path == "/api/models":
    return self.send_json(load_models())
```

Nothing writes. A missing file gives a JSON error through the existing `except` handler.

## B. Update loop: retro wording for `studio/rigs/*/brief.md`

Add this as the last bullet of the outputs list in pitch-room, depth-room and friend-room (after `retro.md`). proto-sprint, coop-proto and design-team have no retro section yet; add the same bullet to their outputs list.

> - **Model notes (end of run, lead only):** append one line per notable seat behaviour to `/mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/models/observations.jsonl` (format in `models/README.md`) and one row per seat to `metrics.csv` there. Name the brief or dispatch file the seat was working from, and say whether that brief asked for the behaviour. Only what you saw happen, each with a file path or quote. Write "seen once" when it was. Don't judge which model is better; the Model Architect does that.

## C. `.gitignore` (outside models; your call)

```
models/observations.jsonl
models/metrics.csv
models/preview/models-preview.html
```

The ledger quotes run outputs, which you already keep private (`studio/rigs/*/runs/`).
