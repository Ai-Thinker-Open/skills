---
name: ota-generator
description: 生成安信可（Ai-Thinker）嵌入式产品的 OTA 升级固件。当用户提到"生成OTA"、"OTA固件"、"OTA build"、"升级固件版本"时使用。支持两种模式：模式A（已有固件文件，添加MD5包头）和模式B（从源码编译并生成OTA固件）。
---

# OTA 固件生成

生成安信可嵌入式产品的 OTA 升级固件。

## 触发条件

用户提到以下任意关键词时触发：`生成OTA`、`OTA固件`、`OTA build`、`升级固件版本`、`生成ota`。

## 工作流程

### 第一步：确定模式

询问用户当前场景：

- **模式 A**：用户已有 `FW_OTA.bin` 或类似固件文件，只需添加 MD5 包头
- **模式 B**：需要从源码编译，生成新的 OTA 固件

### 第二步：收集参数

根据模式收集所需参数（用户未提供的才询问，已有信息跳过）：

**模式 A 需要：**
| 参数 | 说明 | 示例 |
|------|------|------|
| 固件文件路径 | 已有的 .bin 文件 | `./FW_OTA.bin` |
| 输出目录 | 生成文件存放位置 | `.`（当前目录） |

**模式 B 需要：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| 项目根目录 | 包含 `xiaozhi_project_cfg.h` 的上级目录 | 自动检测 |
| 目标版本号 | 如 `3.4` | 读取当前版本 |
| 文件名前缀 | 如 `BL602_XZ` | 从配置读取 |
| 输出目录 | 生成文件存放位置 | `.`（当前目录） |
| 是否执行 make flash | 编译并生成 FW_OTA.bin | 是 |

### 第三步：检测平台并执行脚本

检测当前操作系统，调用对应脚本：

```bash
# Linux/macOS
bash <skill_dir>/scripts/generate_ota.sh [参数]

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File <skill_dir>/scripts/generate_ota.ps1 [参数]
```

其中 `<skill_dir>` 为本 skill 所在目录（即 `skills/ota-generator/`）。

### 脚本参数

**模式 A：**
```
--mode A --input <固件文件路径> [--output <输出目录>]
```

**模式 B：**
```
--mode B [--project-root <项目根目录>] [--version <目标版本>] [--prefix <前缀>] [--output <输出目录>] [--skip-build]
```

模式 B 的 `--skip-build` 参数：跳过 `make flash` 步骤，直接对已有的 `FW_OTA.bin` 添加包头。适用于编译已完成、只需打包的场景。

### 第四步：报告结果

脚本执行成功后，向用户报告：
- 输出文件路径和大小
- 文件 MD5 校验值
- 如有版本号变更，确认已恢复

## ai_pack_head 文件格式

OTA 固件在原始固件前附加 169 字节包头：

| 偏移 | 长度 | 内容 | 说明 |
|------|------|------|------|
| 0x00 | 5 | `V1.0\0` | 版本号 + 结束符 |
| 0x05 | 4 | `UNKN` | 芯片类型 |
| 0x09 | 32 | MD5 | 固件体的 MD5（大写十六进制） |
| 0x29 | 128 | 0x00 | URL 填充（预留） |

## 文件命名规则

- **模式 A**：`<原文件名>_md5.bin`（如 `FW_OTA_md5.bin`）
- **模式 B**：`<前缀>_<版本号>_<语言>_ota.bin`（如 `BL602_XZ_3.4_zh_ota.bin`）

## 注意事项

1. `FW_OTA.bin` 不是最终 OTA 文件，必须添加 ai_pack_head 后才可用
2. MD5 必须正确，OTA 升级时服务端会校验
3. 模式 B 生成完成后必须恢复原始版本号
4. `make flash` 需要设备连接；无设备时可使用 `--skip-build` 跳过编译
