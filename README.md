# Horizon Europe Proposal Review Agent

A **proposal-review agent for Claude Code** that reviews Horizon Europe proposals in a
structured, evidence-based, evaluator-oriented way and produces five ESR-style PDF reports
(Excellence · Impact · Implementation · Cross-Consistency · Final ESR).

It installs as an **npm package**: a small CLI drops a Claude Code **Skill** + a
`/he-review` **command** into `~/.claude/`, and installs the Python deps. Claude itself does
the reviewing (call analysis, figure vision, the five passes, the ESR); bundled Python
scripts do only the deterministic work — extraction, Person-Month maths, and PDF rendering.

## Quick start (Claude Code)

```bash
npm install -g github:lolalol57/HorizonEuropeProposalReviewAgent
```

The package's `postinstall` runs `he-review install` for you — it copies the Skill +
`/he-review` command into `~/.claude/` and installs the Python deps. Then open Claude Code in
your project and run:

```
/he-review path/to/proposal.pdf "<topic URL, ID, or text>" RIA
```

Five PDFs land in `./he-review-workspace/<run-id>/OUTPUT/`.

## How it works

You point the agent at a proposal and its official call/topic. From there:

1. **Deterministic scripts** extract the text, tables and figures, run structural checks, and
   compute the Person-Month / work-package effort maths. They only find *what exists and
   where* — they never judge quality.
2. **Claude does the reasoning** — it maps the call requirements, reviews the figures with
   vision, builds the proposal's traceability map, then works through each rubric
   (`rubrics/*.md`) to write structured findings.
3. **A script renders** those findings into the five PDF reports.

You stay in the driver's seat the whole time: Claude tells you the run ID, what it's doing at
each step, and where the reports land.

## What you get

Five PDFs in `./he-review-workspace/<run-id>/OUTPUT/`:

- **`01_Excellence_Review.pdf`**, **`02_Impact_Review.pdf`**, **`03_Implementation_Review.pdf`**,
  **`04_Cross_Consistency_Call_and_Document_Audit.pdf`** — the **detailed internal reports**.
  Each one is a *broad rubric-coverage* review: the agent works through every module of the
  matching rubric and records a status for each checkpoint —
  ✅ adequate · ⚠️ partial · ❌ missing · ➖ not applicable — with the evidence it relied on, an
  assessment, and a concrete suggested improvement. These are the working documents you use to
  strengthen the proposal.
- **`05_Final_ESR.pdf`** — the **concise evaluator summary**. Per criterion it gives the score
  and short bullet lists of **Strengths**, **Weaknesses**, and an **Evaluator comment**, then
  the total `/ 15.0` and an overall assessment. It reads like a real ESR: it evaluates the
  proposal *as submitted* and deliberately contains **no rewriting suggestions**.

Everything — the reports and all intermediate artefacts — lands in your **current project
directory**, never inside `~/.claude`.

## Use

Open Claude Code in the project where you want the reports, then either pass the proposal
explicitly:

```
/he-review path/to/proposal.pdf "<topic URL, ID, or text>" RIA
```

…or drop a proposal into an `inbox/` folder and just run `/he-review` (the newest file is
picked up). You can also ask in natural language — *"review this Horizon Europe proposal"* —
and the `he-proposal-review` skill triggers.

**Arguments:** `[proposal path] [topic url|id|"text"] [RIA|IA|CSA]`. The path is optional
(newest file in `./inbox/` is used if omitted); the **topic is strongly recommended** — it
drives the call-requirements analysis, so Claude will ask for it if you don't provide one. The
Type of Action is inferred from the topic when omitted.

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

`he-review install` runs automatically on global npm install; run it explicitly if you want to
see the output or re-run it. Remove everything with `he-review uninstall`.

### Project-local install (no global npm, no sudo, no `~/.claude`)

By default the Skill + command are installed **user-wide** to `~/.claude/`, so `/he-review` is
available in every Claude Code project. To scope it to a **single project** instead, use
`--local` — it installs into that project's `./.claude/` only:

```bash
cd ~/my-project
npx github:lolalol57/HorizonEuropeProposalReviewAgent install --local
```

This avoids the global npm folder entirely (so no `EACCES`/sudo) and touches nothing outside
the current project. Remove it with `he-review uninstall --local`.

The npm package name is **`he-proposal-review`**. It is not published to the public npm
registry yet, so install from GitHub as shown above. To publish it yourself, run `npm login`
then `npm publish` from the repo — after that anyone can install it with
`npm install -g he-proposal-review`.

### Permission error (`EACCES`) on `npm install -g`?

`EACCES: permission denied, mkdir '/usr/local/lib/node_modules/...'` means your **global** npm
folder is owned by root — a general npm permissions issue, not specific to this package. The
easiest sudo-free fix is to skip the global install and run the installer via npx:

```bash
npx github:lolalol57/HorizonEuropeProposalReviewAgent install
```

Or give npm a user-owned global prefix, then re-run the global install:

```bash
mkdir -p ~/.npm-global && npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zshrc && source ~/.zshrc
npm install -g github:lolalol57/HorizonEuropeProposalReviewAgent
```

(Last resort: `sudo npm install -g …` — works but creates root-owned files.)

## CLI reference

The skill uses this CLI, but you can also run it by hand:

```bash
he-review install | uninstall | paths                            # manage the install
he-review review [path] --topic "<...>" [--action RIA|IA|CSA]    # intake+extract+structural
he-review intake | extract | structural | pm | report [args]     # individual steps
```

`he-review review` runs the deterministic bookend (intake → extract → structural); Claude then
does the reasoning passes and finishes with `he-review pm <run-id>` and
`he-review report <run-id>`. Set `HE_REVIEW_WORKSPACE` / `HE_REVIEW_INBOX` to override the
default `./he-review-workspace` and `./inbox` locations.

The full 13-step workflow, the rubrics, the status system and scoring live in `PLAYBOOK.md`,
which is the single source of truth for the agent.
