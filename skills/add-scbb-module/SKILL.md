---
name: add-scbb-module
description: 向 AiPi-SCBB 库添加新的外设驱动模块。当用户需要添加新模块、创建新驱动、移植外设到 SCBB 框架时使用。遵循 `AXK_<模块名>_<协议通道>_ACLL` 宏模式和 Ai-Thinker C 编码规范。
---

# 添加 SCBB 模块

## 目录结构

```
SCBB/
├── <ModuleName>/
│   ├── axk_<module>.h      # 头文件：__has_include + 宏定义
│   └── axk_<module>.c      # 实现：只通过宏调用 BSP
└── ...
```

## 步骤 1: 创建头文件

```c
/**
 * @file axk_<module>.h
 * @author SeaHi-Mo (Seahi-Mo@Foxmail.com)
 * @brief <模块名> <功能描述>（<协议> 协议）。
 * @version 0.1
 * @date YYYY-MM-DD
 *
 * @copyright Copyright (c) YYYY
 *
 */
#ifndef __AXK_<MODULE>_H__
#define __AXK_<MODULE>_H__

#if __has_include("<mcu>_bsp_<protocol>.h")
#include "<mcu>_bsp_<protocol>.h"
#define AXK_<MODULE>_<PROTOCOL>_ACLL(_func, ...) <bsp_prefix>_##_func(__VA_ARGS__)
#define AXK_<MODULE>_DELAY_MS(x) delay_ms((x))
#pragma message "<mcu>_bsp_<protocol>.h included"
#else
#error "Please include the appropriate <protocol> header for <module>."
#endif

// 宏定义、枚举、结构体

// 函数声明（带 Doxygen 注释）
int axk_<module>_init(void);

#endif /* __AXK_<MODULE>_H__ */
```

## 步骤 2: 创建源文件

```c
/**
 * @file axk_<module>.c
 * @author SeaHi-Mo (Seahi-Mo@Foxmail.com)
 * @brief <模块名> <功能描述>（<协议> 协议）。
 * @version 0.1
 * @date YYYY-MM-DD
 *
 * @copyright Copyright (c) YYYY
 *
 */
#include "axk_<module>.h"
#include <stdint.h>

// 静态变量（s_axk_ 前缀）
// 全局变量（g_axk_ 前缀）

// 内部函数

// 公开函数实现（通过 AXK_<MODULE>_<PROTOCOL>_ACLL 调用 BSP）
int axk_<module>_init(void) {
    AXK_<MODULE>_<PROTOCOL>_ACLL(init);
    return 0;
}
```

## 步骤 3: 添加到 CMakeLists.txt

在根 `CMakeLists.txt` 中添加：

```cmake
# <模块名> 模块
option(SCBB_<MODULE> "Enable <模块描述>" OFF)

if(SCBB_<MODULE>)
    list(APPEND SCBB_SOURCES
        ${CMAKE_CURRENT_SOURCE_DIR}/<ModuleName>/axk_<module>.c
    )
    list(APPEND SCBB_HEADERS
        ${CMAKE_CURRENT_SOURCE_DIR}/<ModuleName>/axk_<module>.h
    )
    set(SCBB_NEED_<PROTOCOL> ON)
    set(SCBB_NEED_DELAY ON)
endif()
```

在模块依赖区域添加：

```cmake
if(SCBB_<MODULE>)
    target_compile_definitions(aipi_scbb PUBLIC SCBB_<MODULE>_ENABLED=1)
endif()
```

## 步骤 4: 更新 CMakePresets.json（可选）

添加预设配置：

```json
{
    "name": "<module>",
    "displayName": "<Module> Only",
    "description": "Enable <模块描述>",
    "inherits": "default",
    "cacheVariables": {
        "SCBB_<MODULE>": "ON"
    }
}
```

## 命名规范

| 层级 | 前缀 | 示例 |
|------|------|------|
| 模块函数 | `axk_<module>_` | `axk_hxd039b2_init` |
| 模块宏 | `AXK_<MODULE>_<PROTOCOL>_ACLL` | `AXK_HXD039B2_UART_ACLL` |
| BSP 函数 | `bsp_<protocol>_` | `bsp_uart_send_byte` |
| 静态变量 | `s_axk_` | `s_axk_ac_code` |
| 全局变量 | `g_axk_` | `g_axk_device` |

## 协议通道

| 协议 | 宏后缀 | BSP 头文件 |
|------|--------|------------|
| I2C | `_I2C_ACLL` | `stm32f10x_bsp_i2c.h` |
| UART | `_UART_ACLL` | `stm32f10x_bsp_uart.h` |
| SPI | `_SPI_ACLL` | `stm32f10x_bsp_spi.h` |
| PWM+DMA | `_PWM_DMA_ACLL` | `stm32f10x_pwm_dma.h` |
| GPIO | `_GPIO_ACLL` | `stm32f10x_bsp_gpio.h` |

## 编码规范

1. **函数头注释**：`.h` 文件用 Doxygen，`.c` 文件用一行简注或 Doxygen
2. **参数校验**：所有指针参数必须 NULL 检查
3. **格式**：4 空格缩进，禁止 Tab
4. **命名**：遵循 Ai-Thinker C 编码规范

## 完整示例

参考 `HXD039B2/axk_hxd039b2.h` 和 `HXD039B2/axk_hxd039b2.c`。
