# Horizon Europe Final ESR Writing Rules

## 1. Purpose

This file defines the rules for producing the final evaluator-style assessment after the detailed Excellence, Impact, Implementation and Cross-Consistency reviews have been completed.

The Final ESR must:

- evaluate the proposal as submitted;
- remain evidence-based;
- remain criterion-specific;
- reflect the actual strengths and shortcomings identified during review;
- use concise evaluator-style language;
- remain consistent with the assigned score;
- avoid rewriting the proposal;
- avoid providing recommendations for improvement;
- avoid double penalisation.

The Final ESR is not an internal improvement report.

It is the final evaluation output.

---

# 1A. Scoring basis — how the score is decided (authoritative)

Evaluation scoring follows standard Horizon Europe ESR logic. The score must **not**
be based only on the presence of sections. It is based on:

- how convincingly the proposal satisfies the **criterion-specific expectations**;
- how well the **evidence** supports the claims;
- how **serious** the identified shortcomings are.

For each criterion, assess **both strengths and weaknesses**. A high score requires
that the proposal is clear, credible, complete, well-evidenced, and aligned with the
work programme. A lower score is justified when important aspects are vague, weakly
evidenced, inconsistent, over-claimed, insufficiently quantified, or not clearly
linked to implementation.

## Core expectations vs enhancing (bonus) checkpoints

Two layers feed the review, and they are treated differently for scoring:

- **Core evaluation expectations (drive the score).** Each criterion has a defined set
  of core expectations — the "review should consider" list at the top of that criterion's
  rubric, plus the *typical strengths* and *typical weaknesses*. **These, together with the
  General Scoring Logic bands (§5), determine the score.**
- **Detailed rubric checkpoints (enhancing / bonus).** The many numbered checkpoints in
  each rubric are diagnostic-coverage and improvement guidance. They are still written into
  reports 01–04 as `adequate` / `partial` / `missing` / `na` so the applicant can improve
  the proposal — but the **absence or partial status of an enhancing checkpoint does not,
  on its own, lower the score.** Presence of enhancing material may reinforce an already
  strong criterion; its absence is neutral. Record an absent enhancing item as `na`
  ("enhancing — not required") rather than `missing`.

The score is a holistic evaluator judgment against the core expectations and the band
definitions. **Never compute the score by counting ✅/⚠️/❌ across the checklist.** An
excellent proposal that satisfies all core expectations, with only minor or enhancing
gaps, must score at the top of the scale; a genuinely weak proposal must score low —
do not regress every proposal toward the middle.

---

# 2. Inputs

The Final ESR synthesis should use:

- final Excellence findings;
- final Impact findings;
- final Implementation findings;
- Cross-Consistency findings;
- Call Coverage findings;
- confirmed strengths;
- confirmed shortcomings;
- criterion-level draft scores;
- double-penalisation analysis.

The Final ESR should not directly copy all checklist findings.

Only the most important criterion-level findings should be included.

---

# 3. Final ESR Structure

The Final ESR stays concise and evaluator-style, but is **bullet-structured** —
short bullet points, not long dense paragraphs. Each criterion has a score,
**Strengths**, **Weaknesses**, and an **Evaluator comment**. It contains **no
suggested improvements**.

## Criterion 1 — Excellence

Score: X.X / 5.0

Strengths:

- ...
- ...

Weaknesses:

- ...
- ...

Evaluator comment:

- ...
- ...

---

## Criterion 2 — Impact

Score: X.X / 5.0

Strengths:

- ...

Weaknesses:

- ...

Evaluator comment:

- ...

---

## Criterion 3 — Quality and Efficiency of the Implementation

Score: X.X / 5.0

Strengths:

- ...

Weaknesses:

- ...

Evaluator comment:

- ...

---

## Total Score

XX.X / 15.0

## Overall Assessment

- ...
- ...

The `internal/esr-findings.json` the model writes to drive this report is:

```json
{"criteria": [{"name": "Criterion 1 — Excellence", "score": 0.0,
               "strengths": ["..."], "weaknesses": ["..."],
               "evaluator_comment": ["..."]}],
 "total_score": 0.0, "overall": ["..."]}
```

