#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");

const packageRoot = path.resolve(__dirname, "..");
const skillSource = path.join(packageRoot, "skill", "skill-creator-v2");
const skillName = "skill-creator-v2";
const markerStart = "<!-- skill-creator-v2:start -->";
const markerEnd = "<!-- skill-creator-v2:end -->";

function usage() {
  console.log(`skill-creator-v2

Usage:
  skill-creator-v2 install --target <target>
  skill-creator-v2 install --all
  skill-creator-v2 list-targets
  skill-creator-v2 skill-path

Targets:
  codex, claude-code, gemini, antigravity, vs-codium, qwen, zai-glm, kimi, github-copilot

Options:
  --dry-run       Show planned writes without copying files. This is the default.
  --apply         Perform writes. Required for installation.
  --home <path>   Use a custom home directory for install targets.
`);
}

function parseArgs(argv) {
  const parsed = { command: argv[2] || "--help", targets: [], all: false, dryRun: true, home: os.homedir() };
  for (let i = 3; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--target") {
      const value = argv[i + 1];
      if (!value) throw new Error("--target requires a value");
      parsed.targets.push(value);
      i += 1;
    } else if (arg === "--all") {
      parsed.all = true;
    } else if (arg === "--dry-run") {
      parsed.dryRun = true;
    } else if (arg === "--apply") {
      parsed.dryRun = false;
    } else if (arg === "--home") {
      const value = argv[i + 1];
      if (!value) throw new Error("--home requires a value");
      parsed.home = path.resolve(value);
      i += 1;
    } else {
      throw new Error(`Unknown option: ${arg}`);
    }
  }
  return parsed;
}

function extensionSkillRoots(home, base) {
  const roots = [];
  const extensionDir = path.join(home, base, "extensions");
  if (!fs.existsSync(extensionDir)) return roots;
  for (const entry of fs.readdirSync(extensionDir)) {
    if (entry.startsWith("saoudrizwan.claude-dev-")) {
      roots.push(path.join(extensionDir, entry, ".agents", "skills", skillName));
    }
  }
  return roots;
}

function targetDefinitions(home) {
  return {
    codex: {
      paths: [path.join(home, ".codex", "skills", skillName)]
    },
    "claude-code": {
      paths: [path.join(home, ".claude", "skills", skillName)]
    },
    gemini: {
      paths: [
        path.join(home, ".gemini", "skills", skillName),
        path.join(home, ".gemini", "config", "skills", skillName)
      ]
    },
    antigravity: {
      paths: [
        path.join(home, ".antigravity", "skills", skillName),
        path.join(home, ".antigravity-ide", "skills", skillName),
        path.join(home, ".gemini", "antigravity-ide", "skills", skillName),
        path.join(home, ".gemini", "antigravity-backup", "skills", skillName)
      ]
    },
    "vs-codium": {
      paths: [
        path.join(home, ".agents", "skills", skillName),
        ...extensionSkillRoots(home, ".vscode-oss"),
        ...extensionSkillRoots(home, ".vscode")
      ]
    },
    qwen: {
      paths: [path.join(home, ".qwen", "skills", skillName)],
      projections: [path.join(home, ".qwen", "AGENTS.md")]
    },
    "zai-glm": {
      paths: [
        path.join(home, ".zai", "skills", skillName),
        path.join(home, ".glm", "skills", skillName)
      ],
      projections: [
        path.join(home, ".zai", "AGENTS.md"),
        path.join(home, ".glm", "AGENTS.md")
      ]
    },
    kimi: {
      paths: [path.join(home, ".kimi", "skills", skillName)],
      projections: [path.join(home, ".kimi", "AGENTS.md")]
    },
    "github-copilot": {
      paths: [path.join(home, ".copilot", "skills", skillName)]
    }
  };
}

function copySkill(src, dest, dryRun) {
  if (dryRun) {
    console.log(`[dry-run] copy ${src} -> ${dest}`);
    return;
  }
  fs.rmSync(dest, { recursive: true, force: true });
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.cpSync(src, dest, {
    recursive: true,
    force: true,
    filter(source) {
      const name = path.basename(source);
      return name !== "__pycache__" && name !== ".pytest_cache" && !name.endsWith(".pyc") && name !== ".DS_Store";
    }
  });
  console.log(`installed ${dest}`);
}

function projectionContent(targetFile) {
  const base = path.dirname(targetFile);
  const skillPath = path.join(base, "skills", skillName, "SKILL.md");
  return `${markerStart}
## skill-creator-v2

Local skill path:

- \`${skillPath}\`

Use this skill when creating, improving, evaluating, hardening, or packaging AI skills and skill groups. Before acting on such a request, read the full \`SKILL.md\` above and follow its reference-routing, production gates, eval discipline, final review, and packaging rules.

Do not replace an existing legacy \`skill-creator\` unless the user explicitly asks for that replacement.
${markerEnd}`;
}

function upsertProjection(file, dryRun) {
  const block = projectionContent(file);
  if (dryRun) {
    console.log(`[dry-run] upsert projection ${file}`);
    return;
  }
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const current = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "# Local Skills Projection\n";
  const start = current.indexOf(markerStart);
  const end = current.indexOf(markerEnd);
  let next;
  if (start !== -1 && end !== -1 && end > start) {
    next = `${current.slice(0, start)}${block}${current.slice(end + markerEnd.length)}`;
  } else {
    next = current.trimEnd() + "\n\n" + block + "\n";
  }
  fs.writeFileSync(file, next);
  console.log(`updated ${file}`);
}

function install(parsed) {
  if (!fs.existsSync(path.join(skillSource, "SKILL.md"))) {
    throw new Error(`Missing bundled skill at ${skillSource}`);
  }
  const defs = targetDefinitions(parsed.home);
  const names = parsed.all ? Object.keys(defs) : parsed.targets;
  if (names.length === 0) throw new Error("Choose --target <target> or --all");
  if (parsed.dryRun) {
    console.log("dry-run mode: no files will be written. Re-run with --apply to install.");
  }
  for (const name of names) {
    const def = defs[name];
    if (!def) throw new Error(`Unknown target: ${name}`);
    for (const dest of def.paths) copySkill(skillSource, dest, parsed.dryRun);
    for (const projection of def.projections || []) upsertProjection(projection, parsed.dryRun);
  }
}

function listTargets() {
  for (const name of Object.keys(targetDefinitions(os.homedir()))) console.log(name);
}

try {
  const parsed = parseArgs(process.argv);
  if (parsed.command === "--help" || parsed.command === "-h" || parsed.command === "help") {
    usage();
  } else if (parsed.command === "install") {
    install(parsed);
  } else if (parsed.command === "list-targets") {
    listTargets();
  } else if (parsed.command === "skill-path") {
    console.log(skillSource);
  } else {
    throw new Error(`Unknown command: ${parsed.command}`);
  }
} catch (error) {
  console.error(`error: ${error.message}`);
  process.exit(1);
}
