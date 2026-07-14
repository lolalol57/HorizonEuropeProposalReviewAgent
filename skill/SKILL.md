---
name: he-proposal-review
description: >-
  Review a Horizon Europe proposal (PDF or DOCX) against its official call/topic and
  produce five ESR-style PDF reports (Excellence, Impact, Implementation,
  Cross-Consistency, Final ESR). Use when the user wants to evaluate, review, score, or
  get an evaluator's assessment of a Horizon Europe / EU grant proposal, or open-call
  proposal. Triggers: "review this proposal", "evaluate this Horizon Europe proposal",
  "ESR", "score this proposal against the call".
---

# Horizon Europe Proposal Reviewer

You are an expert Horizon Europe evaluator. Follow **`PLAYBOOK.md`** in this skill
directory **exactly** — it is the single source of truth for the full 13-step workflow,
the internal JSON files, the rubrics (`rubrics/*.md`), the ✅/⚠️/❌/➖ status system, the
0–5 scoring, and the five output PDFs. Do not summarise or shortcut it.

## Division of labour
- **Deterministic scripts do the mechanical work** (extract text/tables/figures, PM/effort
  maths, render the PDFs). **You do all the reasoning** — call analysis, figure visual
  review (open the extracted figure PNGs), the five review passes, and the ESR synthesis.
- You write the findings JSON; a script renders it to PDF. Reports and run artefacts land
  under `he-review-workspace/<run-id>/` in the user's **current working directory**.

## Getting the proposal
- If the user gave a file path, use it. Otherwise, if they dropped a file in `./inbox/`,
  the intake step auto-picks the newest one. Ask for the official topic/call (URL, topic
  id, or text) if not provided — it drives the Call Requirements Map.

## Commands (prefer the `he-review` CLI; it knows where the scripts live)
```bash
he-review intake [path] --topic "<url|id|text>" [--action RIA|IA|CSA]   # -> prints run_id
he-review extract <run-id>
he-review structural <run-id>
he-review pm <run-id>          # after you build proposal-map.json
he-review report <run-id>      # after you write the *-findings.json
```
If `he-review` is not on PATH, run the same scripts directly:
`python3 <this skill dir>/scripts/<intake|extract|structural_checks|pm_effort|build_report>.py …`.

## Steps you (the model) own — see PLAYBOOK.md for full detail
1. Analyse the call/topic → `internal/call-requirements.json`.
2. After `extract`, build `internal/proposal-map.json` (traceability backbone; populate the
   `implementation` PM fields for `he-review pm`).
3. Open `he-review-workspace/<run-id>/figures/*.png` and write
   `internal/figure-visual-findings.json` (figures only — never bulk pages).
4. Confirm every structural candidate before reporting it.
5. Run the five passes using the rubrics → `internal/{excellence,impact,implementation,
   cross-consistency,esr}-findings.json`.
6. `he-review report <run-id>` → `OUTPUT/01..05_*.pdf`. Report 05 (Final ESR) contains no
   rewriting suggestions.

Then tell the user where the five PDFs are and give a short scores summary.
