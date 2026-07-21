<div align="center">

# Agent Skills 集合

</div>

[![English](https://img.shields.io/badge/English-README-blue)](README.md)

跨平台通用的 AI Agent Skills 集合，支持 MiMoCode、Claude Code、Codex、Cursor 等 69+ 平台。

> **注意：** 本仓库已同步到 GitHub 以便安装。`npx skills add` 命令可直接使用 GitHub 仓库。

## 快速开始

### 方法 0：使用 npx（推荐）

```bash
# 安装所有 skills
npx skills add Ai-Thinker-Open/skills

# 安装指定 skill
npx skills add Ai-Thinker-Open/skills --skill ai-thinker-c-coding-standard
```

### 方法 1：克隆并复制

```bash
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills

# Claude Code
cp -r skills/ai-thinker-c-coding-standard ~/.claude/skills/

# MiMoCode / OpenCode
cp -r skills/ai-thinker-c-coding-standard ~/.opencode/skills/

# 项目级别使用
cp -r skills/ai-thinker-c-coding-standard ./<agent>/skills/
```

### 方法 2：符号链接（推荐用于开发）

```bash
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills

ln -s $(pwd)/skills/ai-thinker-c-coding-standard ~/.claude/skills/ai-thinker-c-coding-standard
```

## 可用 Skills

| Skill | 说明 |
|-------|------|
| [ai-thinker-c-coding-standard](./skills/ai-thinker-c-coding-standard) | 安信可嵌入式 C 编码规范 |
| [embedded-code-review](./skills/embedded-code-review) | 安信可嵌入式 C 代码深度审查 |
| [coder-ai-m62-m61](./skills/coder-ai-m62-m61) | BL616/BL618 开发指南 (Wi-Fi 6 + BLE 5.0) |
| [coder-ai-wb2](./skills/coder-ai-wb2) | Ai-WB2/BL602 开发指南 (Wi-Fi 4 + BLE 5.0) |
| [add-skills](./skills/add-skills) | 向本仓库添加新 skill 的指南 |

### ai-thinker-c-coding-standard

安信可（Ai-Thinker）嵌入式产品 C 语言编码规范。编写、修改、评审、重构任何嵌入式 C 代码，或生成 .c/.h 文件、加函数头注释、检查代码规范时使用。

**使用场景：**
- 编写嵌入式 C 代码
- 评审代码规范合规性
- 生成 Doxygen 风格的函数头注释

### embedded-code-review

安信可嵌入式 C 代码深度审查 skill。审查安全、内存管理、FreeRTOS 任务规范、中断处理、编码规范合规等。

**使用场景：**
- 嵌入式代码安全审查
- FreeRTOS 任务创建规范检查
- 内存泄漏/溢出风险排查
- ISR 合规性审查
- 编码规范逐项核对

### coder-ai-m62-m61

安信可 BL616/BL618 系列模组开发指南 - Wi-Fi 6 + BLE 5.0 模组，基于 bouffalo_sdk。

**使用场景：**
- BL616/BL618 模组开发
- GPIO、UART、SPI、I2C、DMA 编程
- Wi-Fi 和 BLE 连接

### coder-ai-wb2

安信可 Ai-WB2 系列模组开发指南 (BL602 芯片) - Wi-Fi 4 + BLE 5.0 模组。

**使用场景：**
- Ai-WB2 模组开发
- 外设编程 (GPIO、UART、PWM、ADC)
- MQTT、HTTP 网络协议

### add-skills

向本仓库添加新 skill 的指南。

**使用场景：**
- 创建新 skill
- 学习 skill 格式和结构
- 验证 skill

## 仓库结构

```
skills/
├── skills/                          # 所有 skills 存放于此
│   └── ai-thinker-c-coding-standard/
│       ├── SKILL.md                # Skill 主文件（必需）
│       ├── scripts/                # 辅助脚本（可选）
│       ├── references/             # 按需加载的文档（可选）
│       └── assets/                 # 输出中使用的文件（可选）
├── .coding-ci.yml                  # Coding CI/CD 配置
├── bin/                            # CLI 工具
│   └── cli.js                      # seahi-skills CLI
├── scripts/                        # 构建和发布脚本
│   ├── validate.mjs                # 验证 SKILL.md 文件
│   ├── build.mjs                   # 构建 skills 到 dist/
│   └── release.sh                  # 本地发布脚本
├── README.md                       # English documentation
├── README.zh.md                    # 中文说明
├── package.json
└── skills.sh.json                  # skills.sh 发现配置
```

## 创建新 Skill

### 步骤 1：创建 Skill 目录

```bash
cd skills/
mkdir my-new-skill
cd my-new-skill
```

### 步骤 2：创建 SKILL.md

创建 `SKILL.md` 文件，包含 YAML frontmatter。`description` 字段是主要触发器 - agent 根据它来决定何时激活此 skill。

```markdown
---
name: my-new-skill
description: 这个 skill 做什么以及何时使用。包含触发短语，如"当用户要求 X"或"用于 Y 任务"。
---

# Skill 标题

当此 skill 被激活时，agent 应遵循的指令。

## 使用场景

描述此 skill 应被使用的场景。

## 步骤

1. 首先，做这个
2. 然后，做那个
```

### 步骤 3：（可选）添加资源目录

```bash
mkdir scripts    # 可执行的辅助脚本（Python/Bash/Node）
mkdir references # 按需加载的文档
mkdir assets     # 输出中使用的模板、图片、字体
```

### 步骤 4：验证你的 Skill

```bash
# 在仓库根目录执行
npm run validate
```

预期输出：
```
🔍 Validating skills...

✅ skills/my-new-skill/SKILL.md

📊 Found 2 skill(s)

✅ All skills are valid
```

### Skill Frontmatter 字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | 唯一标识符（仅限小写和连字符） |
| `description` | 是 | skill 功能 + 使用场景（触发激活的关键） |
| `metadata.internal` | 否 | 设为 `true` 可从常规发现中隐藏 |

### 示例：完整的 Skill

```
skills/
└── code-review/
    ├── SKILL.md              # 主文件
    ├── scripts/
    │   └── lint.sh           # 辅助脚本
    └── references/
        └── style-guide.md    # 参考文档
```

`skills/code-review/SKILL.md`：
```markdown
---
name: code-review
description: 审查代码质量、安全性和最佳实践。当用户要求审查、审计或检查代码时使用。
---

# 代码审查 Skill

遵循以下指南审查代码变更。

## 步骤

1. 检查安全漏洞
2. 验证错误处理
3. 审查命名规范
4. 建议改进
```

### 目录结构参考

```
skills/
└── <skill-name>/                 # Skill 名称（小写，连字符）
    ├── SKILL.md                  # 必需：主文件
    ├── scripts/                  # 可选：可执行脚本
    │   └── helper.py
    ├── references/               # 可选：按需加载的文档
    │   └── api-docs.md
    └── assets/                   # 可选：输出模板/文件
        └── template.html
```

```bash
mkdir skills/my-new-skill/scripts    # 可执行的辅助脚本
mkdir skills/my-new-skill/references # 按需加载的文档
mkdir skills/my-new-skill/assets     # 输出中使用的文件
```

### Skill Frontmatter 字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | 唯一标识符（小写，允许连字符） |
| `description` | 是 | 简要说明 skill 的功能和使用场景 |
| `metadata.internal` | 否 | 设为 `true` 可从常规发现中隐藏 |

## 安装

### 方法 0：使用 npx（推荐）

```bash
# 安装指定 skill
npx skills add Ai-Thinker-Open/skills/skills/ai-thinker-c-coding-standard

# 或克隆整个仓库
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills
```

### 方法 1：克隆并复制

```bash
# 克隆仓库
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills

# 复制指定 skill 到 Claude Code（全局）
cp -r skills/ai-thinker-c-coding-standard ~/.claude/skills/

# 复制指定 skill 到 MiMoCode（全局）
cp -r skills/ai-thinker-c-coding-standard ~/.opencode/skills/

# 复制到项目目录（项目级别）
mkdir -p .claude/skills
cp -r skills/ai-thinker-c-coding-standard .claude/skills/
```

### 方法 2：符号链接（推荐用于开发）

```bash
# 克隆仓库
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills

# 为所有 skills 创建符号链接
ln -s $(pwd)/skills/ai-thinker-c-coding-standard ~/.claude/skills/ai-thinker-c-coding-standard
ln -s $(pwd)/skills/embedded-code-review ~/.claude/skills/embedded-code-review
ln -s $(pwd)/skills/coder-ai-m62-m61 ~/.claude/skills/coder-ai-m62-m61
ln -s $(pwd)/skills/coder-ai-wb2 ~/.claude/skills/coder-ai-wb2
```

### 安装范围

| 范围 | 位置 | 使用场景 |
|------|------|----------|
| **全局** | `~/.<agent>/skills/` | 所有项目可用 |
| **项目** | `./<agent>/skills/` | 随项目提交，团队共享 |

## 支持的平台

Skills 遵循 [Agent Skills 规范](https://agentskills.io)，兼容以下平台：

| 平台 | Agent 标志 |
|------|-----------|
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
| + 60 个更多 | 查看[完整列表](https://agentskills.io#supported-agents) |

## 开发

### 本地开发

```bash
# 验证所有 skills
npm run validate

# 构建 skills 到 dist/
npm run build

# 运行 CLI
node bin/cli.js list
```

### 发布

```bash
# 补丁版本 (0.0.1 -> 0.0.2)
npm version patch --no-git-tag-version

# 提交更改
git add package.json
git commit -m "chore: release v0.0.2"

# 创建标签
git tag -a v0.0.2 -m "Release v0.0.2"

# 推送
git push origin main --tags
```

### CI/CD

项目使用 `.coding-ci.yml` 配置 Coding 平台的 CI/CD 流水线。

| 阶段 | 触发条件 | 说明 |
|------|----------|------|
| validate | 所有推送 | 验证 SKILL.md 格式 |
| build | 所有推送 | 构建 dist/ 目录 |

## 许可证

MIT
