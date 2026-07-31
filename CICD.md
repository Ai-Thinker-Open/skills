# Coding CI 构建配置指南

本项目使用 Coding CI 的可视化构建流程（非 Jenkinsfile），自动验证、构建并同步到 GitHub。

> **重要**：可视化编排中每个步骤是独立 shell，环境变量不跨步骤传递。每个步骤都需要单独设置 `PATH`。

## 构建计划配置

### 基本信息

| 配置项 | 值 |
|--------|-----|
| 代码来源 | 选择本仓库代码 |
| 分支 | `master` |
| Jenkinsfile | 不使用（使用可视化编排） |

### 环境变量

在构建计划 → 环境变量中添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `GITHUB_TOKEN` | 你的 GitHub PAT | 用于推送到 GitHub |
| `NODE_VERSION` | `v18.12.1` | Node.js 版本（方便后续修改） |

## 构建步骤

### 第 1 步：安装 Node.js 18

```bash
curl -fsSL https://nodejs.org/dist/v18.12.1/node-v18.12.1-linux-x64.tar.xz | tar -xJ
export PATH=$PWD/node-v18.12.1-linux-x64/bin:$PATH
node --version
npm --version
```

### 第 2 步：验证 Skills

```bash
export PATH=$PWD/node-v18.12.1-linux-x64/bin:$PATH
npm run validate
```

### 第 3 步：构建

```bash
export PATH=$PWD/node-v18.12.1-linux-x64/bin:$PATH
npm run build
```

### 第 4 步：同步到 GitHub

```bash
export PATH=$PWD/node-v18.12.1-linux-x64/bin:$PATH
git remote set-url --push origin "https://${GITHUB_TOKEN}@github.com/Ai-Thinker-Open/skills.git"
git branch -a
git push origin HEAD:master
```

### 第 5 步：发布（仅 tag 触发时）

如果需要发布 Release，创建另一个构建计划，配置 tag 触发（`v*`），步骤如下：

```bash
export PATH=$PWD/node-v18.12.1-linux-x64/bin:$PATH
npm install -g gh
echo "${GITHUB_TOKEN}" | gh auth login --with-token
gh release create "${GIT_TAG_NAME}" \
    --repo "Ai-Thinker-Open/skills" \
    --title "Release ${GIT_TAG_NAME}" \
    --generate-notes \
    dist/**/*
```

## 提交前：更新 skills-manifest.json

仓库根目录的 `skills-manifest.json` 记录了每个 skill 的内容哈希，`npm run
check:updates` 依靠它与远端清单对比来报告更新。

发布流程要求：**每次修改任何 skill 内容后，提交前必须执行**：

```bash
npm run manifest
git add skills-manifest.json
```

`npm run validate`（第 2 步，以及 GitHub Actions 的 validate 步骤）会校验
`skills-manifest.json` 是否与当前内容一致，不一致会直接失败并提示先运行
`npm run manifest`，因此不需要额外增加 CI 检查步骤。

推送时把清单一并带上：Coding 主构建会把 `master` 同步到 GitHub，两个远端
都会包含最新的 `skills-manifest.json`，这样 `npm run check:updates` 才能
在两端都看到一致的哈希。

## 触发配置

| 构建计划 | 触发方式 | 说明 |
|----------|----------|------|
| 主构建 | 推送到 `master` | 验证 + 构建 + 同步到 GitHub |
| 发布 | 推送 `v*` 标签 | 创建 GitHub Release |

## 常见问题

### command not found

错误：`npm: not found`

原因：可视化编排每个步骤是独立 shell，`export PATH` 不会跨步骤传递。

解决：在**每个步骤**开头都加上 `export PATH=$PWD/node-v18.12.1-linux-x64/bin:$PATH`。

### Docker 不可用

错误：`docker: command not found`

原因：Coding CI 公共构建机未安装 Docker。

解决：不要使用 `agent { docker {} }`，改用 `agent any` + 手动安装 Node.js。
