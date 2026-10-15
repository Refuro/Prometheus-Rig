#!/usr/bin/env python3
"""E2 results: compare two critics' scores.jsonl files against each other, the rubric and the answer key.

    python3 tools/compare.py [job folder] [--key path/to/key.json]   # writes results.md

Reads out/claude/scores.jsonl and out/codex/scores.jsonl (a later line for the same id with
"correction": true replaces the earlier one). Reports, per critic and per criterion: score spread and
self-conflicts (a score of 4-5 with its own paired "no", or 1-2 with both its own paired answers "yes").
With --key (MA-035 K1), it also grades each critic against the frozen key, the same way for both: rubric
answer accuracy per question, and key conflicts (the same score rule, with the key's answers). Between the
critics: exact score agreement, mean absolute difference, rubric answer agreement, bottom-third overlap.
"insufficient" (R4 and R5 only; K2 as sharpened in MA-036) is listed and left out of agreement rates. Missing or malformed lines
are listed, not guessed.

Key format: {"x-01": {"R1": {"answer": "yes", "line": "quoted card text"}, ...}, ...}. A key cell may carry
"disputed": true (a reviewer proposed another answer that the drafter didn't accept); those cells are listed, and
graded as the key says. A question whose key answer is the same on every card is flagged as a constant: agreement
with it measures only how often a critic gives that one answer.
"""
import json, pathlib, statistics, sys

CRITICS = ("claude", "codex")
IDS = [f"x-{n:02d}" for n in range(1, 25)]
RS = ("R1", "R2", "R3", "R4", "R5", "R6")
PAIRS = {"exploit_proof": ("R1", "R2"), "depth": ("R3", "R4"), "clarity": ("R5", "R6")}
JUDGED = ("R4", "R5")
key_meta = {"disputed": []}


def valid_answer(r, a):
    return a in ("yes", "no") or (r in JUDGED and a == "insufficient")


def load(job, who):
    path = job / "out" / who / "scores.jsonl"
    rows, problems = {}, []
    if not path.exists():
        return rows, [f"{who}: no scores.jsonl"]
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            cid = row["id"]
            for k in PAIRS:
                if row[k] not in (1, 2, 3, 4, 5):
                    raise ValueError(f"{k}={row[k]!r}")
            for r in RS:
                if not valid_answer(r, row["rubric"][r]["answer"]):
                    raise ValueError(f"{r} answer {row['rubric'][r]['answer']!r}")
        except (ValueError, KeyError, TypeError) as e:
            problems.append(f"{who} line {n}: {e}")
            continue
        if cid in rows and not row.get("correction"):
            problems.append(f"{who} line {n}: duplicate {cid} without correction (kept the first)")
            continue
        rows[cid] = row
    problems += [f"{who}: missing {i}" for i in IDS if i not in rows]
    return rows, problems


def load_key(path):
    key, problems = {}, []
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    disputed = [f"{c} {r}" for c in IDS for r in RS if isinstance(data.get(c), dict)
                and isinstance(data[c].get(r), dict) and data[c][r].get("disputed")]
    key_meta["disputed"] = disputed
    for cid in IDS:
        try:
            ans = {r: data[cid][r]["answer"] for r in RS}
            for r, a in ans.items():
                if not valid_answer(r, a):
                    raise ValueError(f"{r} answer {a!r}")
            key[cid] = ans
        except (ValueError, KeyError, TypeError) as e:
            problems.append(f"key {cid}: {e}")
    return key, problems


def bottom(job, who):
    path = job / "out" / who / "bottom-third.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return [i for i in IDS if i in text]


def conflict(score, a, b):
    """None when an answer is insufficient (not counted)."""
    if "insufficient" in (a, b):
        return None
    return (score >= 4 and "no" in (a, b)) or (score <= 2 and a == b == "yes")


def own_answers(row, crit):
    return tuple(row["rubric"][r]["answer"] for r in PAIRS[crit])


