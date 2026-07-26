---
name: scbb-module-finder
description: 从 AiPi-SCBB 仓库查找并获取所需的外设驱动模块。当用户需要查找传感器驱动、外设模块、硬件驱动代码时使用。支持 I2C、UART、SPI、PWM+DMA 等协议的模块检索。
---

# SCBB 模块查找器

## 源仓库

**优先使用**: https://github.com/Ai-Thinker-Open/AiPi-SCBB.git

## 已知模块列表

| 模块 | 描述 | 协议 | I2C 地址 | 源码路径 |
|------|------|------|----------|----------|
| CH224A | USB-PD 受电芯片（电压协商 5-28V, PPS, AVS） | I2C | 0x22 | `CH224A/` |
| SHT3x | 温湿度传感器 | I2C | 0x44 | `SHT3x/` |
| WS2812 | 可寻址 RGB LED 灯带驱动 + HSV/RGB 颜色工具 | PWM+DMA | — | `WS2812/` |
| HXD039B2 | 红外编解码器（空调遥控） | UART+GPIO | — | `HXD039B2/` |

## 查找流程

### 步骤 1: 确认用户需求

向用户询问:
1. 需要驱动的外设/传感器型号
2. 使用的通信协议（I2C/UART/SPI/PWM+DMA）
3. 目标 MCU 平台

### 步骤 2: 匹配模块

根据用户需求匹配已知模块:

- **USB-PD / 快充 / 电压协商** → CH224A
- **温湿度 / SHT / 传感器** → SHT3x
- **RGB LED / 灯带 / WS2812 / 彩灯** → WS2812
- **红外 / 遥控 / IR / 空调控制** → HXD039B2

### 步骤 3: 获取模块代码

从仓库克隆或下载所需模块:

```bash
# 克隆完整仓库
git clone https://github.com/Ai-Thinker-Open/AiPi-SCBB.git

# 或使用 sparse-checkout 只获取特定模块
git clone --filter=blob:none --sparse https://github.com/Ai-Thinker-Open/AiPi-SCBB.git
cd AiPi-SCBB
git sparse-checkout set <ModuleName> config STM32F10x_bsp
```

### 步骤 4: 集成指导

根据用户构建系统提供集成方案:

#### CMake 项目

```cmake
add_subdirectory(AiPi-SCBB)
target_link_libraries(your_app PRIVATE AiPi::SCBB)
```

#### FetchContent

```cmake
include(FetchContent)
FetchContent_Declare(
    aipi_scbb
    GIT_REPOSITORY https://github.com/Ai-Thinker-Open/AiPi-SCBB.git
    GIT_TAG        master
)
FetchContent_MakeAvailable(aipi_scbb)
target_link_libraries(your_app PRIVATE AiPi::SCBB)
```

#### 手动添加（Keil/IAR/Makefile）

1. 复制模块目录（如 `CH224A/`）到项目
2. 复制 `config/scbb_config.h` 并启用对应模块
3. 添加 `.c` 和 `.h` 文件到构建系统
4. 提供 BSP 实现（参考 `STM32F10x_bsp/`）

### 步骤 5: 配置 scbb_config.h

```c
// 启用所需模块
#define SCBB_CH224A_ENABLED 1
#define SCBB_SHT3X_ENABLED 1
// #define SCBB_WS2812_ENABLED 1
// #define SCBB_HXD039B2_ENABLED 1
```

或使用 menuconfig 工具:

```bash
python menuconfig.py
```

## BSP 移植

若目标平台非 STM32F10x，需实现以下 BSP 接口:

| 协议 | 需实现的函数 | 参考文件 |
|------|-------------|----------|
| I2C | `bsp_i2c_init`, `bsp_i2c_write`, `bsp_i2c_read` | `STM32F10x_bsp/stm32f10x_bsp_i2c.c` |
| UART | `bsp_uart_init`, `bsp_uart_send_byte` | `STM32F10x_bsp/stm32f10x_bsp_uart.c` |
| PWM+DMA | `bsp_pwm_dma_init`, `bsp_pwm_dma_send` | `STM32F10x_bsp/stm32f10x_pwm_dma.c` |
| GPIO | `bsp_gpio_init`, `bsp_gpio_set` | `STM32F10x_bsp/stm32f10x_bsp_gpio.c` |
| Delay | `delay_ms`, `delay_us` | `STM32F10x_bsp/stm32f10x_delay.c` |

## 未找到匹配模块

若仓库中无用户所需模块:

1. 告知用户当前可用模块列表
2. 建议参考 `add-scbb-module` 技能创建新模块
3. 提供模块开发规范链接: 遵循 `AXK_<模块名>_<协议通道>_ACLL` 宏模式

## 注意事项

- 所有模块依赖 `scbb_config.h` 进行编译配置
- I2C 模块需要 BSP 层提供标准 I2C 读写接口
- WS2812 使用 PWM+DMA 方式驱动，需要 MCU 支持 DMA
- HXD039B2 使用 UART+GPIO，需要硬件支持红外收发
