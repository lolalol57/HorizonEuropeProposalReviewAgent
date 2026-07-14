"""Step 1 — Proposal Intake.

Usage:
    python3 scripts/intake.py [proposal.pdf|proposal.docx] \
        [--topic "<url | topic-id | text>"] [--action RIA|IA|CSA|Other]

If no proposal path is given, the newest .pdf/.docx in the inbox is used
(inbox = HE_REVIEW_INBOX env, else <cwd>/inbox). Detects the file type, sets up
workspace/<run-id>/, copies the proposal into inputs/, and records a manifest the
later steps read. Prints the run-id on the last line (scripts downstream take
that run-id as their only argument).
"""
import argparse
import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

SUPPORTED = {".pdf": "pdf", ".docx": "docx"}


def _newest_in_inbox():
    """Return the newest .pdf/.docx in the inbox, or exit with guidance."""
    candidates = []
    for ext in SUPPORTED:
        candidates += glob.glob(os.path.join(common.INBOX, "*" + ext))
        candidates += glob.glob(os.path.join(common.INBOX, "*" + ext.upper()))
    if not candidates:
        raise SystemExit(
            "No proposal path given and no .pdf/.docx found in inbox:\n  {}\n"
            "Either pass a file path, or drop a proposal into that folder.".format(
                common.INBOX)
        )
    return max(candidates, key=os.path.getmtime)


def main():
    ap = argparse.ArgumentParser(description="Horizon Europe proposal intake")
    ap.add_argument("proposal", nargs="?", default=None,
                    help="Path to the proposal (.pdf or .docx). "
                         "If omitted, the newest file in the inbox is used.")
    ap.add_argument("--topic", default=None,
                    help="Official topic URL, topic id, or full topic text")
    ap.add_argument("--action", default=None,
                    help="Type of Action if known (RIA / IA / CSA / Other)")
    args = ap.parse_args()

    proposal = args.proposal or _newest_in_inbox()
    src = os.path.abspath(proposal)
    if not os.path.exists(src):
        raise SystemExit("Proposal not found: {}".format(src))

    ext = os.path.splitext(src)[1].lower()
    if ext == ".doc":
        raise SystemExit(
            "Legacy .doc is not supported directly. Convert to .docx or .pdf first "
            "(e.g. `textutil -convert docx file.doc` or `soffice --convert-to pdf`)."
        )
    if ext not in SUPPORTED:
        raise SystemExit("Unsupported file type '{}'. Use .pdf or .docx.".format(ext))

    run_id = common.run_id_for(src)
    common.ensure_run_dirs(run_id)

    dest = os.path.join(common.subdir(run_id, "inputs"), os.path.basename(src))
    shutil.copy2(src, dest)

    # Persist raw topic text as a file if it is not a short url/id.
    topic_ref = args.topic
    topic_file = None
    if args.topic and (len(args.topic) > 400 or "\n" in args.topic):
        topic_file = os.path.join(common.subdir(run_id, "inputs"), "topic.txt")
        with open(topic_file, "w", encoding="utf-8") as fh:
            fh.write(args.topic)
        topic_ref = "topic.txt"

    manifest = {
        "run_id": run_id,
        "proposal_original_path": src,
        "proposal_file": os.path.basename(src),
        "proposal_type": SUPPORTED[ext],
        "topic": topic_ref,
        "topic_file": os.path.basename(topic_file) if topic_file else None,
        "type_of_action": args.action,
        "steps_completed": ["intake"],
    }
    common.write_json(common.internal_path(run_id, "manifest.json"), manifest)

    print("Intake complete.")
    print("  proposal : {}".format(manifest["proposal_file"]))
    print("  type     : {}".format(manifest["proposal_type"]))
    print("  topic    : {}".format(topic_ref or "(none provided)"))
    print("  action   : {}".format(args.action or "(to be inferred from topic)"))
    print("  workspace: {}".format(common.run_dir(run_id)))
    print("run_id={}".format(run_id))


if __name__ == "__main__":
    main()
