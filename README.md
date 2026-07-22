<div align="center">

# Ai-Thinker Skills

</div>

[![中文](https://img.shields.io/badge/中文-README-blue)](README.zh.md)

AI agent skills for Ai-Thinker embedded product development — coding standards, code review, chip development guides, and peripheral driver templates. Supports MiMoCode, Claude Code, Codex, Cursor, and 70+ other platforms.

> **Note:** This repository is mirrored to GitHub for easy installation. The `npx skills add` command works with the GitHub repository.

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
| [embedded-code-review](./skills/embedded-code-review) | Ai-Thinker embedded C deep code review |
| [coder-ai-m62-m61](./skills/coder-ai-m62-m61) | BL616/BL618 development guide (Wi-Fi 6 + BLE 5.0) |
| [coder-ai-wb2](./skills/coder-ai-wb2) | Ai-WB2/BL602 development guide (Wi-Fi 4 + BLE 5.0) |
| [add-scbb-module](./skills/add-scbb-module) | Guide for adding new peripheral driver modules to AiPi-SCBB |
| [add-skills](./skills/add-skills) | Guide for adding new skills to this repo |
| [ota-generator](./skills/ota-generator) | Ai-Thinker embedded product OTA firmware generator |

### ai-thinker-c-coding-standard

Ai-Thinker embedded product C coding standard. Use when writing, modifying, reviewing, or refactoring any embedded C code, or when generating .c/.h files, adding function header comments, or checking code standards.

**Use cases:**
- Writing embedded C code
- Reviewing code standards compliance
- Generating Doxygen-style function headers

### embedded-code-review

Ai-Thinker embedded C deep code review skill. Covers safety, memory management, FreeRTOS task standards, ISR compliance, coding standard checks, and more.

**Use cases:**
- Embedded code security audit
- FreeRTOS task creation standards check
- Memory leak/overflow risk detection
- ISR compliance review
- Coding standard checklist verification

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

## Repository Structure

```
skills/
├── skills/                          # All skills are stored here
│   └── ai-thinker-c-coding-standard/
│       ├── SKILL.md                # Skill main file (required)
│       ├── scripts/                # Helper scripts (optional)
│       ├── references/             # Documentation loaded on demand (optional)
│       └── assets/                 # Files used in output (optional)
├── .coding-ci.yml                  # Coding CI/CD configuration
├── bin/                            # CLI tools
│   └── cli.js                      # seahi-skills CLI
├── scripts/                        # Build and release scripts
│   ├── validate.mjs                # Validate SKILL.md files
│   ├── build.mjs                   # Build skills to dist/
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

### Step 4: Validate Your Skill

```bash
# From the repo root
npm run validate
```

Expected output:
```
🔍 Validating skills...

✅ skills/my-new-skill/SKILL.md

📊 Found 2 skill(s)

✅ All skills are valid
```

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
ln -s $(pwd)/skills/add-scbb-module ~/.claude/skills/add-scbb-module
ln -s $(pwd)/skills/add-skills ~/.claude/skills/add-skills
```

### Scope

| Scope | Location | Use Case |
|-------|----------|----------|
| **Global** | `~/.<agent>/skills/` | Available across all projects |
| **Project** | `./<agent>/skills/` | Committed with your project, shared with team |

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

# Build skills to dist/
npm run build

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

## License

MIT
