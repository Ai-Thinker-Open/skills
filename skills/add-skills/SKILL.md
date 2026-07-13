---
name: add-skills
description: Guide for adding new skills to this repository. Use when user wants to create a new skill, add a skill to the repo, or asks how to contribute skills.
---

# How to Add Skills to This Repository

## Quick Start

```bash
# 1. Create skill directory
mkdir skills/<skill-name>

# 2. Create SKILL.md
cat > skills/<skill-name>/SKILL.md << 'EOF'
---
name: <skill-name>
description: What this skill does and when to use it
---

# Skill Title

Instructions here...
EOF

# 3. Validate
npm run validate
```

## Skill Directory Structure

```
skills/
└── <skill-name>/              # Lowercase, hyphens only
    ├── SKILL.md               # Required: main skill file
    ├── scripts/               # Optional: executable scripts
    ├── references/            # Optional: docs loaded on demand
    └── assets/                # Optional: output templates/files
```

## SKILL.md Format

### Frontmatter (Required)

Only two fields are required:

```yaml
---
name: <skill-name>           # Lowercase, hyphens only
description: <description>   # What it does + when to use it
---
```

### Body

Write instructions for the agent. Use clear, actionable steps.

### Example

```markdown
---
name: my-new-skill
description: Do X when user asks for Y. Use for Z tasks.
---

# My New Skill

## When to Use

- When user asks to do X
- For Y-related tasks

## Steps

1. First, do this
2. Then, do that

## Examples

```code
example here
```
```

## Naming Rules

| Rule | Example |
|------|---------|
| Lowercase only | `my-skill` ✓, `My-Skill` ✗ |
| Hyphens for spaces | `code-review` ✓, `code review` ✗ |
| No special chars | `api-helper` ✓, `api@helper` ✗ |
| Under 64 chars | `short-name` ✓ |

## Optional Directories

### scripts/

Executable helper scripts (Python/Bash/Node).

```
scripts/
├── helper.py
└── build.sh
```

### references/

Documentation loaded on demand by the agent.

```
references/
├── api-docs.md
└── examples.md
```

Reference from SKILL.md:

```markdown
See [API Docs](./references/api-docs.md) for details.
```

### assets/

Files used in output (templates, images, fonts).

```
assets/
├── template.html
└── logo.png
```

## Validation

Always validate before committing:

```bash
npm run validate
```

Expected output:

```
🔍 Validating skills...

✅ skills/my-skill/SKILL.md

📊 Found N skill(s)

✅ All skills are valid
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Name has uppercase | `My-Skill` → `my-skill` |
| Missing description | Add description to frontmatter |
| Extra fields | Remove `category`, `tags`, etc. |
| Empty references/ | Add docs or remove directory |

## Complete Example

**Directory**: `skills/code-review/`

**SKILL.md**:

```markdown
---
name: code-review
description: Review code for quality, security, and best practices. Use when user asks to review, audit, or check code.
---

# Code Review Skill

## When to Use

- User asks to review code
- User wants to audit code quality
- User asks to check for issues

## Steps

1. Check for security vulnerabilities
2. Verify error handling
3. Review naming conventions
4. Suggest improvements

## Checklist

- [ ] No hardcoded secrets
- [ ] Error handling present
- [ ] Input validation
- [ ] Clear naming
```

## After Creating

1. Run `npm run validate`
2. Test the skill:
   ```bash
   npx skills add ./skills --skill <skill-name> -a <agent>
   ```
3. Commit and push