`evaluator_comment` and `overall` may be a bullet list or a single string. The
legacy flat shape `{criteria:[{name, comment, score}], total_score, overall}` is
still accepted for backward compatibility, but the bullet shape above is preferred.

---

# 4. Criterion-Level Scoring Only

Official scores must be assigned only at criterion level.

Do not assign official 0–5 scores to:

- individual objectives;
- individual WPs;
- individual KERs;
- individual review sections;
- individual checklist items.

Internal statuses such as:

- ✅
- ⚠️
- ❌
- ➖

are diagnostic only.

They must not appear as substitute official scores.

---

# 5. General Scoring Logic

Scores are assigned in `0.5` steps. Use the following band interpretation, applied
against the criterion's **core evaluation expectations** (§1A) — not against the count
of checklist items.

## 5.0

The criterion is addressed excellently. Strengths are clear and convincing. Any
weaknesses are minor and do not affect credibility.

## 4.0–4.5

The criterion is addressed very well. There are some shortcomings, but they are
limited and do not seriously undermine the proposal.

## 3.0–3.5

The criterion is broadly addressed, but there are meaningful weaknesses. The proposal
is fundable only if the weaknesses are not critical. (This is the funding **threshold**
band: the criterion is met, but with clear weaknesses.)

## 2.0–2.5

The criterion is weakly addressed. There are significant shortcomings affecting
credibility, feasibility or impact. (Below threshold.)

## 1.0–1.5

The criterion is inadequately addressed. Major information is missing or the logic is
not credible.

## 0–0.5

The criterion is not addressed or cannot be assessed.

**Calibration guardrails.** A score of 5 requires almost no meaningful shortcomings.
A score of 3 means the proposal meets the threshold but has clear weaknesses. A score
below 3 means the criterion is below threshold or has serious weaknesses. Enhancing
(bonus) gaps never pull a proposal below the band its core expectations earn.

---

# 6. Score–Comment Consistency

Before finalising each criterion:

☐ Does the written comment justify the score?

☐ Are important shortcomings reflected in the score?

☐ Does a score close to 5 contain only minor shortcomings?

☐ Does a score around 4 reflect a small number of meaningful shortcomings?

☐ Does a score around 3 reflect several shortcomings?

☐ Does a score below threshold reflect significant weaknesses?

☐ Is the severity of the language consistent with the score?

---

# 7. Shortcoming Severity

The reviewer should distinguish between different levels of issue.

## Minor Shortcoming

A marginal issue that is easy to correct and does not materially affect criterion quality.

A proposal may still receive a very high score.

---

## Shortcoming

An important issue that affects criterion quality but does not prevent useful project results.

The issue should influence the score.

---

## Significant Weakness

A major issue showing that an important aspect of the criterion is addressed in a limited, insufficient or ineffective way.

A significant weakness should materially reduce the score.

---

## Serious Inherent Weakness

A fundamental problem affecting the overall credibility of the criterion.

This may justify a very low score.

---

# 8. Writing Principles

The Final ESR comment should be:

- fair;
- accurate;
- clear;
- complete;
- criterion-specific;
- precise;
- concise;
- fact-based;
- consistent with the score.

The comment should explain:

1. what is strong;
2. what is insufficient;
3. why the shortcoming matters.

---

# 9. Strength Writing

Strengths should be written at criterion level.

Good:

> The objectives are clearly defined, measurable and well aligned with the topic, while the proposed methodology provides a coherent pathway from the identified research gaps to development and validation.

Weak:

> Objective 1 is good. Objective 2 is good. Objective 3 is also good.

Do not list every positive checklist item.

Prioritise the strengths that materially justify the score.

---

# 10. Shortcoming Writing

Shortcomings should be:

- specific;
- evidence-based;
- criterion-related;
- proportionate.

Good:

> However, the rationale for several quantitative performance targets is insufficiently substantiated, which weakens the credibility of the claimed level of ambition.

Weak:

> The KPIs should be improved.

---

# 11. No Recommendations in the Final ESR

