<div align="center">

# Agent Skills 集合

</div>

[![English](https://img.shields.io/badge/English-README-blue)](README.md)

跨平台通用的 AI Agent Skills 集合，支持 MiMoCode、Claude Code、Codex、Cursor 等 69+ 平台。

> **注意：** 本仓库已同步到 GitHub 以便安装。`npx skills add` 命令可直接使用 GitHub 仓库。

## 项目介绍

本仓库是面向安信可（Ai-Thinker）嵌入式产品开发整理的 AI Agent Skills
集合，覆盖编码规范、深度代码审查、BL602/BL616/BL618 等芯片与模组开发指南、
外设驱动模板和模组选型。所有 skill 遵循开放的
[Agent Skills](https://agentskills.io) 规范，可在 MiMoCode、Claude Code、
Codex、Cursor 等 69+ 平台通用。

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
| [module-selector](./skills/module-selector) | 安信可模组选型助手（WiFi/LoRa/雷达/UWB/星闪） |
| [scbb-module-finder](./skills/scbb-module-finder) | SCBB 模块查找器 |
| [ota-generator](./skills/ota-generator) | OTA 固件生成器 |
| [add-scbb-module](./skills/add-scbb-module) | 向 SCBB 库添加新模块 |
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

### module-selector

安信可模组选型助手。支持 Wi-Fi、BLE、LoRa、雷达、UWB、星闪(NearLink)、NB-IoT 等全系列模组的选型推荐，包含规格书链接。

**使用场景：**
- 物联网模组选型
- 传感器模块选择
- 无线通信模组推荐

### scbb-module-finder

SCBB 模块查找器。从 AiPi-SCBB 仓库查找外设驱动模块，支持 I2C、UART、SPI、PWM+DMA 等协议。

**使用场景：**
- 查找传感器驱动
- 获取外设模块代码
- SCBB 框架集成

### ota-generator

OTA 固件生成器。支持模式A（添加MD5包头）和模式B（从源码编译）。

**使用场景：**
- 生成 OTA 升级固件
- 嵌入式固件更新

### add-scbb-module

向 SCBB 库添加新模块的指南。

**使用场景：**
- 创建新的外设驱动
- 移植模块到 SCBB 框架

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
├── skills-manifest.json            # 用于远程更新检查的内容哈希
├── .coding-ci.yml                  # Coding CI/CD 配置
├── bin/                            # CLI 工具
│   └── cli.js                      # seahi-skills CLI
├── scripts/                        # 构建和发布脚本
│   ├── validate.mjs                # 验证 SKILL.md 文件
│   ├── generate-manifest.mjs       # 重新生成 skills-manifest.json
│   ├── check-updates.mjs           # 检查/应用远端 skill 更新
│   ├── build.mjs                   # 构建 skills 到 dist/
│   ├── install.mjs                 # 安装 skills 到用户目录
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

### 步骤 4：重新生成清单并验证

每次修改 skill 后都必须同步更新 `skills-manifest.json`——远程更新检查依赖
它，而且 `npm run validate` 在清单过期时会直接失败。

```bash
# 在仓库根目录执行
npm run manifest    # 重新生成 skills-manifest.json
npm run validate    # 验证 SKILL.md 格式 + 清单新鲜度
```

预期输出：
```
🔍 Validating skills...

✅ skills/my-new-skill/SKILL.md

📊 Found N skill(s)

📋 Checking skills-manifest.json...
✅ skills-manifest.json is up to date

✅ All skills are valid
```

### 步骤 5：提交并推送

```bash
# 连同新 skill 和更新后的清单一起提交
git add skills/my-new-skill skills-manifest.json
git commit -m "feat(skills): add my-new-skill"

# 保持两个远端同步
git push github master
git push origin master
```

推送后，其他克隆通过 `npm run check:updates` 会看到新 skill 显示为
`🆕 远端新增`（参见[检查更新](#检查更新)）。以后每次编辑已有 skill，
记得重新执行 `npm run manifest`。

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

## 检查更新

仓库根目录维护一份 `skills-manifest.json`，包含每个 skill 的确定性
SHA-256 内容哈希。它会被拿来与 GitHub（`github`）和 Coding（`origin`）
两个远端上的清单对比，用于报告上游 skill 是否发生了变化。

```bash
# 检查两个远端（默认分支：master）
npm run check:updates

# 只检查一个远端
npm run check:updates -- --remote github

# 检查其他分支
npm run check:updates -- --branch main

# 将远端变更应用到 skills/ 并刷新已安装副本
npm run check:updates -- --update
```

状态图标：

| 图标 | 含义 |
|------|------|
| ✅ | 本地与远端一致 |
| ⬆️ | 远端有新内容 |
| 🆕 | 远端新增 skill |
| 🗑 | 远端已删除 skill |
| ⚠️ | 两个远端内容不一致，需手动处理 |

`--update` 只会把发生变更的 skill 目录恢复到工作区——不会 stage、不会提交，
方便你 review 后再提交。当该 skill 本地存在未提交修改，或两个远端给出的
内容不一致时，会跳过并提示。更新完成后会刷新已安装副本（只刷新已包含该
skill 的目录，如 `~/.codex/skills`、`~/.claude/skills`），重新生成工作区中的
`skills-manifest.json`，并运行 `npm run validate`。

退出码：`0` 全部最新，`1` 存在可更新项（或有跳过项），`2` 远端不可达 /
缺少清单，或发生内部错误。

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

# 修改 skills 后重新生成 skills-manifest.json
npm run manifest

# 检查 GitHub/Coding 远端的 skill 更新
npm run check:updates

# 构建 skills 到 dist/
npm run build

# 安装 skills 到 ~/.claude/skills 和 ~/.codex/skills
npm run install:all

# 安装指定 skill
node scripts/install.mjs module-selector

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

## FAQ / 常见问题

**`npm run check:updates` 退出码为 2。**
远端不可达，或所检查的分支上没有 `skills-manifest.json`。先把清单推送到
两个远端，再重试。

**`npm run validate` 提示 `skills-manifest.json is out of date`。**
运行 `npm run manifest` 重新生成清单，并与 skill 改动一起提交。

**只想安装某一个 skill 怎么办？**
在仓库根目录执行 `node scripts/install.mjs <skill-name>`，或使用
`npx skills add Ai-Thinker-Open/skills --skill <skill-name>`。

## 贡献指南

欢迎贡献。新增 skill 请参照上文[创建新 Skill](#创建新-skill)的步骤，或阅读
[add-skills](./skills/add-skills) 指南。修改任何 skill 后，请运行
`npm run manifest` 和 `npm run validate`，然后提交并同时推送到 GitHub
（`github`）与 Coding（`origin`）两个远端，保持镜像同步。

## 许可证

[MIT](./LICENSE)
