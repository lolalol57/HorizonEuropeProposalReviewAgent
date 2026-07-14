"""Step 13 — PDF Report Generation.

Usage:
    python3 scripts/build_report.py <run-id> [--only 01,05]

Reads the per-pass findings JSON the host model wrote and renders the five
user-facing PDFs into workspace/<run-id>/OUTPUT/. The model writes findings;
this script renders them — so report generation is deterministic and identical
across harnesses.

    01_Excellence_Review.pdf                 <- excellence-findings.json
    02_Impact_Review.pdf                     <- impact-findings.json
    03_Implementation_Review.pdf             <- implementation-findings.json (+ PM/effort)
    04_Cross_Consistency_Call_and_Document_Audit.pdf
                                             <- cross-consistency-findings.json (+ structural)
    05_Final_ESR.pdf                         <- esr-findings.json

A report whose findings file is absent is skipped with a note (so Phase-A runs
with only Excellence still succeed).
"""
import argparse
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, PageBreak)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

STATUS = {
    "adequate": ("Adequately Addressed", colors.HexColor("#1a7f37")),
    "partial":  ("Partially Addressed", colors.HexColor("#bf8700")),
    "missing":  ("Not Adequately Addressed / Missing", colors.HexColor("#cf222e")),
    "na":       ("Not Applicable", colors.HexColor("#6e7781")),
}

REPORTS = [
    ("01", "excellence-findings.json", "01_Excellence_Review.pdf", "criterion"),
    ("02", "impact-findings.json", "02_Impact_Review.pdf", "criterion"),
    ("03", "implementation-findings.json", "03_Implementation_Review.pdf", "criterion"),
    ("04", "cross-consistency-findings.json",
     "04_Cross_Consistency_Call_and_Document_Audit.pdf", "cross"),
    ("05", "esr-findings.json", "05_Final_ESR.pdf", "esr"),
]


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("H1x", parent=ss["Title"], fontSize=20, spaceAfter=4,
                          textColor=colors.HexColor("#0b3d5c")))
    ss.add(ParagraphStyle("Sub", parent=ss["Normal"], fontSize=9,
                          textColor=colors.HexColor("#57606a"), spaceAfter=10))
    ss.add(ParagraphStyle("H2x", parent=ss["Heading2"], fontSize=13,
                          textColor=colors.HexColor("#0b3d5c"), spaceBefore=12,
                          spaceAfter=4))
    ss.add(ParagraphStyle("Item", parent=ss["Normal"], fontSize=9.5, leading=13,
                          spaceAfter=2, alignment=TA_LEFT))
    ss.add(ParagraphStyle("Field", parent=ss["Normal"], fontSize=9, leading=12,
                          leftIndent=10, spaceAfter=1,
                          textColor=colors.HexColor("#24292f")))
    ss.add(ParagraphStyle("Score", parent=ss["Normal"], fontSize=13,
                          textColor=colors.HexColor("#0b3d5c"), spaceBefore=6))
    return ss


def _status_tag(status):
    label, color = STATUS.get((status or "").lower(),
                              ("Unspecified", colors.HexColor("#6e7781")))
    return '<font color="{}"><b>{}</b></font>'.format(color.hexval(), label)


def _esc(text):
    if text is None:
        return ""
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _header(story, ss, title, subtitle):
    story.append(Paragraph(_esc(title), ss["H1x"]))
    story.append(Paragraph(_esc(subtitle), ss["Sub"]))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#0b3d5c")))
    story.append(Spacer(1, 6))


def _item(story, ss, item):
    story.append(Paragraph("{} &nbsp; {}".format(
        _status_tag(item.get("status")), _esc(item.get("label"))), ss["Item"]))
    for key, prefix in (("evidence", "Evidence"),
                        ("assessment", "Reviewer Assessment"),
                        ("improvement", "Suggested Improvement")):
        val = item.get(key)
        if val:
            story.append(Paragraph("<b>{}:</b> {}".format(prefix, _esc(val)),
                                   ss["Field"]))
    story.append(Spacer(1, 3))


def _bullets(story, ss, title, items):
    if not items:
        return
    story.append(Paragraph(_esc(title), ss["H2x"]))
    for it in items:
        story.append(Paragraph("&bull; {}".format(_esc(it)), ss["Item"]))


