"""Shared helpers for the Horizon Europe Proposal Review Agent scripts.

Only deterministic utilities live here: workspace layout, run-id derivation,
JSON read/write, and the regexes used to detect table/figure numbering.

No LLM calls happen anywhere in scripts/ — the host harness model does the
reasoning; these scripts do only mechanical, reproducible work.
"""
import hashlib
import json
import os
import re

# ---------------------------------------------------------------------------
# Paths / workspace layout
# ---------------------------------------------------------------------------
# scripts/ lives one level below the asset root (rubrics/PLAYBOOK live here). After
# `he-review install` this is ~/.claude/skills/he-proposal-review/, which is NOT
# writable-friendly — so run artefacts (workspace, inbox) resolve to the *current
# working directory* instead, keeping outputs in the user's project. Override with
# HE_REVIEW_WORKSPACE (workspace root) / HE_REVIEW_INBOX (inbox dir).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUBRICS_DIR = os.path.join(REPO_ROOT, "rubrics")

WORKSPACE = os.environ.get(
    "HE_REVIEW_WORKSPACE",
    os.path.join(os.getcwd(), "he-review-workspace"),
)
INBOX = os.environ.get("HE_REVIEW_INBOX", os.path.join(os.getcwd(), "inbox"))

# Sub-directories created inside workspace/<run-id>/
SUBDIRS = ("inputs", "internal", "figures", "pages", "OUTPUT")


def run_dir(run_id):
    return os.path.join(WORKSPACE, run_id)


def subdir(run_id, name):
    return os.path.join(run_dir(run_id), name)


def internal_path(run_id, filename):
    return os.path.join(subdir(run_id, "internal"), filename)


def ensure_run_dirs(run_id):
    for name in SUBDIRS:
        os.makedirs(subdir(run_id, name), exist_ok=True)
    return run_dir(run_id)


def run_id_for(proposal_path):
    """Stable, human-readable run-id derived from the proposal filename.

    Re-running intake on the same file reuses the same run-id (idempotent),
    while a short path hash keeps two same-named files from colliding.
    """
    base = os.path.splitext(os.path.basename(proposal_path))[0]
    slug = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-").lower()[:40] or "proposal"
    digest = hashlib.sha1(os.path.abspath(proposal_path).encode("utf-8")).hexdigest()[:6]
    return "{}-{}".format(slug, digest)


# ---------------------------------------------------------------------------
# JSON IO
# ---------------------------------------------------------------------------
def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return path


def read_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_manifest(run_id):
    manifest = read_json(internal_path(run_id, "manifest.json"))
    if manifest is None:
        raise SystemExit(
            "No manifest for run '{}'. Run intake.py first.".format(run_id)
        )
    return manifest


# ---------------------------------------------------------------------------
# Detection regexes (used by extract.py + structural_checks.py)
# ---------------------------------------------------------------------------
# A caption line that *labels* a table/figure, e.g. "Table 3: ..." / "Figure 4 —".
TABLE_CAPTION_RE = re.compile(r"^\s*Table\s+(\d+)\b[\.\:\)–—\-\s]*(.*)$", re.I)
FIGURE_CAPTION_RE = re.compile(r"^\s*Fig(?:ure)?\.?\s+(\d+)\b[\.\:\)–—\-\s]*(.*)$", re.I)

# An in-text *reference* anywhere in a line, e.g. "... as shown in Figure 4 ...".
TABLE_REF_RE = re.compile(r"\bTable\s+(\d+)\b", re.I)
FIGURE_REF_RE = re.compile(r"\bFig(?:ure)?\.?\s+(\d+)\b", re.I)
