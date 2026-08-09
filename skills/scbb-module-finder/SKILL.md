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
| SHT3x | 温湿度传感器（SHT30/SHT31/SHT35，含 CRC-8 校验） | I2C | 0x44 | `SHT3x/` |
| INA226 | 电压/电流/功率监测（默认 0x40，可配置 0x40–0x4F） | I2C | 0x40 | `INA226/` |
| WS2812 | 可寻址 RGB LED 灯带驱动 + HSV/RGB 颜色工具 | PWM+DMA | — | `WS2812/` |
| HXD039B2 | 红外编解码器（空调遥控） | UART+GPIO | — | `HXD039B2/` |
| ST7789V_LCD | ST7789V 驱动芯片通用 LCD（1.47"/1.69"/1.9"/2.0"） | SPI+GPIO | — | `ST7789V_LCD/` |
| OLED_096_SPI | 0.96" OLED 显示屏（SSD1306, 128x64，帧缓冲渲染） | SPI+GPIO | — | `OLED_096_SPI/` |
| LLCC68 | LoRa 射频收发模块（sub-GHz，全双工 SPI） | SPI+GPIO | — | `LLCC68/` |
| RD03_V2 | 毫米波雷达（人体存在/距离检测，仅 UART 接收） | UART | — | `RD03_V2/` |
| DHT11 | 温湿度传感器（单总线 One-Wire） | GPIO | — | `DHT11/` |
| DS1302 | RTC 实时时钟（3 线 GPIO 位操作） | GPIO | — | `DS1302/` |
| RELAY | 继电器驱动（高电平有效） | GPIO | — | `RELAY/` |

## 查找流程

### 步骤 1: 确认用户需求

向用户询问:
1. 需要驱动的外设/传感器型号
2. 使用的通信协议（I2C/UART/SPI/PWM+DMA）
3. 目标 MCU 平台

### 步骤 2: 匹配模块

根据用户需求匹配已知模块:

- **USB-PD / 快充 / 电压协商** → CH224A
- **温湿度 / SHT30 / SHT31 / SHT35** → SHT3x
- **电压 / 电流 / 功率监测 / 采样** → INA226
- **RGB LED / 灯带 / WS2812 / 彩灯** → WS2812
- **红外 / 遥控 / IR / 空调控制** → HXD039B2
- **LCD / 屏幕 / 显示 / ST7789** → ST7789V_LCD
- **OLED / SSD1306 / 0.96" 屏** → OLED_096_SPI
- **LoRa / 射频 / 远距离通信** → LLCC68
- **雷达 / 人体检测 / 存在检测 / 距离** → RD03_V2
- **温湿度 / DHT11 / 单总线** → DHT11
- **时钟 / RTC / 时间** → DS1302
- **继电器 / 开关控制** → RELAY

### 步骤 3: 获取模块代码

从仓库克隆或下载所需模块:

```bash
# 克隆完整仓库
git clone https://github.com/Ai-Thinker-Open/AiPi-SCBB.git

# 或使用 sparse-checkout 只获取特定模块
git clone --filter=blob:none --sparse https://github.com/Ai-Thinker-Open/AiPi-SCBB.git
cd AiPi-SCBB
git sparse-checkout set <ModuleName> BSP
```

> 注：`scbb_config.h` 由 `python menuconfig.py` 在仓库根目录生成；内置 BSP 位于 `BSP/Ai-M6x/`（BL616/BL618）与 `BSP/stm32f10x/`（STM32F103）。

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
2. 在项目根目录创建 `scbb_config.h` 并启用对应模块
3. 添加 `.c` 和 `.h` 文件到构建系统
4. 提供 BSP 实现（参考 `BSP/Ai-M6x/` 或 `BSP/stm32f10x/`）

### 步骤 5: 配置 scbb_config.h

```c
// 启用所需模块
#define SCBB_CH224A_ENABLED 1
#define SCBB_SHT3X_ENABLED 1
// #define SCBB_INA226_ENABLED 1
// #define SCBB_WS2812_ENABLED 1
// #define SCBB_HXD039B2_ENABLED 1
// #define SCBB_ST7789V_LCD_ENABLED 1
// #define SCBB_OLED_096_SPI_ENABLED 1
// #define SCBB_LLCC68_ENABLED 1
// #define SCBB_RD03_V2_ENABLED 1
// #define SCBB_DHT11_ENABLED 1
// #define SCBB_DS1302_ENABLED 1
// #define SCBB_RELAY_ENABLED 1
```

或使用 menuconfig 工具:

```bash
python menuconfig.py
```

## BSP 移植

若目标平台非 STM32F10x，需实现以下 BSP 接口:

| 协议 | 需实现的函数 | 参考文件 |
|------|-------------|----------|
| I2C | `bsp_i2c_init`, `bsp_i2c_write`, `bsp_i2c_read` | `BSP/stm32f10x/i2c/stm32f10x_bsp_i2c.c` |
| SPI | `bsp_spi_init`, `bsp_spi_send8`, `bsp_spi_send16`, `bsp_spi_transfer8` | `BSP/stm32f10x/spi/stm32f10x_bsp_spi.c` |
| UART | `bsp_uart_init`, `bsp_uart_send_byte` | `BSP/stm32f10x/uart/stm32f10x_bsp_uart.c` |
| PWM+DMA | `bsp_pwm_dma_init`, `bsp_pwm_dma_send` | `BSP/stm32f10x/pwm_dma/stm32f10x_pwm_dma.c` |
| GPIO | `bsp_gpio_init`, `bsp_gpio_set` | `BSP/stm32f10x/gpio/stm32f10x_bsp_gpio.c` |
| Delay | `delay_ms`, `delay_us` | `BSP/stm32f10x/delay/stm32f10x_delay.c` |

> 注：BL616/BL618 平台（`BSP/Ai-M6x/`）无 PWM+DMA BSP，WS2812 目前依赖 STM32F10x 平台。

## 未找到匹配模块

若仓库中无用户所需模块:

1. 告知用户当前可用模块列表
2. 建议参考 `add-scbb-module` 技能创建新模块
3. 提供模块开发规范链接: 遵循 `AXK_<模块名>_<协议通道>_ACLL` 宏模式

## 注意事项

- 所有模块依赖 `scbb_config.h` 进行编译配置
- I2C 模块需要 BSP 层提供标准 I2C 读写接口
- SPI 模块（ST7789V_LCD / OLED_096_SPI / LLCC68）需要 BSP 层提供 SPI 初始化与发送接口，LLCC68 要求全双工 SPI
- WS2812 使用 PWM+DMA 方式驱动，需要 MCU 支持 DMA
- HXD039B2 使用 UART+GPIO，需要硬件支持红外收发
- DHT11 使用单总线 GPIO 时序（含 18ms 起始信号），需要高精度延时
- DS1302 使用 3 线 GPIO 位操作（CE/SCLK/IO），引脚宏可覆盖
- RD03_V2 仅 UART 接收，解析 `distance:XXX` / `OFF` 帧
- INA226 采样电阻默认 10mΩ，可通过 `AXK_INA226_SHUNT` 覆盖