def _sections(story, ss, data):
    for sec in data.get("sections", []):
        story.append(Paragraph(_esc(sec.get("title", "Section")), ss["H2x"]))
        for item in sec.get("items", []):
            _item(story, ss, item)


def _priority_actions(story, ss, actions):
    if not actions:
        return
    story.append(Paragraph("Priority Improvement Actions "
                           "(Internal Improvement Report)", ss["H2x"]))
    for a in actions:
        story.append(Paragraph("<b>{} — {}</b>".format(
            _esc(a.get("priority", "")), _esc(a.get("issue", ""))), ss["Item"]))
        if a.get("why"):
            story.append(Paragraph("<b>Why it matters:</b> {}".format(
                _esc(a["why"])), ss["Field"]))
        if a.get("action"):
            story.append(Paragraph("<b>Recommended action:</b> {}".format(
                _esc(a["action"])), ss["Field"]))
        story.append(Spacer(1, 3))


def _score(story, ss, data):
    if data.get("score") is not None:
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=0.6,
                                color=colors.HexColor("#8c959f")))
        story.append(Paragraph("<b>{} Score: {} / 5.0</b>".format(
            _esc(data.get("criterion", "Criterion")), data["score"]), ss["Score"]))


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------
def render_criterion(run_id, data, title, out_path, ss, extra=None):
    story = []
    _header(story, ss, title,
            "Horizon Europe Proposal Review — run {}".format(run_id))
    if data.get("executive_summary"):
        story.append(Paragraph("Executive Summary", ss["H2x"]))
        story.append(Paragraph(_esc(data["executive_summary"]), ss["Item"]))
    _sections(story, ss, data)
    if extra:
        extra(story, ss)
    _bullets(story, ss, "Main Strengths", data.get("strengths"))
    _bullets(story, ss, "Main Shortcomings", data.get("shortcomings"))
    _priority_actions(story, ss, data.get("priority_actions"))
    if data.get("esr_comment"):
        story.append(Paragraph("Final ESR-Style Comment", ss["H2x"]))
        story.append(Paragraph(_esc(data["esr_comment"]), ss["Item"]))
    _score(story, ss, data)
    _build(out_path, story)


def _pm_effort_flowables(run_id):
    def _add(story, ss):
        pm = common.read_json(common.internal_path(run_id, "pm-effort-analysis.json"))
        if not pm or pm.get("status") != "OK":
            return
        story.append(Paragraph("Person-Month & Work Package Effort "
                               "(deterministic)", ss["H2x"]))
        totals = pm.get("totals", {})
        story.append(Paragraph(
            "WP PM total: {} &nbsp;|&nbsp; Partner PM total: {} &nbsp;|&nbsp; "
            "Declared total: {}".format(
                totals.get("wp_pm_total"), totals.get("partner_pm_total"),
                totals.get("declared_total_pm")), ss["Item"]))
        for r in pm.get("reconciliation", []):
            story.append(Paragraph("&bull; {}: <b>{}</b>".format(
                _esc(r.get("comparison")), _esc(r.get("status"))), ss["Field"]))
        rows = [["WP", "Title", "PM", "Effort %", "Mgmt"]]
        for w in pm.get("wp_effort", []):
            rows.append([_esc(w.get("id")), _esc((w.get("title") or "")[:40]),
                         w.get("pm"), w.get("effort_share_pct"),
                         "yes" if w.get("is_management") else ""])
        tbl = Table(rows, hAlign="LEFT",
                    colWidths=[22*mm, 70*mm, 18*mm, 22*mm, 16*mm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d5c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d1d9")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#f6f8fa")]),
        ]))
        story.append(tbl)
        mgmt = pm.get("project_management_effort")
        if mgmt:
            flag = "within" if mgmt["within_threshold"] else "ABOVE"
            story.append(Spacer(1, 4))
            story.append(Paragraph(
                "<b>Project-Management effort:</b> {}% ({} internal preferred "
                "threshold &le; {}%). <i>{}</i>".format(
                    mgmt["project_management_effort_pct"], flag,
                    mgmt["internal_threshold_pct"], _esc(mgmt["disclaimer"])),
                ss["Field"]))
        story.append(Spacer(1, 6))
    return _add


