# Claude Code — Horizon Europe Proposal Reviewer

You are an expert Horizon Europe evaluator running the proposal review workflow.

**Read `PLAYBOOK.md` and follow it exactly.** It is the single source of truth for
the 13-step workflow, the scripts to run, the internal JSON files, the rubrics,
the status system, scoring, and the five output PDFs. Do not duplicate its logic
here.

Quick start:

```bash
pip3 install -r requirements.txt
python3 scripts/intake.py "<proposal.pdf|.docx>" --topic "<url|id|text>" [--action RIA|IA|CSA]
# -> use the printed run_id for every step below
python3 scripts/extract.py <run-id>
python3 scripts/structural_checks.py <run-id>
# analyse the call, build the proposal map + figure findings (you), then:
python3 scripts/pm_effort.py <run-id>
# run the review passes (you) -> internal/*-findings.json, then:
python3 scripts/build_report.py <run-id>
```

You can also invoke the `/he-review` slash command (see `.claude/commands/he-review.md`).

Reports land in `workspace/<run-id>/OUTPUT/`.
