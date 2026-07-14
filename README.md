# Horizon Europe Proposal Review Agent

A **proposal-review agent for Claude Code** that reviews Horizon Europe proposals in a
structured, evidence-based, evaluator-oriented way and produces five ESR-style PDF reports
(Excellence · Impact · Implementation · Cross-Consistency · Final ESR).

It installs as an **npm package**: a small CLI drops a Claude Code **Skill** + a
`/he-review` **command** into `~/.claude/`, and installs the Python deps. Claude itself does
the reviewing (call analysis, figure vision, the five passes, the ESR); bundled Python
scripts do only the deterministic work — extraction, Person-Month maths, and PDF rendering.

> The agent also still works in Codex/Cursor via the in-repo `AGENTS.md` / `.cursor/rules`
> after a plain `git clone`, but the npm install below targets **Claude Code**.

## Quick start (Claude Code)

One command — this is the easiest install (**npm**, not brew):

```bash
npm install -g github:lolalol57/HorizonEuropeProposalReviewAgent
```

That's it. The package's `postinstall` automatically runs `he-review install`, which copies
the Skill + `/he-review` command into `~/.claude/` and installs the Python deps. Then open
Claude Code in your project and run `/he-review <proposal.pdf> "<topic>"`.

> **Why npm and not brew?** This is a Node CLI that installs a Claude Code Skill, so npm is
> the native, one-line path. A Homebrew formula would add a macOS-only tap to maintain for
> no benefit — you don't need brew.

## Install — details & alternatives

Prerequisites: **Node ≥18** and **Python ≥3.8** (with `pip3`).

```bash
# Recommended — global install from GitHub (postinstall does the rest):
npm install -g github:lolalol57/HorizonEuropeProposalReviewAgent

# No global install (one-off): run the installer via npx
npx github:lolalol57/HorizonEuropeProposalReviewAgent install

# …or clone then install locally (for development):
git clone https://github.com/lolalol57/HorizonEuropeProposalReviewAgent.git
cd HorizonEuropeProposalReviewAgent && npm install -g .

# If the automatic postinstall was skipped, run it manually:
he-review install    # copies the Skill + /he-review command into ~/.claude
                     # and installs the Python deps (PyMuPDF, python-docx, reportlab)
```

`he-review install` runs automatically on global npm install; run it explicitly if you want
to see the output or re-run it. Remove everything with `he-review uninstall`.

## Use

Open Claude Code in the project where you want the reports, then either:

```
/he-review ~/Desktop/HARMONY.pdf "MAGICIAN Open Call #1" RIA
```

or drop a proposal into an `inbox/` folder and just run:

```
/he-review
```

You can also ask in natural language — "review this Horizon Europe proposal" — and the
`he-proposal-review` skill triggers. Claude will ask for the official topic/call if you
didn't provide one (it drives the review).

**Arguments:** `[proposal path] [topic url|id|"text"] [RIA|IA|CSA]`. The path is optional
(newest file in `./inbox/` is used if omitted); the topic is strongly recommended.

**Output:** five PDFs in `./he-review-workspace/<run-id>/OUTPUT/`
(`01_Excellence` … `05_Final_ESR`). Reports and all intermediate artefacts land in the
**current project directory**, not inside `~/.claude`.

## CLI (used by the skill; also runnable by hand)

```bash
he-review install | uninstall | paths
he-review review [path] --topic "<...>" [--action RIA|IA|CSA]   # intake+extract+structural
he-review intake | extract | structural | pm | report [args]     # individual steps
```

`he-review review` runs the deterministic bookend; Claude then does the reasoning passes and
finishes with `he-review pm <run-id>` and `he-review report <run-id>`. Set
`HE_REVIEW_WORKSPACE` / `HE_REVIEW_INBOX` to override the default `./he-review-workspace` and
`./inbox` locations.

## How it fits together

```
PLAYBOOK.md          <- single source of truth (the 13-step workflow)
skill/SKILL.md       <- Claude Code Skill (installed to ~/.claude/skills/he-proposal-review/)
commands/he-review.md<- /he-review slash command (installed to ~/.claude/commands/)
bin/he-review.js     <- npm CLI: installer + deterministic-step runner
rubrics/             <- the five authored review rubrics (full depth)
scripts/             <- deterministic: intake, extract, structural, pm, report
schemas/             <- JSON contracts for the internal files
he-review-workspace/ <- per-run inputs, internal JSON, figures, OUTPUT PDFs (in your project)
```

**Division of labour:** scripts find *what exists and where* + do exact PM/effort maths +
render PDFs; Claude does call analysis, the proposal map, figure visual review (reads
extracted PNGs), the five review passes, and the ESR synthesis. The model writes *findings
JSON*; a script renders it to PDF — so reports are reproducible.

## Status

All five rubrics are authored at full depth (Excellence · Impact · Implementation ·
Cross-Consistency · ESR). Reports 01–05 are produced at full fidelity.

## Design principles

Evaluate as submitted · evidence before judgement · confirm every structural candidate ·
figures only to vision (never whole pages) · scripts calculate, the model interprets ·
internal heuristics (e.g. PM ≤7%) are labelled internal, never presented as official HE
rules · no double-penalisation · the Final ESR contains no rewriting suggestions. Single
main workflow — no subagents.