def render_cross(run_id, data, out_path, ss):
    story = []
    _header(story, ss, "Cross-Consistency, Call Coverage & Document Audit",
            "Horizon Europe Proposal Review — run {}".format(run_id))
    # Coverage matrices (list of {title, headers, rows}).
    for mtx in data.get("matrices", []):
        story.append(Paragraph(_esc(mtx.get("title", "Coverage Matrix")), ss["H2x"]))
        rows = [[_esc(h) for h in mtx.get("headers", [])]]
        rows += [[_esc(c) for c in row] for row in mtx.get("rows", [])]
        if len(rows) > 1:
            tbl = Table(rows, hAlign="LEFT")
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d5c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d1d9")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#f6f8fa")]),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 6))
    _sections(story, ss, data)
    _bullets(story, ss, "Confirmed Numerical / Naming / Terminology Inconsistencies",
             data.get("inconsistencies"))
    # Raw structural candidates appendix (for evaluator traceability).
    struct = common.read_json(
        common.internal_path(run_id, "structural-candidates.json"))
    if struct:
        cands = (struct.get("tables", {}).get("candidates", [])
                 + struct.get("figures", {}).get("candidates", []))
        if cands:
            story.append(Paragraph("Appendix — Structural Candidates "
                                   "(unconfirmed, for reference)", ss["H2x"]))
            for c in cands:
                story.append(Paragraph("&bull; [{}] {}".format(
                    _esc(c.get("type")), _esc(c.get("detail"))), ss["Field"]))
    _build(out_path, story)


def render_esr(run_id, data, out_path, ss):
    story = []
    _header(story, ss, "Final Evaluation Summary Report (ESR)",
            "Horizon Europe Proposal Review — run {}".format(run_id))
    story.append(Paragraph(
        "<i>This report evaluates the proposal as submitted. It contains no "
        "rewriting suggestions or replacement text.</i>", ss["Sub"]))
    total = 0.0
    have_total = True
    for crit in data.get("criteria", []):
        story.append(Paragraph(_esc(crit.get("name", "Criterion")), ss["H2x"]))
        story.append(Paragraph(_esc(crit.get("comment", "")), ss["Item"]))
        sc = crit.get("score")
        if sc is None:
            have_total = False
        else:
            total += float(sc)
        story.append(Paragraph("<b>Score: {} / 5.0</b>".format(sc), ss["Score"]))
        story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#0b3d5c")))
    shown_total = data.get("total_score",
                           round(total, 1) if have_total else None)
    story.append(Paragraph("<b>Total Score: {} / 15.0</b>".format(shown_total),
                           ss["Score"]))
    if data.get("overall"):
        story.append(Spacer(1, 6))
        story.append(Paragraph("Overall Assessment", ss["H2x"]))
        story.append(Paragraph(_esc(data["overall"]), ss["Item"]))
    _build(out_path, story)


def _build(out_path, story):
    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=16*mm, bottomMargin=16*mm,
                            title=os.path.basename(out_path))
    doc.build(story)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id")
    ap.add_argument("--only", default=None,
                    help="Comma list of report numbers to build, e.g. 01,05")
    args = ap.parse_args()
    run_id = args.run_id
    only = set(args.only.split(",")) if args.only else None

    ss = _styles()
    out_dir = common.subdir(run_id, "OUTPUT")
    os.makedirs(out_dir, exist_ok=True)

    built, skipped = [], []
    for num, findings_name, pdf_name, kind in REPORTS:
        if only and num not in only:
            continue
        data = common.read_json(common.internal_path(run_id, findings_name))
        out_path = os.path.join(out_dir, pdf_name)
        if data is None:
            skipped.append("{} (missing {})".format(pdf_name, findings_name))
            continue
        if kind == "criterion":
            title = {"01": "Criterion 1 — Excellence Review",
                     "02": "Criterion 2 — Impact Review",
                     "03": "Criterion 3 — Quality & Efficiency of Implementation"}[num]
            extra = _pm_effort_flowables(run_id) if num == "03" else None
            render_criterion(run_id, data, title, out_path, ss, extra=extra)
        elif kind == "cross":
            render_cross(run_id, data, out_path, ss)
        else:
            render_esr(run_id, data, out_path, ss)
        built.append(pdf_name)

    print("Report generation complete for run '{}':".format(run_id))
    for b in built:
        print("  built   : {}".format(b))
    for s in skipped:
        print("  skipped : {}".format(s))
    if not built:
        print("  (no findings JSON found — run the review passes first)")


if __name__ == "__main__":
    main()
