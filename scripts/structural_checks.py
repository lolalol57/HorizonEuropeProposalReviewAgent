"""Steps 4 & 9 — Lightweight Structural Checks.

Usage:
    python3 scripts/structural_checks.py <run-id>

Emits internal/structural-candidates.json. Every item is a CANDIDATE issue,
never a confirmed weakness — per spec §9 the host model must confirm each one
against the actual document before it may appear in a report.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def _numbering_issues(numbers, kind):
    """Duplicates and gaps in a set of detected Table/Figure numbers."""
    issues = []
    seen = {}
    for n in numbers:
        seen[n] = seen.get(n, 0) + 1
    for n, c in sorted(seen.items()):
        if c > 1:
            issues.append({
                "type": "duplicate_number",
                "detail": "{} {} appears {} times.".format(kind, n, c),
                "status": "POTENTIAL ISSUE — REVIEW REQUIRED",
            })
    if seen:
        lo, hi = min(seen), max(seen)
        missing = [n for n in range(lo, hi + 1) if n not in seen]
        for n in missing:
            issues.append({
                "type": "numbering_gap",
                "detail": "{} {} was not identified (gap between {} and {}).".format(
                    kind, n, lo, hi),
                "status": "POTENTIAL ISSUE — REVIEW REQUIRED",
            })
    return issues


def _referenced_numbers(full_text, ref_re, caption_re):
    """Numbers referenced in running text, excluding pure caption lines."""
    refs = set()
    for line in full_text.splitlines():
        if caption_re.match(line):
            continue  # a caption defines, it does not reference
        for m in ref_re.finditer(line):
            refs.add(int(m.group(1)))
    return refs


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 scripts/structural_checks.py <run-id>")
    run_id = sys.argv[1]

    document = common.read_json(common.internal_path(run_id, "document.json"), {})
    table_map = common.read_json(common.internal_path(run_id, "table-map.json"), {})
    figure_map = common.read_json(common.internal_path(run_id, "figure-map.json"), {})
    full_text = document.get("full_text", "")

    # ---- Tables -----------------------------------------------------------
    t_labels = table_map.get("detected_table_labels", [])
    t_numbers = [l["detected_number"] for l in t_labels if l.get("detected_number")]
    table_issues = _numbering_issues(t_numbers, "Table")
    for lbl in t_labels:
        if not lbl.get("detected_title"):
            table_issues.append({
                "type": "missing_title",
                "detail": "Table {} may have no title on page {}.".format(
                    lbl.get("detected_number"), lbl.get("page")),
                "status": "POTENTIAL ISSUE — REVIEW REQUIRED",
            })
    t_refs = _referenced_numbers(full_text, common.TABLE_REF_RE,
                                 common.TABLE_CAPTION_RE)
    for n in sorted(set(t_numbers)):
        if n not in t_refs:
            table_issues.append({
                "type": "unreferenced_table",
                "detail": "Table {} may not be referenced in the main text.".format(n),
                "status": "POTENTIAL ISSUE — REVIEW REQUIRED",
            })
    tables_no_number = [t["id"] for t in table_map.get("tables", [])
                        if not t.get("detected_number")]

    # ---- Figures ----------------------------------------------------------
    figs = figure_map.get("figures", [])
    unmatched = figure_map.get("unmatched_captions", [])
    f_numbers = [f["detected_number"] for f in figs if f.get("detected_number")]
    f_numbers += [u["detected_number"] for u in unmatched if u.get("detected_number")]
    figure_issues = _numbering_issues(f_numbers, "Figure")
    for f in figs:
        if not f.get("detected_number"):
            figure_issues.append({
                "type": "missing_number_or_caption",
                "detail": "Extracted image {} (page {}) has no detected "
                          "figure number/caption.".format(f["id"], f.get("page")),
                "status": "POTENTIAL ISSUE — REVIEW REQUIRED",
            })
    for u in unmatched:
        figure_issues.append({
            "type": "figure_without_raster",
            "detail": "Figure {} (page {}) had no extractable raster image "
                      "(likely vector art); render the page for visual review.".format(
                          u.get("detected_number"), u.get("page")),
            "status": "POTENTIAL ISSUE — REVIEW REQUIRED",
        })
    f_refs = _referenced_numbers(full_text, common.FIGURE_REF_RE,
                                 common.FIGURE_CAPTION_RE)
    for n in sorted(set(f_numbers)):
        if n not in f_refs:
            figure_issues.append({
                "type": "unreferenced_figure",
                "detail": "Figure {} may not be referenced in the main text.".format(n),
                "status": "POTENTIAL ISSUE — REVIEW REQUIRED",
            })

    result = {
        "run_id": run_id,
        "note": "All items are CANDIDATES. The reviewing model must confirm each "
                "against the document before including it in any report.",
        "tables": {
            "detected_numbers": sorted(set(t_numbers)),
            "referenced_numbers": sorted(t_refs),
            "tables_without_number": tables_no_number,
            "candidates": table_issues,
        },
        "figures": {
            "detected_numbers": sorted(set(f_numbers)),
            "referenced_numbers": sorted(f_refs),
            "candidates": figure_issues,
        },
    }
    common.write_json(common.internal_path(run_id, "structural-candidates.json"),
                      result)

    print("Structural checks complete for run '{}':".format(run_id))
    print("  table candidates : {}".format(len(table_issues)))
    print("  figure candidates: {}".format(len(figure_issues)))
    print("  (all flagged POTENTIAL ISSUE — REVIEW REQUIRED)")


if __name__ == "__main__":
    main()
