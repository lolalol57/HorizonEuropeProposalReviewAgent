---
description: Review a Horizon Europe proposal and produce the 5 ESR-style PDF reports
argument-hint: [proposal.pdf|.docx] [topic-url|topic-id|"topic text"] [RIA|IA|CSA]
---

Run the Horizon Europe proposal review (the `he-proposal-review` skill / `PLAYBOOK.md`).

Arguments: `$ARGUMENTS`
- 1st = path to the proposal (.pdf or .docx). **Optional** — if omitted, the newest file
  in `./inbox/` is used.
- 2nd = official topic URL, topic id, or topic text — strongly recommended (drives the
  Call Requirements Map). Ask the user if not provided.
- 3rd = Type of Action (RIA / IA / CSA / Other) — optional (inferred from the topic if
  omitted).

If the `he-review` CLI is not on PATH (e.g. a project-local or `npx` install), run the
bundled scripts directly instead: `python3 <this skill dir>/scripts/<intake|extract|
structural_checks|pm_effort|build_report>.py …` — the same arguments apply.

Then follow the `he-proposal-review` skill and `PLAYBOOK.md` end to end:

1. `he-review intake "<proposal-or-empty>" --topic "<topic>" [--action <ToA>]` → capture the
   printed `run_id`.
2. Analyse the call/topic → write `internal/call-requirements.json`.
3. `he-review extract <run-id>` then `he-review structural <run-id>`.
4. Open `he-review-workspace/<run-id>/figures/*.png`, review the figures, and write
   `internal/figure-visual-findings.json` (figures only — never bulk pages).
5. Build `internal/proposal-map.json` (populate implementation PM fields), then
   `he-review pm <run-id>`.
6. Run the five passes (Excellence → Impact → Implementation → Cross-Consistency → ESR)
   using the rubrics, writing each `internal/*-findings.json`. Confirm every structural
   candidate first. Reports 01–04 must give **broad rubric coverage** — one
   `sections[].items` entry per meaningful rubric module/checkpoint (`na` with a reason
   where not applicable), not just a handful of findings. The ESR (05) stays concise and
   bullet-structured (score, Strengths, Weaknesses, Evaluator comment; no improvements).
7. `he-review report <run-id>` (or `python3 scripts/build_report.py <run-id>`).
8. Map the completed review onto the fixed 235-checkpoint checklist → write
   `internal/checklist-fill.json` (per checkpoint: `status`, `citation` = the finding's
   evidence quote/ref, `note`), then `python3 scripts/build_checklist.py <run-id>` →
   `OUTPUT/06_Proposal_Preparation_Checklist.xlsx`.

Finally, report the five PDFs **and the filled checklist** in
`he-review-workspace/<run-id>/OUTPUT/` and a short scores summary.
