# Horizon Europe Proposal Review — PLAYBOOK

**This file is the single source of truth.** Claude Code, Codex, and Cursor all
run the *same* workflow by reading this file. Do not duplicate logic elsewhere —
the per-harness files (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/review.mdc`) only
point here.

You are an **expert Horizon Europe evaluator**. You review a proposal against its
official call/topic in a structured, evidence-based, evaluator-oriented way and
produce five PDF reports. Evaluate the proposal **as submitted**.

## Division of labour (read this first)

- **Deterministic Python scripts** find *what exists and where*, do the exact
  Person-Month maths, and render the final PDFs. They never judge quality.
- **You (the host model)** do all reasoning: call analysis, the proposal map,
  figure visual review, confirming structural candidates, the five review passes,
  and ESR synthesis. You write **findings JSON**; a script renders it to PDF.

```
EXTRACTION        -> what figure/table/section exists and where
CLAUDE VISION     -> can the figure be read and understood
DETERMINISTIC     -> exact PM and WP effort values
RUBRICS           -> what must be reviewed
MAIN REVIEW       -> proposal quality, per criterion
CROSS-CONSISTENCY -> is the proposal internally coherent + covers the call
ESR SYNTHESIS     -> validated findings -> final evaluator comments
```

First version is a **single main workflow** — no subagents.

## Setup

```bash
pip3 install -r requirements.txt   # PyMuPDF, python-docx, reportlab
```

All per-run artefacts live under `workspace/<run-id>/`:
`inputs/ internal/ figures/ pages/ OUTPUT/`. Every script takes the `run-id` as
its argument. Internal JSON files are described in `schemas/`.

---

## The 13 steps

### 1 — Proposal Intake  *(script)*
```bash
python3 scripts/intake.py "<proposal.pdf|.docx>" [--topic "<url|id|text>"] [--action RIA|IA|CSA|Other]
```
Prints `run_id=...` on the last line. Use that run-id for every later step.
Required inputs: the proposal + at least one of {topic URL, topic id, topic text,
call document}. Optional: Part A, budget docs, previous ESR, template, reference
proposal, internal quality rules — accept these if provided and use them as
supporting evidence.

### 2 — Call / Topic Context Analysis  *(you)*
Read the official topic/call. Write the **Call Requirements Map** to
`internal/call-requirements.json` (schema: `call-requirements.schema.json`):
call/topic id, title, Type of Action, Scope, Expected Outcomes, Expected Impacts,
Specific Requirements, required stakeholders/disciplines, SSH, cross-border, TRL
expectations, other conditions. If Type of Action was not given, infer it here.
This map is used throughout — especially Impact and Cross-Consistency.

### 3 — Document Extraction  *(script)*
```bash
python3 scripts/extract.py <run-id>
```
Writes `internal/document.json` (page text + headings + full_text),
`internal/table-map.json`, `internal/figure-map.json`, and figure PNGs in
`figures/`. Extraction determines *what exists and where* — it does not judge.

### 4 — Structural + Lightweight Checks  *(script)*
```bash
python3 scripts/structural_checks.py <run-id>
```
Writes `internal/structural-candidates.json`. **Every item is a CANDIDATE**
(`POTENTIAL ISSUE — REVIEW REQUIRED`). You must confirm each against the actual
document before it may appear in any report. Do not report unconfirmed candidates.

### 5 — Figure Extraction  *(script, part of step 3)*
Already produced by `extract.py`: raster figures in `figures/figure_NN.png` plus
`figure-map.json`. Vector figures with no raster image appear under
`unmatched_captions` — render their page only if you need to review them:
`python3 -c "import sys; sys.path.insert(0,'scripts'); import extract; print(extract.render_page('<run-id>', <page>))"`.

### 6 — Figure Visual Review (host vision)  *(you)*
Open the extracted figure PNGs (`workspace/<run-id>/figures/*.png`) and review
**only figures** — never bulk-send proposal pages. Relevant types:
project-at-a-glance, overall concept, system/solution architecture, methodology,
workflow, data-flow, key-technology/innovation diagram, validation setting, use
case, impact pathway, PERT/Gantt. Assess **Readability** (labels, text size,
arrows/direction, resolution, pixelation, cropping, overcrowding, contrast,
legend), **Understandability** (purpose, hierarchy, reading direction,
inputs/outputs, layers, relationships, arrow meaning, overall message), and
**Content Consistency** with the text (key technology/innovation/objective names,
architecture/methodology/validation relationships). Write
`internal/figure-visual-findings.json` (schema: `figure-visual-findings.schema.json`).

### 7 — Build the Proposal Map + PM data  *(you, then script)*
From the extracted content build `internal/proposal-map.json` (schema:
`proposal-map.schema.json`) — the traceability backbone:
`Problem → Gap → Objective → KPI → Baseline → Target → Key R&I Development /
Key Innovation → Key Technology → WP → Task → Validation → Result → Outcome →
Impact`. Populate `implementation.partners[].pm`, `work_packages[].pm`,
`work_packages[].is_management`, and `declared_total_pm` from the effort tables.
Then run the deterministic maths:
```bash
python3 scripts/pm_effort.py <run-id> [--pm-threshold 7.0]
```
Writes `internal/pm-effort-analysis.json`: partner/WP/declared PM reconciliation,
per-WP effort %, and the **Project-Management effort %** vs an
**INTERNAL PROPOSAL QUALITY HEURISTIC** (default ≤7% — *not* an official HE rule).
The script calculates and flags; you interpret.

### 8 — Excellence Review  *(you)* → `internal/excellence-findings.json`
Load `rubrics/EXCELLENCE_REVIEW.md` and work through every module. Inputs: Call
Requirements Map, Proposal Map, Excellence rubric, relevant figure visual
findings, relevant structural findings. Produce findings JSON (schema:
`proposal-findings.schema.json`) + a draft Excellence score.

### 9 — Impact Review  *(you)* → `internal/impact-findings.json`
Load `rubrics/IMPACT_REVIEW.md`. Inputs: Call Requirements Map, Proposal Map,
Impact rubric, relevant figure findings, relevant structural findings.

### 10 — Implementation Review  *(you)* → `internal/implementation-findings.json`
Load `rubrics/IMPLEMENTATION_REVIEW.md`. Inputs: Proposal Map, Implementation
rubric, **PM/effort analysis**, WP effort %, relevant structural findings.

### 11 — Cross-Consistency & Call Coverage  *(you)* → `internal/cross-consistency-findings.json`
Load `rubrics/CROSS_CONSISTENCY_REVIEW.md`. Check the whole proposal along the
traceability chain (Problem → … → Impact). Identify: broken traceability,
inconsistent numbers/names, contradictory TRLs, objectives without implementation
pathways, KPIs without validation, innovations without enabling technologies,
technologies without R&I purpose, results claimed in Impact but not generated,
and topic requirements not adequately covered. Include coverage matrices
(Expected Outcome coverage, Expected Impact coverage) as `matrices` (each:
`{title, headers, rows}`) and confirmed inconsistencies as `inconsistencies`.

### 12 — Final ESR Synthesis  *(you)* → `internal/esr-findings.json`
Load `rubrics/ESR_WRITING_RULES.md`. Consolidate validated findings, remove
duplicates, prevent double-penalisation, ensure score↔comment consistency.
Produce `{criteria:[{name, comment, score}], total_score, overall}`. The ESR
evaluates the proposal **as submitted** and contains **no rewriting suggestions
or replacement text**.

### 13 — PDF Report Generation  *(script)*
```bash
python3 scripts/build_report.py <run-id>          # all available reports
python3 scripts/build_report.py <run-id> --only 01,05
```
Renders `OUTPUT/01..05_*.pdf`. A report whose findings JSON is missing is skipped.

---

## Status system (used in every findings item)

| JSON `status` | Meaning | PDF |
|---------------|---------|-----|
| `adequate` | Adequately addressed | ✅ |
| `partial`  | Partially addressed (info incomplete/unclear/inconsistent) | ⚠️ |
| `missing`  | Not adequately addressed / missing | ❌ |
| `na`       | Not applicable | ➖ |

For every `partial`/`missing` item give **Evidence** (short quote or precise
section/page/table/figure ref), **Reviewer Assessment** (what is wrong + why it
matters for the criterion), and, in the Internal Improvement Report only,
**Suggested Improvement**.

## Scoring

- One official score per criterion, `0.0–5.0` in `0.5` steps. Internal item
  statuses are diagnostic only — never score individual items.
- `5` excellent (only minor shortcomings) · `4` very good · `3` good (several
  shortcomings) · `2` significant weaknesses · `1` serious weaknesses ·
  `0` fails/unassessable.
- Total `/15.0`. Before finalising: does the written assessment justify the
  score? Are important weaknesses reflected? Has any weakness been penalised
  twice? (Score–comment consistency gate.)

## Output responsibilities (spec §18–19)

- `01_Excellence_Review.pdf` — detailed Excellence findings, objectives/KPIs/key
  technologies/methodology, relevant figure findings, strengths, shortcomings,
  improvements, draft score.
- `02_Impact_Review.pdf` — outcomes, wider impact, pathway to impact,
  dissemination/exploitation/communication, KERs, figure findings, score.
- `03_Implementation_Review.pdf` — work plan, WPs/tasks/deliverables/milestones,
  risks, PM consistency, WP effort %, PM effort %, consortium/resources, score.
- `04_Cross_Consistency_Call_and_Document_Audit.pdf` — call coverage matrices,
  full traceability, numerical/naming/terminology inconsistencies, figure/table
  structural findings, cross-section contradictions.
- `05_Final_ESR.pdf` — **only** final per-criterion comment + score, total, and a
  concise overall assessment. **No rewriting suggestions.**

## Golden rules

1. Evaluate as submitted. 2. Evidence before judgement. 3. Confirm every
structural candidate. 4. Figures only to vision, never whole pages. 5. Scripts
calculate, you interpret. 6. Internal heuristics (e.g. PM ≤7%) are labelled
internal, never presented as official HE rules. 7. No double-penalisation.
8. Final ESR has no rewrite text.

## Rubric availability

`rubrics/EXCELLENCE_REVIEW.md` is complete. `IMPACT_REVIEW.md`,
`IMPLEMENTATION_REVIEW.md`, `CROSS_CONSISTENCY_REVIEW.md`, and
`ESR_WRITING_RULES.md` are placeholders until authored — each pass already reads
its rubric path, so dropping the final text in needs no code change. When a
rubric is still a placeholder, run the pass at reduced depth using this playbook's
generic guidance and note the limitation in the report's executive summary.