The Final ESR must not contain:

- rewrite suggestions;
- replacement sentences;
- instructions to the consortium;
- recommended new Tasks;
- recommended new WPs;
- recommended new KERs;
- suggested table structures.

Avoid:

> The consortium should add a clearer baseline.

Prefer:

> The baseline supporting the claimed 30% improvement is not clearly defined.

Avoid:

> The proposal should include a competitor analysis.

Prefer:

> The market positioning is insufficiently substantiated because relevant competing solutions are not adequately analysed.

---

# 12. Evaluate the Proposal as Submitted

Do not assume:

- missing information can be added later;
- weak methodology can be corrected during Grant Agreement Preparation;
- missing partners can be added;
- missing validation can be designed later.

The review must assess what is actually submitted.

---

# 13. No Double Penalisation

The same underlying weakness must not be repeatedly penalised without a distinct criterion-specific effect.

Example:

Missing KPI baseline may affect:

Excellence:
objective measurability.

Impact:
credibility of claimed Scale and Significance.

These are distinct effects and may be mentioned separately.

However, the same missing baseline should not be repeated multiple times within the same criterion as separate penalties.

---

# 14. Criterion-Specific Boundaries

## Excellence

Focus on:

- objectives;
- ambition;
- State of the Art;
- advancement;
- methodology;
- interdisciplinarity;
- SSH;
- gender dimension;
- Open Science.

---

## Impact

Focus on:

- Expected Outcomes;
- pathways towards impact;
- scale and significance;
- target groups;
- Communication;
- Dissemination;
- Exploitation;
- KERs;
- uptake;
- sustainability.

---

## Implementation

Focus on:

- work plan;
- resources;
- WP structure;
- Tasks;
- consortium;
- partner roles;
- PM allocation;
- Deliverables;
- Milestones;
- risk management;
- management structures.

---

# 15. Excellence ESR Comment Structure

A strong Excellence comment may follow:

1. Overall positive assessment.
2. Objectives and ambition.
3. State of the Art and advancement.
4. Methodology.
5. Relevant cross-cutting methodological aspects.
6. Main shortcomings.

Example structure:

> The proposal presents clear and relevant objectives that are well aligned with the topic and supported by an ambitious technological approach. The proposed advancements beyond the State of the Art are generally well explained, and the methodology provides a coherent framework for development, integration and validation. The interdisciplinary approach and Open Science strategy are appropriately addressed. However, the rationale for several quantitative performance targets is insufficiently substantiated, and the availability of some critical data inputs is not fully demonstrated. These shortcomings reduce the overall credibility of the proposed ambition.

Do not reuse this wording mechanically.

---

# 16. Impact ESR Comment Structure

A strong Impact comment may follow:

1. Expected Outcome alignment.
2. Pathway credibility.
3. Scale and Significance.
4. Target groups.
5. Measures to maximise impact.
6. KERs and exploitation.
7. Main shortcomings.

Example structure:

> The proposal provides a generally credible pathway from project results to the expected outcomes and identifies relevant target groups and exploitation routes. The planned communication and dissemination activities are comprehensive, and the proposed KERs provide a useful basis for post-project exploitation. However, the scale and significance of several expected contributions are insufficiently quantified, while the market positioning and post-project investment requirements of some commercially oriented results remain underdeveloped.

Do not reuse this wording mechanically.

---

# 17. Implementation ESR Comment Structure

A strong Implementation comment may follow:

1. Overall work-plan coherence.
2. WP and Task structure.
3. resources and PM distribution.
4. consortium quality.
5. Deliverables, Milestones and risks.
6. Main shortcomings.

Example structure:

> The work plan is coherent and provides a logical progression from requirements and development to integration and validation. Partner roles are generally clear and the consortium covers the main scientific, technological and end-user capabilities required for implementation. The allocation of resources is broadly proportionate to responsibilities, and the risk-management approach addresses the main project challenges. However, several Task descriptions do not sufficiently differentiate the contributions of participating partners, and some Milestones are formulated primarily as Deliverable submission points rather than meaningful project maturity checkpoints.

