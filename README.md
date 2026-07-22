# Ai-Thinker Skills

为安信可（Ai-Thinker）嵌入式产品开发提供的一套 AI Agent 技能集，帮助开发者在编写、评审、重构嵌入式 C 代码时自动遵循安信可编码规范和开发最佳实践。

本技能集覆盖：

- **编码规范** - 统一的 C 语言编码标准（命名、格式、注释、安全）
- **代码评审** - 深度代码审查，包括内存安全、FreeRTOS 任务规范、ISR 合规性
- **芯片开发指南** - BL616/BL618（Wi-Fi 6）、BL602/Ai-WB2（Wi-Fi 4）系列模块开发
- **外设驱动** - AiPi-SCBB 外设驱动模块添加指南

支持 MiMoCode、Claude Code、Codex、Cursor 等 70+ 平台，遵循 [Agent Skills 规范](https://agentskills.io)。

## 安装

### 方式 0：npx 一键安装（推荐）

```bash
# 安装全部技能
npx skills add Ai-Thinker-Open/skills

# 安装单个技能
npx skills add Ai-Thinker-Open/skills --skill ai-thinker-c-coding-standard
```

### 方式 1：克隆后复制

```bash
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills

# Claude Code
cp -r skills/ai-thinker-c-coding-standard ~/.claude/skills/

# MiMoCode / OpenCode
cp -r skills/ai-thinker-c-coding-standard ~/.opencode/skills/

# 项目级别
cp -r skills/ai-thinker-c-coding-standard ./<agent>/skills/
```

### 方式 2：符号链接（开发推荐）

```bash
git clone git@github.com:Ai-Thinker-Open/skills.git
cd skills

ln -s $(pwd)/skills/ai-thinker-c-coding-standard ~/.claude/skills/ai-thinker-c-coding-standard
```

### 安装范围

| 范围 | 位置 | 用途 |
|------|------|------|
| **全局** | `~/.<agent>/skills/` | 所有项目可用 |
| **项目** | `./<agent>/skills/` | 跟随项目，团队共享 |

## 可用技能

| 技能 | 说明 |
|------|------|
| [ai-thinker-c-coding-standard](./skills/ai-thinker-c-coding-standard) | 安信可嵌入式 C 编码规范 |
| [embedded-code-review](./skills/embedded-code-review) | 安信可嵌入式 C 深度代码评审 |
| [coder-ai-m62-m61](./skills/coder-ai-m62-m61) | BL616/BL618 开发指南（Wi-Fi 6 + BLE 5.0） |
| [coder-ai-wb2](./skills/coder-ai-wb2) | Ai-WB2/BL602 开发指南（Wi-Fi 4 + BLE 5.0） |
| [add-scbb-module](./skills/add-scbb-module) | AiPi-SCBB 外设驱动模块添加指南 |
| [add-skills](./skills/add-skills) | 向本仓库添加新技能指南 |

## 技能详情

### ai-thinker-c-coding-standard

安信可嵌入式产品 C 语言编码规范。编写、修改、评审任何嵌入式 C 代码时自动遵循，包括：

- 统一前缀 `axk` 命名规则
- K&R 大括号风格，4 空格缩进
- Doxygen 函数头注释
- 参数校验与内存安全
- `#include` 排序与文件组织

### embedded-code-review

安信可嵌入式 C 深度代码评审，覆盖：

- 安全漏洞与内存越界检测
- FreeRTOS 任务创建规范
- 中断服务程序（ISR）合规性
- 编码规范逐项核查

### coder-ai-m62-m61

BL616/BL618 系列模块开发指南（Wi-Fi 6 + BLE 5.0），基于 bouffalo_sdk：

- GPIO、UART、SPI、I2C、DMA 编程
- Wi-Fi 和 BLE 连接

### coder-ai-wb2

Ai-WB2/BL602 系列模块开发指南（Wi-Fi 4 + BLE 5.0）：

- 外设编程（GPIO、UART、PWM、ADC）
- MQTT、HTTP 网络协议

### add-scbb-module

AiPi-SCBB 外设驱动模块添加指南，遵循 `AXK_<module>_<protocol>_ACLL` 宏模式。

## 创建新技能

```bash
cd skills/
mkdir my-skill && cd my-skill
```

创建 `SKILL.md`：

```markdown
---
name: my-skill
description: 技能描述及触发条件。
---

# My Skill

技能指令内容...
```

验证技能：

```bash
npm run validate
```

## 目录结构

```
skills/
├── skills/                      # 所有技能
│   └── ai-thinker-c-coding-standard/
│       ├── SKILL.md             # 技能主文件（必需）
│       ├── scripts/             # 辅助脚本（可选）
│       ├── references/          # 按需加载的文档（可选）
│       └── assets/              # 输出使用的文件（可选）
├── .github/workflows/           # GitHub Actions
├── bin/                         # CLI 工具
├── scripts/                     # 构建和发布脚本
└── README.md
```

## 开发

```bash
# 验证所有技能
npm run validate

# 构建
npm run build
```

## License

MIT
