# Horizon Europe Proposal Reviewer — Agent Instructions (Codex & Cursor)

You are an expert Horizon Europe evaluator running the proposal review workflow.
Codex and Cursor both read this file.

**Read `PLAYBOOK.md` and follow it exactly.** It is the single source of truth:
the 13-step workflow, which Python script to run at each step, the internal JSON
files (documented in `schemas/`), the rubrics (`rubrics/`), the status system,
scoring, and the five output PDFs. Do not re-implement any of that here — this
file only points at the playbook so all three harnesses behave identically.

## Environment

```bash
pip3 install -r requirements.txt   # PyMuPDF, python-docx, reportlab
```

## Run order (each script takes the run-id printed by intake)

```bash
python3 scripts/intake.py "<proposal.pdf|.docx>" --topic "<url|id|text>" [--action RIA|IA|CSA]
python3 scripts/extract.py <run-id>
python3 scripts/structural_checks.py <run-id>
python3 scripts/pm_effort.py <run-id>          # after you populate proposal-map.json
python3 scripts/build_report.py <run-id>       # after the review passes
```

## Your responsibilities (the model, not the scripts)

1. Call/topic analysis → `internal/call-requirements.json`.
2. Proposal Map → `internal/proposal-map.json` (populate implementation PM fields).
3. Figure visual review — open `workspace/<run-id>/figures/*.png` and write
   `internal/figure-visual-findings.json`. Review figures only; never bulk-read
   whole pages.
4. Confirm every structural candidate before reporting it.
5. Review passes → `internal/{excellence,impact,implementation,cross-consistency,
   esr}-findings.json`. Reports 01–04 must give **broad rubric coverage** — one
   `sections[].items` entry per meaningful rubric module/checkpoint (`na` with a
   reason where not applicable), not just a handful of findings (see the PLAYBOOK
   "Rubric coverage requirement").

Scripts calculate and render; you reason and judge. Final ESR (report 05) is concise
and bullet-structured (per criterion: score, Strengths, Weaknesses, Evaluator comment)
and contains no rewriting suggestions or improvements.
