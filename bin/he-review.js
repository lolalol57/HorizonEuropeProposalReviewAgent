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
 *   he-review checklist <run-id>
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

// Install targets. Default = user scope (~/.claude, available in every Claude Code
// project). With --local = project scope (./.claude, only the current project) — no
// global npm, no sudo, no ~/.claude change.
function targets(local) {
  const base = path.join(local ? process.cwd() : os.homedir(), ".claude");
  return {
    base,
    scope: local ? "proje-yerel (./.claude)" : "kullanıcı-geneli (~/.claude)",
    skillDest: path.join(base, "skills", SKILL_NAME),
    cmdDest: path.join(base, "commands", "he-review.md"),
  };
}

// Map CLI verbs -> python script filenames.
const STEP_SCRIPTS = {
  intake: "intake.py",
  extract: "extract.py",
  structural: "structural_checks.py",
  pm: "pm_effort.py",
  report: "build_report.py",
  checklist: "build_checklist.py",
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

function install(quiet, local) {
  const t = targets(local);
  // 1. Skill: SKILL.md at the skill root + a self-contained copy of the assets.
  fs.mkdirSync(t.skillDest, { recursive: true });
  fs.copyFileSync(path.join(ASSET_DIR, "skill", "SKILL.md"),
    path.join(t.skillDest, "SKILL.md"));
  for (const asset of ["PLAYBOOK.md", "rubrics", "scripts", "schemas",
    "requirements.txt"]) {
    copyInto(asset, t.skillDest);
  }

  // 2. Slash command.
  fs.mkdirSync(path.dirname(t.cmdDest), { recursive: true });
  fs.copyFileSync(path.join(ASSET_DIR, "commands", "he-review.md"), t.cmdDest);

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
    log("✓ Kurulum kapsamı: " + t.scope);
    log("✓ Skill      : " + t.skillDest);
    log("✓ /he-review : " + t.cmdDest);
    if (pipOk) {
      log("✓ Python bağımlılıkları kuruldu (PyMuPDF, python-docx, reportlab).");
    } else {
      warn("! Python bağımlılıkları otomatik kurulamadı. Elle çalıştır:");
      warn("    pip3 install -r \"" + reqs + "\"");
    }
    log("");
    if (local) {
      log("Bu proje için kuruldu. Claude Code'u BU klasörde açıp çalıştır:");
    } else {
      log("Sonraki adım: Claude Code'u projende açıp çalıştır:");
    }
    log("    /he-review <oneri.pdf> \"<topic url|id|metin>\" [RIA|IA|CSA]");
    log("  (veya öneriyi ./inbox'a bırakıp sadece /he-review)");
    log("Raporlar ./he-review-workspace/<run-id>/OUTPUT/ içine düşer.");
  }
}

function uninstall(local) {
  const t = targets(local);
  let removed = false;
  if (fs.existsSync(t.skillDest)) {
    fs.rmSync(t.skillDest, { recursive: true, force: true });
    log("Removed skill: " + t.skillDest);
    removed = true;
  }
  if (fs.existsSync(t.cmdDest)) {
    fs.rmSync(t.cmdDest, { force: true });
    log("Removed command: " + t.cmdDest);
    removed = true;
  }
  if (!removed) log("Nothing to remove at " + t.scope + ".");
}

function paths() {
  const user = targets(false), local = targets(true);
  const ws = process.env.HE_REVIEW_WORKSPACE ||
    path.join(process.cwd(), "he-review-workspace");
  const inbox = process.env.HE_REVIEW_INBOX || path.join(process.cwd(), "inbox");
  log("asset dir        : " + ASSET_DIR);
  log("skill (user)     : " + user.skillDest);
  log("command (user)   : " + user.cmdDest);
  log("skill (--local)  : " + local.skillDest);
  log("command (--local): " + local.cmdDest);
  log("workspace        : " + ws);
  log("inbox            : " + inbox);
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
  log("then:  he-review pm " + runId + "   report " + runId + "   checklist " + runId);
}

function main() {
  const [cmd, ...rest] = process.argv.slice(2);
  const local = rest.includes("--local") || rest.includes("-l");
  switch (cmd) {
    case "install":
      return install(rest.includes("--quiet"), local);
    case "uninstall":
      return uninstall(local);
    case "paths":
      return paths();
    case "review":
      return review(rest);
    case "intake":
    case "extract":
    case "structural":
    case "pm":
    case "report":
    case "checklist": {
      const res = runStep(cmd, rest);
      process.exit(res.status || 0);
      break;
    }
    default:
      log("he-review — Horizon Europe proposal reviewer for Claude Code");
      log("");
      log("Usage:");
      log("  he-review install [--local] [--quiet]  install the Skill + /he-review command");
      log("  he-review uninstall [--local]          remove them");
      log("  he-review paths                        show install/workspace/inbox dirs");
      log("  he-review review [path] ...            deterministic bookend (intake+extract+structural)");
      log("  he-review intake|extract|structural|pm|report|checklist [args]");
      log("");
      log("  --local : install into THIS project's ./.claude (only this project),");
      log("            instead of the user-wide ~/.claude. No global npm / sudo needed.");
      log("");
      log("In Claude Code, use the /he-review command or ask to 'review this proposal'.");
      if (cmd && cmd !== "help" && cmd !== "--help" && cmd !== "-h") {
        process.exit(1);
      }
  }
}

main();
