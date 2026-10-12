#!/usr/bin/env python3
"""Compare local Ollama models on research-style agent tasks.
Usage (in Ubuntu):  python3 run_test.py gemma4:12b qwen3-coder:30b
Writes results/<model>.md and prints a summary table."""
import json, sys, time, urllib.request, pathlib, re

HOST = "http://localhost:11434"
HERE = pathlib.Path(__file__).resolve().parent
TASKS = json.loads((HERE / "tasks.json").read_text())
CTX = 16384  # roughly what an agent seat needs

def chat(model, prompt):
    body = json.dumps({"model": model, "stream": False,
                       "messages": [{"role": "user", "content": prompt}],
                       "options": {"num_ctx": CTX, "temperature": 0.2}}).encode()
    req = urllib.request.Request(HOST + "/api/chat", body, {"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        out = json.load(r)
    wall = time.time() - t0
    toks = out.get("eval_count", 0)
    tps = toks / (out.get("eval_duration", 1) / 1e9) if out.get("eval_duration") else 0
    return out["message"]["content"], wall, tps

def strict_json(text):
    try:
        json.loads(text.strip()); return "pass"
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, re.S)
    try:
        if m: json.loads(m.group(0)); return "loose (extra text around JSON)"
    except Exception:
        pass
    return "FAIL"

def main(models):
    rows = []
    for model in models:
        print(f"\n=== {model} (first call includes load time) ===", flush=True)
        lines = [f"# {model}\n", f"num_ctx={CTX}\n"]
        for t in TASKS:
            text, wall, tps = chat(model, t["prompt"])
            fmt = strict_json(text) if t["kind"] == "json" else "-"
            print(f"{t['id']:9} {wall:6.1f}s  {tps:5.1f} tok/s  json: {fmt}", flush=True)
            rows.append((model, t["id"], wall, tps, fmt))
            lines += [f"\n## {t['id']}  ({wall:.1f}s, {tps:.1f} tok/s, json: {fmt})\n\n", text, "\n"]
        safe = model.replace(":", "_").replace("/", "_")
        (HERE / "results" / f"{safe}.md").write_text("".join(lines))
    print("\nSaved to model-test/results/. Now run 'ollama ps' in PowerShell and paste both outputs to Claude.")

if __name__ == "__main__":
    main(sys.argv[1:] or ["gemma4:12b", "qwen3-coder:30b"])
