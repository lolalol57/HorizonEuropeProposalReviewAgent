#!/usr/bin/env node
"use strict";
/*
 * he-review — installer + deterministic-step runner for the Horizon Europe
 * proposal review agent (Claude Code).
 *
 *   he-review install [--quiet]   copy Skill + /he-review command into ~/.claude,
 *                                 then pip-install the Python deps
 *   he-review uninstall           remove the installed Skill + command
 *   he-review paths               show asset dir, workspace dir, inbox dir
 *   he-review intake [path] ...   run a deterministic step (pass-through to python)
 *   he-review extract   <run-id>
 *   he-review structural <run-id>
 *   he-review pm        <run-id>
 *   he-review report    <run-id>
 *   he-review review [path] ...   deterministic bookend: intake -> extract -> structural
 *
 * Claude does the reasoning passes between `structural` and `pm`/`report`.
 * Zero npm dependencies — Node built-ins only.
 */
const fs = require("fs");
const os = require("os");
const path = require("path");
const cp = require("child_process");

const ASSET_DIR = path.resolve(__dirname, "..");
const SKILL_NAME = "he-proposal-review";
const CLAUDE_DIR = path.join(os.homedir(), ".claude");
const SKILL_DEST = path.join(CLAUDE_DIR, "skills", SKILL_NAME);
const CMD_DEST = path.join(CLAUDE_DIR, "commands", "he-review.md");

// Map CLI verbs -> python script filenames.
const STEP_SCRIPTS = {
  intake: "intake.py",
  extract: "extract.py",
  structural: "structural_checks.py",
  pm: "pm_effort.py",
  report: "build_report.py",
};

function log(msg) {
  process.stdout.write(msg + "\n");
}
function warn(msg) {
  process.stderr.write(msg + "\n");
}

function pythonExe() {
  for (const exe of ["python3", "python"]) {
    try {
      cp.execFileSync(exe, ["--version"], { stdio: "ignore" });
      return exe;
    } catch (_) {
      /* keep trying */
    }
  }
  return null;
}

function pipExe() {
  for (const exe of ["pip3", "pip"]) {
    try {
      cp.execFileSync(exe, ["--version"], { stdio: "ignore" });
      return exe;
    } catch (_) {
      /* keep trying */
    }
  }
  return null;
}

// Run a bundled python script, inheriting stdio, from the user's cwd so that
// he-review-workspace/ lands in the current project. Returns exit code.
function runStep(step, args, opts) {
  const py = pythonExe();
  if (!py) {
    warn("Python 3 was not found on PATH. Install Python >=3.8 and re-run.");
    process.exit(2);
  }
  const script = path.join(ASSET_DIR, "scripts", STEP_SCRIPTS[step]);
  const res = cp.spawnSync(py, [script, ...args], {
    stdio: opts && opts.capture ? ["inherit", "pipe", "inherit"] : "inherit",
    cwd: process.cwd(),
    env: process.env,
    encoding: "utf8",
  });
  if (opts && opts.capture) {
    if (res.stdout) process.stdout.write(res.stdout);
    res.captured = res.stdout || "";
  }
  return res;
}

function copyInto(srcName, destDir) {
  const src = path.join(ASSET_DIR, srcName);
  if (!fs.existsSync(src)) return;
  const dest = path.join(destDir, srcName);
  fs.cpSync(src, dest, {
    recursive: true,
    filter: (s) => !s.includes("__pycache__") && !s.endsWith(".pyc"),
  });
}

