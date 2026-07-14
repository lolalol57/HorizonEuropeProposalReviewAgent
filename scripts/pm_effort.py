"""Step 11 — Limited Deterministic Person-Month / Effort Calculations.

Usage:
    python3 scripts/pm_effort.py <run-id> [--pm-threshold 7.0]

Reads PM data from internal/proposal-map.json (the model populates this from the
partner-effort and WP-effort tables). Computes only what the spec (§11) allows:
    1. Total Person-Month reconciliation (partner vs WP vs declared)
    2. Person-Month totals per Work Package
    3. Work Package effort percentages
    4. Project-Management WP effort percentage vs an INTERNAL heuristic

The script calculates and flags; the host model interprets. The PM threshold is
labelled an INTERNAL PROPOSAL QUALITY HEURISTIC, not an official HE rule.

Expected shape in proposal-map.json:
    "implementation": {
        "declared_total_pm": 480,
        "partners": [{"name": "P1", "pm": 60}, ...],
        "work_packages": [{"id": "WP1", "title": "...", "pm": 38,
                            "is_management": false}, ...]
    }
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id")
    ap.add_argument("--pm-threshold", type=float, default=7.0,
                    help="Internal preferred max Project-Management effort share (%%)")
    args = ap.parse_args()
    run_id = args.run_id

    pmap = common.read_json(common.internal_path(run_id, "proposal-map.json"), {})
    impl = (pmap or {}).get("implementation", {})
    partners = impl.get("partners", []) or []
    wps = impl.get("work_packages", []) or []
    declared = _num(impl.get("declared_total_pm"))

    partner_pms = [(_num(p.get("pm")), p.get("name")) for p in partners]
    wp_rows = [(w.get("id"), _num(w.get("pm")), bool(w.get("is_management")),
                w.get("title")) for w in wps]

    partner_total = sum(pm for pm, _ in partner_pms if pm is not None) \
        if partner_pms else None
    wp_total = sum(pm for _, pm, _, _ in wp_rows if pm is not None) \
        if wp_rows else None

    have_enough = bool(wp_rows) and wp_total not in (None, 0)
    if not have_enough:
        result = {
            "run_id": run_id,
            "status": "INSUFFICIENT_DATA",
            "note": "proposal-map.json does not yet contain WP person-months. "
                    "Populate implementation.work_packages[].pm (and partners[].pm / "
                    "declared_total_pm where available), then re-run.",
        }
        common.write_json(common.internal_path(run_id, "pm-effort-analysis.json"),
                          result)
        print("PM/effort: INSUFFICIENT_DATA — populate proposal-map.json first.")
        return

    # ---- Reconciliation ---------------------------------------------------
    reconciliation = []

    def _cmp(label_a, a, label_b, b):
        if a is None or b is None:
            return {"comparison": "{} vs {}".format(label_a, label_b),
                    "status": "NOT_AVAILABLE"}
        diff = round(a - b, 3)
        return {"comparison": "{} vs {}".format(label_a, label_b),
                label_a: a, label_b: b, "difference": diff,
                "status": "Consistent" if abs(diff) < 1e-6 else "Inconsistent"}

    if partner_total is not None:
        reconciliation.append(_cmp("partner_pm_total", partner_total,
                                   "wp_pm_total", wp_total))
    if declared is not None:
        reconciliation.append(_cmp("declared_total_pm", declared,
                                   "wp_pm_total", wp_total))
        if partner_total is not None:
            reconciliation.append(_cmp("declared_total_pm", declared,
                                       "partner_pm_total", partner_total))

    # ---- Per-WP effort share ---------------------------------------------
    wp_breakdown = []
    pm_wp_share = None
    for wp_id, pm, is_mgmt, title in wp_rows:
        share = round(pm / wp_total * 100, 2) if pm is not None else None
        row = {"id": wp_id, "title": title, "pm": pm,
               "effort_share_pct": share, "is_management": is_mgmt}
        wp_breakdown.append(row)
        if is_mgmt and share is not None:
            pm_wp_share = share if pm_wp_share is None else pm_wp_share + share

    pm_flag = None
    if pm_wp_share is not None:
        pm_flag = {
            "project_management_effort_pct": round(pm_wp_share, 2),
            "internal_threshold_pct": args.pm_threshold,
            "within_threshold": pm_wp_share <= args.pm_threshold,
            "label": "INTERNAL PROPOSAL QUALITY HEURISTIC",
            "disclaimer": "This threshold is an internal proposal-quality "
                          "preference, NOT an official Horizon Europe rule.",
        }

    result = {
        "run_id": run_id,
        "status": "OK",
        "totals": {
            "partner_pm_total": partner_total,
            "wp_pm_total": wp_total,
            "declared_total_pm": declared,
        },
        "reconciliation": reconciliation,
        "wp_effort": wp_breakdown,
        "project_management_effort": pm_flag,
    }
    common.write_json(common.internal_path(run_id, "pm-effort-analysis.json"), result)

    print("PM/effort analysis complete for run '{}':".format(run_id))
    print("  WP PM total      : {}".format(wp_total))
    print("  partner PM total : {}".format(partner_total))
    print("  declared total   : {}".format(declared))
    for r in reconciliation:
        print("  {} -> {}".format(r["comparison"], r["status"]))
    if pm_flag:
        print("  PM WP effort     : {}% (internal threshold <= {}%, {})".format(
            pm_flag["project_management_effort_pct"], args.pm_threshold,
            "OK" if pm_flag["within_threshold"] else "ABOVE"))


if __name__ == "__main__":
    main()
