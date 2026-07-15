# Coding CI 构建配置指南

本项目使用 Coding CI 的可视化构建流程（非 Jenkinsfile），自动验证、构建并同步到 GitHub。

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

## 构建步骤

### 第 1 步：安装 Node.js 18

```bash
curl -fsSL https://nodejs.org/dist/v18.20.4/node-v18.20.4-linux-x64.tar.xz | tar -xJ
export PATH=$PWD/node-v18.20.4-linux-x64/bin:$PATH
node --version
npm --version
```

### 第 2 步：验证 Skills

```bash
export PATH=$PWD/node-v18.20.4-linux-x64/bin:$PATH
npm run validate
```

预期输出：
```
Validating skills...
✅ skills/xxx/SKILL.md
Found N skill(s)
All skills are valid
```

### 第 3 步：构建

```bash
export PATH=$PWD/node-v18.20.4-linux-x64/bin:$PATH
npm run build
```

### 第 4 步：同步到 GitHub

```bash
git remote set-url --push origin "https://${GITHUB_TOKEN}@github.com/Ai-Thinker-Open/skills.git"
git push origin master
```

### 第 5 步：发布（仅 tag 触发时）

如果需要发布 Release，创建另一个构建计划，配置 tag 触发（`v*`），步骤如下：

```bash
export PATH=$PWD/node-v18.20.4-linux-x64/bin:$PATH
npm install -g gh
echo "${GITHUB_TOKEN}" | gh auth login --with-token
gh release create "${GIT_TAG_NAME}" \
    --repo "Ai-Thinker-Open/skills" \
    --title "Release ${GIT_TAG_NAME}" \
    --generate-notes \
    dist/**/*
```

## 触发配置

| 构建计划 | 触发方式 | 说明 |
|----------|----------|------|
| 主构建 | 推送到 `master` | 验证 + 构建 + 同步到 GitHub |
| 发布 | 推送 `v*` 标签 | 创建 GitHub Release |

## 常见问题

### Docker 不可用

错误：`docker: command not found`

原因：Coding CI 公共构建机未安装 Docker。

解决：不要使用 `agent { docker {} }`，改用 `agent any` + 手动安装 Node.js。
