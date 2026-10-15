#!/usr/bin/env python3
"""Harvest end-of-run model notes from job folders into models/ (see models/HARVEST.md).

Usage, from the repo root:  python3 models/tools/harvest.py [--dry-run] [--live]
Reads jobs-mirror/*/ and research-mirror/*/ for model-notes.jsonl and model-metrics.csv.
--live reads ~/openrig/jobs/*/ and ~/openrig/research/*/ instead (for a seat running in WSL; the mirrors
go stale). Override the base with RIG_OPENRIG_HOME. Paths in the ledger keep the mirror names, so the
Models page's evidence links still work, and harvest_hash is the same either way (it uses only the job name).
Appends new, valid entries to models/observations.jsonl and models/metrics.csv. Safe to re-run.
"""
import csv, glob, hashlib, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS = os.path.join(ROOT, 'models')
OBS = os.path.join(MODELS, 'observations.jsonl')
MET = os.path.join(MODELS, 'metrics.csv')
REQUIRED = ('seat', 'model', 'role', 'brief', 'what_happened', 'evidence', 'kind')
KINDS = {'strength', 'failure', 'quirk', 'cost', 'reliability'}
MET_IN = ['seat', 'model', 'role', 'brief', 'outputs', 'survived_judging', 'send_backs', 'stops_real',
          'stops_spurious', 'self_report_mismatches', 'capacity_errors', 'notes']


def h(*parts):
    return hashlib.sha1('\x1f'.join(parts).encode('utf-8')).hexdigest()[:16]


def job_dirs(live=False):
    base = os.path.expanduser(os.environ.get('RIG_OPENRIG_HOME', '~/openrig'))
    for mirror, real in (('jobs-mirror', 'jobs'), ('research-mirror', 'research')):
        root = os.path.join(base, real) if live else os.path.join(ROOT, mirror)
        for d in sorted(glob.glob(os.path.join(root, '*'))):
            if os.path.isdir(d):
                yield mirror, os.path.basename(d), d


def main(dry, live=False):
    obs = [json.loads(l) for l in open(OBS, encoding='utf-8') if l.strip()] if os.path.exists(OBS) else []
    seen = {o.get('harvest_hash') for o in obs}
    nums = [int(o['id'][1:]) for o in obs if str(o.get('id', '')).startswith('O') and o['id'][1:].isdigit()]
    next_id = max(nums, default=0) + 1
    met_rows = list(csv.DictReader(open(MET, encoding='utf-8'))) if os.path.exists(MET) else []
    met_cols = list(met_rows[0].keys()) if met_rows else []
    for c in ('harvest_hash',):
        if c not in met_cols: met_cols.append(c)
    met_seen = {r.get('harvest_hash') for r in met_rows}
    new_obs, new_met, problems = [], [], []

    for mirror, rig, d in job_dirs(live):
      # The job folder itself, plus seats' own folders one or two levels down (e.g. a lab game's clerk/ and
      # powers/<nation>/). The hash still uses only the job name and the line, so it's unchanged (MA-024).
      for notes in [os.path.join(d, 'model-notes.jsonl')] + sorted(glob.glob(os.path.join(d, '*', 'model-notes.jsonl'))) \
              + sorted(glob.glob(os.path.join(d, '*', '*', 'model-notes.jsonl'))):
        sub = os.path.relpath(os.path.dirname(notes), d)
        sub = '' if sub == '.' else sub + '/'
        if os.path.exists(notes):
            for n, line in enumerate(open(notes, encoding='utf-8'), 1):
                if not line.strip(): continue
                where = f'{mirror}/{rig}/{sub}model-notes.jsonl:{n}'
                try:
                    e = json.loads(line)
                except ValueError as ex:
                    problems.append(f'{where}: not JSON ({ex})'); continue
                missing = [k for k in REQUIRED if not str(e.get(k, '')).strip()]
                if missing:
                    problems.append(f'{where}: missing {", ".join(missing)}'); continue
                if e['kind'] not in KINDS:
                    problems.append(f'{where}: kind "{e["kind"]}" not in {sorted(KINDS)}'); continue
                key = h(rig, line.strip())
                if key in seen: continue
                seen.add(key)
                rec = {'id': f'O{next_id:03d}', 'date': e.get('date', ''), 'model': e['model'],
                       'version_if_known': e.get('version_if_known', 'unknown'), 'runtime': e.get('runtime', ''),
                       'seat': e['seat'], 'role': e['role'], 'rig': rig,
                       'brief': f'{mirror}/{rig}/{e["brief"]}', 'brief_date': e.get('brief_date', ''),
                       'brief_asked': e.get('brief_asked', 'unclear'), 'attribution': 'unclear',
                       'what_happened': e['what_happened'], 'evidence': f'{mirror}/{rig}/{e["evidence"]}',
                       'kind': e['kind'], 'confidence': 'observed', 'n': int(e.get('n', 1) or 1),
                       'harvested_from': where, 'harvest_hash': key, 'status': 'harvested: needs review'}
                next_id += 1
                new_obs.append(rec)
      for mfile in [os.path.join(d, 'model-metrics.csv')] + sorted(glob.glob(os.path.join(d, '*', 'model-metrics.csv'))) \
              + sorted(glob.glob(os.path.join(d, '*', '*', 'model-metrics.csv'))):
        sub = os.path.relpath(os.path.dirname(mfile), d)
        sub = '' if sub == '.' else sub + '/'
        if os.path.exists(mfile):
            for n, r in enumerate(csv.DictReader(open(mfile, encoding='utf-8')), 2):
                where = f'{mirror}/{rig}/{sub}model-metrics.csv:{n}'
                if not (r.get('seat') and r.get('model')):
                    problems.append(f'{where}: missing seat or model'); continue
                key = h(rig, json.dumps(r, sort_keys=True))
                if key in met_seen: continue
                met_seen.add(key)
                row = {c: '' for c in met_cols}
                row.update({k: r.get(k, '') for k in MET_IN if k in met_cols})
                row.update({'rig': rig, 'date': r.get('date', ''), 'runtime': r.get('runtime', ''),
                            'harvest_hash': key})
                new_met.append(row)

    print(f'new observations: {len(new_obs)}, new metric rows: {len(new_met)}, problems: {len(problems)}')
    for p in problems: print('  PROBLEM', p)
    for r in new_obs: print('  +', r['id'], r['rig'], r['seat'], r['kind'], '-', r['what_happened'][:70])
    if dry or not (new_obs or new_met):
        return 1 if problems else 0
    with open(OBS, 'a', encoding='utf-8') as f:
        for r in new_obs: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    if new_met:
        with open(MET, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=met_cols); w.writeheader(); w.writerows(met_rows + new_met)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main('--dry-run' in sys.argv, '--live' in sys.argv))
