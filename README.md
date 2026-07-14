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

One command:

```bash
npm install -g github:lolalol57/HorizonEuropeProposalReviewAgent
```

That's it. The package's `postinstall` automatically runs `he-review install`, which copies
the Skill + `/he-review` command into `~/.claude/` and installs the Python deps. Then open
Claude Code in your project and run `/he-review <proposal.pdf> "<topic>"`.

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

The npm package name is **`he-proposal-review`**. It is not published to the public npm
registry yet, so install from GitHub as shown above. To publish it yourself later, run
`npm login` then `npm publish` from the repo — after that anyone could install it with
`npm install -g he-proposal-review`.

### Permission error (`EACCES`) on `npm install -g`?

`EACCES: permission denied, mkdir '/usr/local/lib/node_modules/...'` means your **global**
npm folder is owned by root — it's a general npm permissions issue, not specific to this
package. Easiest sudo-free fix (recommended): skip the global install and run the installer
via npx —

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

## Use

Open Claude Code in the project where you want the reports, then either:

```
/he-review path/to/proposal.pdf "<topic URL, ID, or text>" RIA
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

## Status

All five rubrics are authored at full depth (Excellence · Impact · Implementation ·
Cross-Consistency · ESR). Reports 01–05 are produced at full fidelity.
