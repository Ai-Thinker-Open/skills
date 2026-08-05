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

## Project Memory

### Release / CI 发布流程

- 新版本发布：本地 `git tag vX.Y.Z` 后推送到 `github` 远程（`git push github vX.Y.Z`，不要推 `origin`）。GitHub Actions `.github/workflows/release.yml` 在 `push: tags: 'v*'` 时自动构建并发布 Release；也可在 GitHub 上手动触发该工作流（`workflow_dispatch`，填 version）。
- 手动触发时工作流内会自动创建/推送 tag 并发布 Release，一次完成；但 tag 已存在时 `git tag` 步骤会失败，重复发布需先处理旧 tag。
- 默认 `GITHUB_TOKEN` 创建的 tag/release 不会再触发其它 workflow（GitHub 防递归机制，2023 年起生效），因此 workflow 内推送的 tag 不会再次触发本工作流。
- GitHub 会自动把最高 semver 的正式 Release 标记为 Latest。
- 当前版本：v0.1.4（2026-08-05 发布，Latest）。

### Jenkins 与本地构建

- `Jenkinsfile`（Jenkins）：validate → `npm run build` → 仅把 master 同步到 GitHub；不创建 tag、不发布 Release。
- 本地 `npm run build` 生成 `dist/`；`dist/skills-manifest.json` 版本取自 package.json，改版本后需重新构建才会更新 manifest。
- 远程：`github` = github.com:Ai-Thinker-Open/skills.git（Actions/Release 所在）；`origin` = Coding.net。
