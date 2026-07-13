# Agent Skills Collection

A cross-platform collection of AI agent skills, supporting MiMoCode, Claude Code, Codex, Cursor, and 69+ other platforms.

[![skills.sh](https://skills.sh/b/seahi/skills)](https://skills.sh/seahi/skills)

## Quick Start

### Install All Skills

```bash
npx skills add seahi/skills
```

### Install Specific Skills

```bash
npx skills add seahi/skills --skill ai-thinker-c-coding-standard
```

### Use Without Installing

```bash
# Pipe to an agent
npx skills use seahi/skills@ai-thinker-c-coding-standard | claude

# Start agent interactively
npx skills use seahi/skills --skill ai-thinker-c-coding-standard --agent claude-code
```

## Available Skills

### ai-thinker-c-coding-standard

Ai-Thinker embedded product C coding standard. Use when writing, modifying, reviewing, or refactoring any embedded C code, or when generating .c/.h files, adding function header comments, or checking code standards.

**Use cases:**
- Writing embedded C code
- Reviewing code standards compliance
- Generating Doxygen-style function headers

**Key requirements:**
- Doxygen-style function headers for public interfaces in `.h` files
- Unified prefixes (`axk`/`aiio`/`ai`) for identifiers
- 4-space indentation (no tabs)
- Parameter validation
- Standardized file organization

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
├── README.zh.md                    # 中文说明
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

## Installation Options

### Scope

| Scope | Flag | Location | Use Case |
|-------|------|----------|----------|
| **Project** | (default) | `./<agent>/skills/` | Committed with your project, shared with team |
| **Global** | `-g` | `~/<agent>/skills/` | Available across all projects |

### Installation Methods

| Method | Description |
|--------|-------------|
| **Symlink** (Recommended) | Creates symlinks from each agent to a canonical copy. Single source of truth, easy updates. |
| **Copy** | Creates independent copies for each agent. Use when symlinks aren't supported. |

### Common Commands

```bash
# List available skills in a repository
npx skills add seahi/skills --list

# Install to specific agents
npx skills add seahi/skills -a claude-code -a opencode

# Install globally
npx skills add seahi/skills -g

# Non-interactive installation (CI/CD)
npx skills add seahi/skills --skill ai-thinker-c-coding-standard -g -a claude-code -y

# Install all skills to all agents
npx skills add seahi/skills --all

# List installed skills
npx skills list

# Update installed skills
npx skills update

# Remove installed skills
npx skills remove my-skill
```

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
| + 60 more | See [full list](https://github.com/vercel-labs/skills#supported-agents) |

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

When you push a version tag, GitHub Actions will:

1. Validate all skills
2. Build the package
3. Create a GitHub Release with build artifacts

#### Quick Release (Recommended)

```bash
# Bump patch version (0.0.1 -> 0.0.2)
./scripts/release.sh patch

# Bump minor version (0.0.1 -> 0.1.0)
./scripts/release.sh minor

# Bump major version (0.0.1 -> 1.0.0)
./scripts/release.sh major
```

#### Manual Release

```bash
# 1. Update version in package.json
npm version patch --no-git-tag-version

# 2. Commit changes
git add package.json
git commit -m "chore: release v0.0.2"

# 3. Create tag
git tag -a v0.0.2 -m "Release v0.0.2"

# 4. Push
git push origin main --tags
```

### CI/CD

项目使用 `.coding-ci.yml` 配置 Coding 平台的 CI/CD 流水线。

| 阶段 | 触发条件 | 说明 |
|------|----------|------|
| validate | 所有推送 | 验证 SKILL.md 格式 |
| build | 所有推送 | 构建 dist/ 目录 |
| release | 推送 `v*` 标签 | 创建 GitHub Release |

## License

MIT
