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
├── .github/workflows/              # CI/CD workflows
│   ├── validate.yml                # Validation on push/PR
│   └── release.yml                 # Auto-release on tag push
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

1. Create a new directory under `skills/`:

```bash
mkdir skills/my-new-skill
```

2. Create `SKILL.md` with YAML frontmatter:

```markdown
---
name: my-new-skill
description: What this skill does and when to use it
---

# My Skill Title

Instructions for the agent to follow when this skill is activated.

## When to Use

Describe the scenarios where this skill should be used.

## Steps

1. First, do this
2. Then, do that
```

3. Optionally add resource directories:

```bash
mkdir skills/my-new-skill/scripts    # Executable helper scripts
mkdir skills/my-new-skill/references # Documentation loaded on demand
mkdir skills/my-new-skill/assets     # Files used in output
```

### Skill Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (lowercase, hyphens allowed) |
| `description` | Yes | Brief explanation of what the skill does and when to use it |
| `metadata.internal` | No | Set to `true` to hide from normal discovery |

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

### CI/CD Workflows

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `validate.yml` | Push to main, PRs | Validates SKILL.md format |
| `release.yml` | Push version tag (`v*`) | Builds and creates GitHub Release |

## License

MIT
