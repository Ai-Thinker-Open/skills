# Agent Skills Repository

This repository contains agent skills that follow the [Agent Skills specification](https://agentskills.io).

## Structure

```
skills/
├── <skill-name>/
│   ├── SKILL.md          # Required: Skill instructions with YAML frontmatter
│   ├── scripts/          # Optional: Executable helper scripts
│   ├── references/       # Optional: Documentation loaded on demand
│   └── assets/           # Optional: Files used in output
```

## Adding Skills

1. Create a new directory under `skills/`
2. Add a `SKILL.md` file with YAML frontmatter containing `name` and `description`
3. Optionally add `scripts/`, `references/`, or `assets/` directories

## Skill Format

```markdown
---
name: skill-name
description: What this skill does and when to use it
---

# Skill Title

Instructions for the agent to follow when this skill is activated.
```
