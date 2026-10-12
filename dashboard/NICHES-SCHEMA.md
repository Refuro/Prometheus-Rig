# niches.json: the research team's live tracker

The lead keeps `~/openrig/research/run-1/niches.json` up to date. Write it
whenever a niche is added, scored, cut, or advanced, and whenever the phase
changes. Always write the complete file (write to a temp file, then rename).

```json
{
  "run": "run-1",
  "updated": "2026-10-11T15:30:00-07:00",
  "phase": "longlist",
  "phase_note": "Analysts gathering candidates",
  "niches": [
    {
      "id": "n01",
      "name": "Utility bill splitting for small landlords",
      "one_line": "Landlords with 2-10 units split utilities by spreadsheet.",
      "stage": "longlist",
      "scores": {"spending": 3, "gap": 4, "pain": 3, "reach": 4, "build": 5, "economics": 2},
      "total": 21,
      "reason": "Why it advanced or was cut, one sentence.",
      "skeptic": "Strongest objection, one line (empty until the skeptic weighs in).",
      "evidence": ["https://example.com/thread"],
      "owner": "analyst-pain",
      "updated": "2026-10-11T15:30:00-07:00"
    }
  ]
}
```

- `targets` (optional): `{"longlist": 15, "screened": 5, "shortlist": 2}`, the funnel sizes from your brief.
- `funnel` (optional): `{"screened": 8, "deep_dive": 2}`, the peak count each stage reached. Cuts later
  in the run don't lower these. The dashboard also tracks peaks itself.
- `phase`: one of `longlist`, `screen`, `checkpoint`, `deep-dive`, `shortlist`, `done`.
- `stage`: one of `longlist`, `screened` (in the top 8), `cut`, `shortlisted`, `finalist`.
- `scores`: 1-5 per criterion from brief section 2; leave out criteria not scored yet.
- `total`: sum of the scores present.
- `evidence`: real links only, never invented.