function install(quiet) {
  // 1. Skill: SKILL.md at the skill root + a self-contained copy of the assets.
  fs.mkdirSync(SKILL_DEST, { recursive: true });
  fs.copyFileSync(path.join(ASSET_DIR, "skill", "SKILL.md"),
    path.join(SKILL_DEST, "SKILL.md"));
  for (const asset of ["PLAYBOOK.md", "rubrics", "scripts", "schemas",
    "requirements.txt"]) {
    copyInto(asset, SKILL_DEST);
  }

  // 2. Slash command.
  fs.mkdirSync(path.dirname(CMD_DEST), { recursive: true });
  fs.copyFileSync(path.join(ASSET_DIR, "commands", "he-review.md"), CMD_DEST);

  // 3. Python dependencies (best-effort — never fail the whole install on this).
  const pip = pipExe();
  const reqs = path.join(ASSET_DIR, "requirements.txt");
  let pipOk = false;
  if (pip) {
    const attempts = [
      [pip, ["install", "-r", reqs]],
      [pip, ["install", "--user", "-r", reqs]],
      [pip, ["install", "--break-system-packages", "-r", reqs]],
    ];
    for (const [exe, args] of attempts) {
      const r = cp.spawnSync(exe, args, { stdio: quiet ? "ignore" : "inherit" });
      if (r.status === 0) { pipOk = true; break; }
    }
  }

  if (!quiet) {
    log("");
    log("✓ Installed the he-proposal-review skill:");
    log("    " + SKILL_DEST);
    log("✓ Installed the /he-review command:");
    log("    " + CMD_DEST);
    if (pipOk) {
      log("✓ Python dependencies installed (PyMuPDF, python-docx, reportlab).");
    } else {
      warn("! Could not auto-install Python deps. Run manually:");
      warn("    pip3 install -r \"" + reqs + "\"");
    }
    log("");
    log("Next: open Claude Code in your project and run");
    log("    /he-review <proposal.pdf> \"<topic url|id|text>\" [RIA|IA|CSA]");
    log("  (or drop a proposal in ./inbox and just run /he-review)");
    log("Reports appear in ./he-review-workspace/<run-id>/OUTPUT/.");
  }
}

function uninstall() {
  let removed = false;
  if (fs.existsSync(SKILL_DEST)) {
    fs.rmSync(SKILL_DEST, { recursive: true, force: true });
    log("Removed skill: " + SKILL_DEST);
    removed = true;
  }
  if (fs.existsSync(CMD_DEST)) {
    fs.rmSync(CMD_DEST, { force: true });
    log("Removed command: " + CMD_DEST);
    removed = true;
  }
  if (!removed) log("Nothing to remove.");
}

function paths() {
  const ws = process.env.HE_REVIEW_WORKSPACE ||
    path.join(process.cwd(), "he-review-workspace");
  const inbox = process.env.HE_REVIEW_INBOX || path.join(process.cwd(), "inbox");
  log("asset dir : " + ASSET_DIR);
  log("skill dir : " + SKILL_DEST);
  log("command   : " + CMD_DEST);
  log("workspace : " + ws);
  log("inbox     : " + inbox);
}

function review(rest) {
  // Deterministic bookend: intake -> extract -> structural. Claude does the
  // reasoning passes afterwards, then `he-review pm` / `he-review report`.
  const r1 = runStep("intake", rest, { capture: true });
  if (r1.status !== 0) process.exit(r1.status || 1);
  const m = (r1.captured || "").match(/run_id=(\S+)/);
  if (!m) {
    warn("Could not determine run_id from intake output.");
    process.exit(1);
  }
  const runId = m[1];
  const r2 = runStep("extract", [runId]);
  if (r2.status !== 0) process.exit(r2.status || 1);
  const r3 = runStep("structural", [runId]);
  if (r3.status !== 0) process.exit(r3.status || 1);
  log("");
  log("Deterministic steps done for run: " + runId);
  log("Claude now: call analysis -> proposal map -> figure review -> 5 passes,");
  log("then:  he-review pm " + runId + "   and   he-review report " + runId);
}

function main() {
  const [cmd, ...rest] = process.argv.slice(2);
  switch (cmd) {
    case "install":
      return install(rest.includes("--quiet"));
    case "uninstall":
      return uninstall();
    case "paths":
      return paths();
    case "review":
      return review(rest);
    case "intake":
    case "extract":
    case "structural":
    case "pm":
    case "report": {
      const res = runStep(cmd, rest);
      process.exit(res.status || 0);
      break;
    }
    default:
      log("he-review — Horizon Europe proposal reviewer for Claude Code");
      log("");
      log("Usage:");
      log("  he-review install [--quiet]     install the Skill + /he-review command");
      log("  he-review uninstall             remove them");
      log("  he-review paths                 show asset / workspace / inbox dirs");
      log("  he-review review [path] ...     deterministic bookend (intake+extract+structural)");
      log("  he-review intake|extract|structural|pm|report [args]");
      log("");
      log("In Claude Code, use the /he-review command or ask to 'review this proposal'.");
      if (cmd && cmd !== "help" && cmd !== "--help" && cmd !== "-h") {
        process.exit(1);
      }
  }
}

main();