def main():
    args = sys.argv[1:]
    key_path = None
    if "--key" in args:
        i = args.index("--key")
        key_path = args[i + 1]
        del args[i:i + 2]
    job = pathlib.Path(args[0] if args else ".").resolve()
    data, problems = {}, []
    for who in CRITICS:
        data[who], p = load(job, who)
        problems += p
    key = {}
    if key_path:
        key, p = load_key(key_path)
        problems += p
    out = ["# E2 results", "", f"Job: `{job}`. Cards scored: "
           + ", ".join(f"{w} {len(data[w])}/24" for w in CRITICS)
           + (f". Key: `{key_path}` ({len(key)}/24 cards)." if key_path else ". No key given."), ""]

    out += ["## Each critic against its own rubric answers (self-consistency)", "",
            "| Critic | Criterion | Mean | Stdev | Counts 1-5 | Self-conflicts |", "|---|---|---|---|---|---|"]
    for who in CRITICS:
        rows = list(data[who].values())
        for crit in PAIRS:
            vals = [r[crit] for r in rows]
            if not vals:
                continue
            counts = "/".join(str(vals.count(v)) for v in range(1, 6))
            sd = statistics.pstdev(vals) if len(vals) > 1 else 0.0
            conf = [r["id"] for r in rows if conflict(r[crit], *own_answers(r, crit))]
            out.append(f"| {who} | {crit} | {statistics.mean(vals):.2f} | {sd:.2f} | {counts} | "
                       f"{len(conf)}{': ' + ', '.join(conf) if conf else ''} |")

    if key:
        out += ["", "## Each critic against the key", "",
                "Rubric accuracy counts cards where both the key and the critic gave yes or no.", "",
                "| Critic | " + " | ".join(RS) + " |", "|---|" + "---|" * len(RS)]
        for who in CRITICS:
            cells = []
            for r in RS:
                ids = [i for i in IDS if i in data[who] and i in key
                       and "insufficient" not in (key[i][r], data[who][i]["rubric"][r]["answer"])]
                right = sum(data[who][i]["rubric"][r]["answer"] == key[i][r] for i in ids)
                cells.append(f"{right}/{len(ids)}")
            out.append(f"| {who} | " + " | ".join(cells) + " |")
        out += ["", "| Critic | Criterion | Key conflicts |", "|---|---|---|"]
        for who in CRITICS:
            for crit in PAIRS:
                conf = [i for i in IDS if i in data[who] and i in key
                        and conflict(data[who][i][crit], *(key[i][r] for r in PAIRS[crit]))]
                out.append(f"| {who} | {crit} | {len(conf)}{': ' + ', '.join(conf) if conf else ''} |")
        ins = [f"{i} {r}" for i in IDS if i in key for r in JUDGED if key[i][r] == "insufficient"]
        out += ["", "Key marks insufficient (left out): " + (", ".join(ins) or "none")]
        const = [f"{r} (all {next(iter(key.values()))[r]})" for r in RS
                 if len({key[i][r] for i in key}) == 1]
        out.append("Constant key answers (agreement there only measures how often a critic gives that answer): "
                   + (", ".join(const) or "none"))
        out.append("Disputed key cells (graded as the key says): " + (", ".join(key_meta["disputed"]) or "none"))

    for who in CRITICS:
        ins = [f"{i} {r}" for i in IDS if i in data[who] for r in JUDGED
               if data[who][i]["rubric"][r]["answer"] == "insufficient"]
        out.append(f"{who} marks insufficient (left out): " + (", ".join(ins) or "none"))

    both = [i for i in IDS if all(i in data[w] for w in CRITICS)]
    out += ["", f"## Between the critics ({len(both)} cards scored by both)", ""]
    if both:
        out += ["| Criterion | Exact agreement | Mean abs. difference |", "|---|---|---|"]
        for crit in PAIRS:
            diffs = [abs(data["claude"][i][crit] - data["codex"][i][crit]) for i in both]
            out.append(f"| {crit} | {diffs.count(0)}/{len(both)} | {statistics.mean(diffs):.2f} |")
        agree = []
        for r in RS:
            ids = [i for i in both if "insufficient" not in
                   (data["claude"][i]["rubric"][r]["answer"], data["codex"][i]["rubric"][r]["answer"])]
            n = sum(data["claude"][i]["rubric"][r]["answer"] == data["codex"][i]["rubric"][r]["answer"]
                    for i in ids)
            agree.append(f"{r} {n}/{len(ids)}")
        out += ["", "Rubric answer agreement: " + ", ".join(agree)]
    b = {w: bottom(job, w) for w in CRITICS}
    shared = sorted(set(b["claude"]) & set(b["codex"]))
    out += ["", f"Bottom third: claude {len(b['claude'])} named, codex {len(b['codex'])} named, "
            f"{len(shared)} in both" + (f" ({', '.join(shared)})" if shared else ""), ""]

    out += ["## Problems", ""] + ([f"- {p}" for p in problems] or ["- none"])
    out += ["", "One run is not decision-grade: report results as consistent or not consistent with a model "
            "difference (models/EXPERIMENTS.md)."]
    (job / "results.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