Do not reuse this wording mechanically.

---

# 18. Avoid Checklist Language

The Final ESR should not read like:

- Objectives: good.
- KPIs: partial.
- Open Science: good.
- Gender: partial.

Instead, synthesise findings into evaluator-style prose.

---

# 19. Avoid Excessive Detail

Do not include every minor issue.

The Final ESR should focus on:

- score-driving strengths;
- score-driving shortcomings.

Detailed corrections belong in the internal review reports.

---

# 20. Avoid Unsupported Praise

Do not write:

> The proposal is highly innovative.

unless the review evidence supports this.

Prefer:

> The proposal presents a significant advancement beyond existing approaches through...

The assessment should explain why.

---

# 21. Avoid Unsupported Negative Language

Do not write:

> The methodology is weak.

Prefer:

> The methodology does not sufficiently explain how the heterogeneous data sources will be integrated and validated, which weakens implementation credibility.

---

# 22. Avoid Contradictory Score Language

A score of 4.5 should not contain:

- several significant weaknesses;
- major feasibility concerns;
- fundamental methodological gaps.

A score of 2.5 should not contain:

- overwhelmingly positive language;
- only one minor shortcoming.

---

# 23. Comment Length

The Final ESR should remain concise.

Each criterion comment should normally prioritise:

- the strongest 2–4 strengths;
- the most important 1–4 shortcomings.

The exact length may vary according to proposal complexity.

---

# 24. Consolidation of Findings

Before writing the Final ESR:

☐ Remove duplicate findings.

☐ Merge related findings.

☐ Identify the root cause of repeated issues.

☐ Determine which criterion is primarily affected.

☐ Retain secondary criterion effects only where genuinely distinct.

---

# 25. Final Score Calibration

Before finalising each criterion, calibrate the score against the **General Scoring
Logic bands (§5)** and the criterion's **core evaluation expectations (§1A)**:

☐ Does the band match how convincingly the **core expectations** are satisfied, the
quality of the evidence, and the severity of the weaknesses — **not** the number of
checklist items?

☐ Are **enhancing/bonus** gaps excluded from the score (they never pull the criterion
below the band its core expectations earn)?

☐ **5.0** — all core expectations satisfied; only minor/enhancing gaps; credibility
unaffected.

☐ **4.0–4.5** — very well addressed; limited shortcomings that do not seriously
undermine the proposal.

☐ **3.0–3.5** (threshold) — broadly addressed but with meaningful weaknesses; fundable
only if the weaknesses are not critical.

☐ **Below 3.0** — significant/serious weaknesses in the core expectations; the written
assessment is clearly critical enough to justify the score.

☐ Is the severity of the written comment consistent with the band (no 4.5 comment full
of significant weaknesses; no 2.5 comment that is overwhelmingly positive)?

---

# 26. Final Quality Check

Before producing the Final ESR:

☐ Are all criterion comments criterion-specific?

☐ Are comments evidence-based?

☐ Are scores consistent with comments?

☐ Are duplicate penalties removed?

☐ Are rewrite suggestions removed?

☐ Are internal heuristic thresholds removed from official-style comments unless directly relevant as analytical context?

☐ Are unofficial internal preferences avoided as if they were formal EC rules?

☐ Is the proposal assessed as submitted?

☐ Is the wording professional and neutral?

☐ Is the total score calculated correctly?

---

# 27. Final Output Template

# Horizon Europe Proposal Evaluation

## Criterion 1 — Excellence

Score: X.X / 5.0

Strengths:

- [most important strengths]

Weaknesses:

- [most important weaknesses]

Evaluator comment:

- [concise evaluator-style bullets — no suggested improvements]

---

## Criterion 2 — Impact

Score: X.X / 5.0

Strengths:

- ...

Weaknesses:

- ...

Evaluator comment:

- ...

---

## Criterion 3 — Quality and Efficiency of the Implementation

Score: X.X / 5.0

Strengths:

- ...

Weaknesses:

- ...

Evaluator comment:

- ...

---

# Total Score

XX.X / 15.0

## Overall Assessment

- ...
