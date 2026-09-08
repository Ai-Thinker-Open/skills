<div align="center">

# Ai-Thinker Skills

</div>

[![中文](https://img.shields.io/badge/中文-README-blue)](README.zh.md)

AI agent skills for Ai-Thinker embedded product development — coding standards, code review, chip development guides, and peripheral driver templates. Supports MiMoCode, Claude Code, Codex, Cursor, and 70+ other platforms.

> **Note:** This repository is mirrored to GitHub for easy installation. The `npx skills add` command works with the GitHub repository.

## Introduction

This repository is a curated collection of AI agent skills built for
Ai-Thinker embedded product development. It covers coding standards, deep
code review, chip/module development guides (BL602/BL616/BL618), peripheral
driver templates, and module selection, and follows the open
[Agent Skills](https://agentskills.io) specification so the same skills work
across MiMoCode, Claude Code, Codex, Cursor and 70+ other platforms.

## Quick Start

### Method 0: Using npx (Recommended)

```bash
# Install all skills
npx skills add Ai-Thinker-Open/skills

# Install specific skill
npx skills add Ai-Thinker-Open/skills --skill ai-thinker-c-coding-standard
```

### Method 1: Clone and Copy

```bash
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills

# For Claude Code
cp -r skills/ai-thinker-c-coding-standard ~/.claude/skills/

# For MiMoCode / OpenCode
cp -r skills/ai-thinker-c-coding-standard ~/.opencode/skills/

# For project-level usage
cp -r skills/ai-thinker-c-coding-standard ./<agent>/skills/
```

### Method 2: Symlink (Recommended for Development)

```bash
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills

ln -s $(pwd)/skills/ai-thinker-c-coding-standard ~/.claude/skills/ai-thinker-c-coding-standard
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [ai-thinker-c-coding-standard](./skills/ai-thinker-c-coding-standard) | Ai-Thinker embedded C coding standard |
| [ai-thinker-bl-coredump-skill](./skills/ai-thinker-bl-coredump-skill) | Ai-Thinker Bouffalo (BL series) coredump crash debugging (log parsing + GDB RSP + task_dump) |
| [board-pins](./skills/board-pins) | Ai-Thinker development board pin configuration lookup (pin map, pin reuse/conflict, per-board references) |
| [embedded-code-review](./skills/embedded-code-review) | Ai-Thinker embedded C deep code review |
| [coder-ai-m62-m61](./skills/coder-ai-m62-m61) | BL616/BL618 development guide (Wi-Fi 6 + BLE 5.0) |
| [coder-ai-wb2](./skills/coder-ai-wb2) | Ai-WB2/BL602 development guide (Wi-Fi 4 + BLE 5.0) |
| [coder-ra-01sc](./skills/coder-ra-01sc) | Ra-01SC series LoRa module development guide (LLCC68, sub-GHz over SPI) |
| [combo-at-commands](./skills/combo-at-commands) | Ai-Thinker Combo AT command development assistant (WiFi/MQTT/Socket/BLE/HTTP/SNTP/GPIO/PWM) |
| [module-selector](./skills/module-selector) | Module selection assistant (WiFi/LoRa/Radar/UWB/NearLink) |
| [scbb-module-finder](./skills/scbb-module-finder) | SCBB module finder from AiPi-SCBB repository |
| [add-scbb-module](./skills/add-scbb-module) | Guide for adding new peripheral driver modules to AiPi-SCBB |
| [add-skills](./skills/add-skills) | Guide for adding new skills to this repo |
| [ota-generator](./skills/ota-generator) | Ai-Thinker embedded product OTA firmware generator |
| [cmw-wlan-test](./skills/cmw-wlan-test) | WLAN signaling test SOP for CMW-500 + AmebaDplus (TX power/EVM/RX sensitivity) |

### ai-thinker-c-coding-standard

Ai-Thinker embedded product C coding standard. Use when writing, modifying, reviewing, or refactoring any embedded C code, or when generating .c/.h files, adding function header comments, or checking code standards.

**Use cases:**
- Writing embedded C code
- Reviewing code standards compliance
- Generating Doxygen-style function headers

### ai-thinker-bl-coredump-skill

Ai-Thinker Bouffalo (BL series) coredump crash debugging skill. Use when the user provides a crash log or coredump file path, or asks to analyze a crash / coredump / GDB debugging. Automates log parsing, port allocation, GDB RSP server startup and GDB connection.

**Use cases:**
- Analyzing crash logs and coredump files (serial log or flash `crash.bin`)
- Recovering crashed task call stack, registers and memory
- GDB debugging with `task_dump` / `task_list_ready` / `task_list_wait`

### embedded-code-review

Ai-Thinker embedded C deep code review skill. Covers safety, memory management, FreeRTOS task standards, ISR compliance, coding standard checks, and more.

**Use cases:**
- Embedded code security audit
- FreeRTOS task creation standards check
- Memory leak/overflow risk detection
- ISR compliance review
- Coding standard checklist verification

### board-pins

Ai-Thinker development board pin configuration lookup. Use when the user asks which pin / GPIO connects to what on a specific dev board, wants a pin map or pin definition table, or needs to check pin reuse and conflicts. Board data is stored as one reference document per board under `references/`.

**Use cases:**
- Querying a dev board's pin definition table (pin → function)
- Finding an available pin for a peripheral (function → pin: GPIO/SPI/IIC/ADC/PWM/UART)
- Checking pin reuse / conflicts and default NC or Flash-shared pins that must be avoided
- Power pins (3V3/5V/GND), default serial port (TX/RX), LEDs and buttons

Currently supported boards (one reference file per board under `references/`; see [`references/kit-boards-index.md`](./skills/board-pins/references/kit-boards-index.md) for the full catalog and spec links):
- `Ai-WB2-12F-Kit` (manually verified)
- All other `-Kit` dev boards (Ai-M6x/Ai-WBx/BWx/TG, PB/TB, Ai-BS21/Ai-WS1, LoRa/Ra-08, Rd-60/Rd-Kit, BU03/04/NodeMCU-BU01, VC-01/02, GP-01/02, EC-01/01F/01G) — auto-parsed from official spec sheets; **verify against the spec before wiring**.

### coder-ai-m62-m61

Ai-Thinker BL616/BL618 series module development guide - Wi-Fi 6 + BLE 5.0 module, based on bouffalo_sdk.

**Use cases:**
- Developing with BL616/BL618 modules
- GPIO, UART, SPI, I2C, DMA programming
- Wi-Fi and BLE connectivity

### coder-ai-wb2

Ai-Thinker Ai-WB2 series module development guide (BL602 chip) - Wi-Fi 4 + BLE 5.0 module.

**Use cases:**
- Developing with Ai-WB2 modules
- Peripheral programming (GPIO, UART, PWM, ADC)
- MQTT, HTTP network protocols

### coder-ra-01sc

Ai-Thinker Ra-01SC series LoRa module development guide (LLCC68 chip, covering Ra-01SC/Ra-01SC-P/Ra-01SCH/Ra-01SCH-P) - sub-GHz RF transceiver controlled via SPI, covering LoRa (SF5-11, 125/250/500kHz), (G)FSK 0.6-300kbps, CAD, SPI command protocol, TX/RX programming and driver porting.

**Use cases:**
- Developing with Ra-01SC series LoRa modules (Ra-01SC/SCH and -P variants)
- LoRa/GFSK point-to-point communication over SPI
- Porting the official LLCC68 driver to a new platform

### combo-at-commands

Ai-Thinker Combo module AT command development assistant. Covers the Combo
framework AT command set (V4.18P_3.8.0) for Ai-WB2 (BL602) and Ai-M61/M62
(BL616/BL618) modules — WiFi, MQTT, Socket, BLE, HTTP, SNTP, GPIO, PWM and
more.

**Use cases:**
- Developing IoT features with AT commands
- Looking up AT command usage and parameters
- Troubleshooting AT command / URC event issues
- Planning AT command execution flows

### module-selector

Ai-Thinker module selection assistant. Supports Wi-Fi, BLE, LoRa, Radar, UWB, NearLink, NB-IoT and other module recommendations with datasheet links.

**Use cases:**
- IoT module selection
- Wireless communication module recommendation
- Module specification comparison

### scbb-module-finder

SCBB module finder. Searches and retrieves peripheral driver modules from AiPi-SCBB repository, supporting I2C, UART, SPI, PWM+DMA protocols.

**Use cases:**
- Finding sensor drivers
- Getting peripheral module code
- SCBB framework integration

### add-scbb-module

Guide for adding new peripheral driver modules to the AiPi-SCBB library. Follows the `AXK_<module>_<protocol>_ACLL` macro pattern and Ai-Thinker C coding standard.

**Use cases:**
- Adding new peripheral drivers to SCBB framework
- Creating I2C, UART, SPI, PWM+DMA, or GPIO modules
- Following SCBB naming conventions and macro patterns
- Integrating BSP functions with SCBB abstraction layer

### add-skills

Guide for adding new skills to this repository.

**Use cases:**
- Creating a new skill
- Learning skill format and structure
- Validating skills

### ota-generator

Ai-Thinker embedded product OTA firmware generator. Supports two modes: add MD5 header to existing firmware, or compile from source and generate OTA package.

**Use cases:**
- Generating OTA upgrade firmware
- Adding MD5 header to firmware files
- Compiling from source to create OTA packages

### cmw-wlan-test

WLAN signaling-based measurement SOP for the R&S CMW-500 + Realtek AmebaDplus bench. Pure-SCPI workflow covers TX power, EVM, RX sensitivity, CCK/HT-MCS, and full compliance runs on 2.4 GHz / 5 GHz.

**Use cases:**
- Running TX power / EVM / RX-sensitivity measurements
- 802.11a/b/g/n signaling tests
- Full compliance test runs and report generation

## Repository Structure

```
skills/
├── skills/                          # All skills are stored here
│   └── ai-thinker-c-coding-standard/
│       ├── SKILL.md                # Skill main file (required)
│       ├── scripts/                # Helper scripts (optional)
│       ├── references/             # Documentation loaded on demand (optional)
│       └── assets/                 # Files used in output (optional)
├── skills-manifest.json            # Content hashes for remote update checks
├── .coding-ci.yml                  # Coding CI/CD configuration
├── bin/                            # CLI tools
│   └── cli.js                      # seahi-skills CLI
├── scripts/                        # Build and release scripts
│   ├── validate.mjs                # Validate SKILL.md files
│   ├── generate-manifest.mjs       # Regenerate skills-manifest.json
│   ├── check-updates.mjs           # Check/apply remote skill updates
│   ├── build.mjs                   # Build skills to dist/
│   ├── install.mjs                 # Install skills to user directories
│   └── release.sh                  # Local release script
├── README.md                       # English documentation
├── README.zh.md                    # Chinese documentation
├── package.json
└── skills.sh.json                  # skills.sh discovery config
```

## Creating a New Skill

### Step 1: Create the Skill Directory

```bash
cd skills/
mkdir my-new-skill
cd my-new-skill
```

### Step 2: Create SKILL.md

Create `SKILL.md` with YAML frontmatter. The `description` field is the primary trigger - agents use it to decide when to activate this skill.

```markdown
---
name: my-new-skill
description: What this skill does and when to use it. Include trigger phrases like "when user asks to X" or "for Y tasks".
---

# My Skill Title

Instructions for the agent to follow when this skill is activated.

## When to Use

Describe the scenarios where this skill should be used.

## Steps

1. First, do this
2. Then, do that
```

### Step 3: (Optional) Add Resource Directories

```bash
mkdir scripts    # Executable helper scripts (Python/Bash/Node)
mkdir references # Documentation loaded on demand by the agent
mkdir assets     # Templates, images, fonts used in output
```

### Step 4: Regenerate the Manifest and Validate

Every skill change must be reflected in `skills-manifest.json` — the remote
update check relies on it, and `npm run validate` fails if the manifest is
stale.

```bash
# From the repo root
npm run manifest    # Refresh skills-manifest.json
npm run validate    # Validate SKILL.md format + manifest freshness
```

Expected output:
```
🔍 Validating skills...

✅ skills/my-new-skill/SKILL.md

📊 Found N skill(s)

📋 Checking skills-manifest.json...
✅ skills-manifest.json is up to date

✅ All skills are valid
```

### Step 5: Commit and Push

```bash
# Stage the new skill together with the refreshed manifest
git add skills/my-new-skill skills-manifest.json
git commit -m "feat(skills): add my-new-skill"

# Keep both mirrors in sync
git push github master
git push origin master
```

Once pushed, other clones will detect the new skill as `🆕 远端新增` with
`npm run check:updates` (see [Checking for Updates](#checking-for-updates)).
Remember to run `npm run manifest` again whenever you edit an existing skill.

### Skill Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (lowercase, hyphens only) |
| `description` | Yes | What the skill does + when to use it (this triggers activation) |
| `metadata.internal` | No | Set `true` to hide from normal discovery |

### Example: Complete Skill

```
skills/
└── code-review/
    ├── SKILL.md              # Main skill file
    ├── scripts/
    │   └── lint.sh           # Helper script
    └── references/
        └── style-guide.md    # Reference docs
```

`skills/code-review/SKILL.md`:
```markdown
---
name: code-review
description: Review code for quality, security, and best practices. Use when user asks to review, audit, or check code.
---

# Code Review Skill

Review code changes following these guidelines.

## Steps

1. Check for security vulnerabilities
2. Verify error handling
3. Review naming conventions
4. Suggest improvements
```

### Directory Structure Reference

```
skills/
└── <skill-name>/                 # Skill name (lowercase, hyphens)
    ├── SKILL.md                  # REQUIRED: Main skill file
    ├── scripts/                  # OPTIONAL: Executable scripts
    │   └── helper.py
    ├── references/               # OPTIONAL: Docs loaded on demand
    │   └── api-docs.md
    └── assets/                   # OPTIONAL: Output templates/files
        └── template.html
```

## Installation

### Method 0: Using npx (Recommended)

```bash
# Install a specific skill
npx skills add Ai-Thinker-Open/skills/skills/ai-thinker-c-coding-standard

# Or clone the entire repository
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills
```

### Method 1: Clone and Copy

```bash
# Clone the repository
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills

# Copy specific skill to Claude Code (global)
cp -r skills/ai-thinker-c-coding-standard ~/.claude/skills/

# Copy specific skill to MiMoCode (global)
cp -r skills/ai-thinker-c-coding-standard ~/.opencode/skills/

# Copy to project directory (project-level)
mkdir -p .claude/skills
cp -r skills/ai-thinker-c-coding-standard .claude/skills/
```

### Method 2: Symlink (Recommended for Development)

```bash
# Clone the repository
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills

# Create symlinks for all skills
ln -s $(pwd)/skills/ai-thinker-c-coding-standard ~/.claude/skills/ai-thinker-c-coding-standard
ln -s $(pwd)/skills/embedded-code-review ~/.claude/skills/embedded-code-review
ln -s $(pwd)/skills/coder-ai-m62-m61 ~/.claude/skills/coder-ai-m62-m61
ln -s $(pwd)/skills/coder-ai-wb2 ~/.claude/skills/coder-ai-wb2
ln -s $(pwd)/skills/coder-ra-01sc ~/.claude/skills/coder-ra-01sc
ln -s $(pwd)/skills/add-scbb-module ~/.claude/skills/add-scbb-module
ln -s $(pwd)/skills/add-skills ~/.claude/skills/add-skills
```

### Scope

| Scope | Location | Use Case |
|-------|----------|----------|
| **Global** | `~/.<agent>/skills/` | Available across all projects |
| **Project** | `./<agent>/skills/` | Committed with your project, shared with team |

## Checking for Updates

The repository keeps a `skills-manifest.json` at the root with deterministic
SHA-256 content hashes for every skill. It is compared against the manifest on
the GitHub (`github`) and Coding (`origin`) remotes to report when skills have
changed upstream.

```bash
# Check both remotes (default branch: master)
npm run check:updates

# Only check one remote
npm run check:updates -- --remote github

# Check against a different branch
npm run check:updates -- --branch main

# Apply remote changes to skills/ and refresh installed copies
npm run check:updates -- --update
```

Status icons:

| Icon | Meaning |
|------|---------|
| ✅ | Local matches the remote |
| ⬆️ | Remote has new content |
| 🆕 | New skill exists on the remote |
| 🗑 | Skill was removed on the remote |
| ⚠️ | Remotes disagree — resolve manually |

`--update` only restores the changed skill directories into the working tree —
it never stages or commits, so you can review the changes before committing.
It skips a skill when the local directory has uncommitted changes, or when the
two remotes provide different content for the same skill. After applying
changes it refreshes installed copies (only in directories that already
contain the skill, e.g. `~/.codex/skills`, `~/.claude/skills`), regenerates
`skills-manifest.json` in the working tree, and runs `npm run validate`.

Exit codes: `0` everything is up to date, `1` updates are available (or some
were skipped), `2` a remote is unreachable / missing the manifest, or an
internal error occurred.

## Supported Platforms

Skills follow the [Agent Skills specification](https://agentskills.io) and work with:

| Platform | Agent Flag |
|----------|------------|
| MiMoCode | `opencode` |
| Claude Code | `claude-code` |
| Codex | `codex` |
| Cursor | `cursor` |
| OpenCode | `opencode` |
| GitHub Copilot | `github-copilot` |
| Gemini CLI | `gemini-cli` |
| Windsurf | `windsurf` |
| Cline | `cline` |
| Roo Code | `roo` |
| + 60 more | See [full list](https://agentskills.io#supported-agents) |

## Development

### Local Development

```bash
# Validate all skills
npm run validate

# Regenerate skills-manifest.json after editing skills
npm run manifest

# Check GitHub/Coding remotes for skill updates
npm run check:updates

# Build skills to dist/
npm run build

# Install skills to ~/.claude/skills and ~/.codex/skills
npm run install:all

# Install specific skill
node scripts/install.mjs module-selector

# Run CLI
node bin/cli.js list
```

### Releasing

```bash
# Bump patch version (0.0.1 -> 0.0.2)
npm version patch --no-git-tag-version

# Commit changes
git add package.json
git commit -m "chore: release v0.0.2"

# Create tag
git tag -a v0.0.2 -m "Release v0.0.2"

# Push
git push origin main --tags
```

### CI/CD

Project uses `.coding-ci.yml` to configure Coding platform CI/CD pipeline.

| Stage | Trigger | Description |
|-------|---------|-------------|
| validate | All pushes | Validate SKILL.md format |
| build | All pushes | Build dist/ directory |

## FAQ / Troubleshooting

**`npm run check:updates` exits with code 2.**
The remote is unreachable, or the checked branch has no
`skills-manifest.json`. Push the manifest to both remotes first, then retry.

**`npm run validate` reports `skills-manifest.json is out of date`.**
Run `npm run manifest` to regenerate the manifest, then commit it together
with your skill changes.

**How do I install just one skill?**
Use `node scripts/install.mjs <skill-name>` from the repo root, or
`npx skills add Ai-Thinker-Open/skills --skill <skill-name>`.

## Contributing

Contributions are welcome. To add a new skill, follow the steps in
[Creating a New Skill](#creating-a-new-skill) above, or read the
[add-skills](./skills/add-skills) guide. After changing any skill, run
`npm run manifest` and `npm run validate`, then commit and push to both the
GitHub (`github`) and Coding (`origin`) remotes so the mirrors stay in sync.

## License

[MIT](./LICENSE)
