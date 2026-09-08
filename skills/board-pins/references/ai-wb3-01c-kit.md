# Ai-WB3-01C-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-WB3-01C-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-WB3-01C-Kit Specification V1.0.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/WiFi/WB3/specification/Ai-WB3-01C-Kit_V1.0.0%20Specification%2020230310%20.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | ADC | ADC pin, and IOA0 pin partial pressure |
| 2 | IOA0 | GPIOA0/ADC/EXT_INT/FULLMUX |
| 3 | NC | Empty feet |
| 4 | IOA1 | GPIOA1/ADC/SWD/EXT_INT/FULLMUX |
| 5 | IOA7 | GPIOA7/SDIO_IO3/EXT_INT/FULLMUX |
| 6 | IOA10 | GPIOA10/SDIO_IO0/I2S_SDO/FULLMUX |
| 7 | IOA11 | GPIOA11/SDIO_IO1/FULLMUX |
| 8 | IOA4 | GPIOA4/ADC/SWCK/FULLMUX |
| 9 | IOA5 | GPIOA5/EXT_INT/FULLMUX |
| 10 | GND | Ground |
| 11 | 3V3 | 3.3V Empty feet |
| 12 | EN | By default, it is enabled on the chip. The high level is valid |
| 13 | IOA6 | GPIOA6/SDIO_IO2/I2S_SDI/EXT_INT/FULLMUX |
| 14 | GND | Ground |
| 15 | 5V | 5V Empty feet |
| 16 | 3V3 | 3.3V Empty feet |
| 17 | GND | Ground |
| 18 | TX | TXD/GPIOA2/EXT_INT/FULLMUX |
| 19 | RX | RXD/GPIOA3/EXT_INT/FULLMUX |
| 20 | IOB5 | GPIOB5/ADC/FULLMUX |
| 21 | IOB4 | GPIOB4/ADC/FULLMUX |
| 22 | NC | Empty feet |
| 23 | IOB7 | GPIOB7/FULLMUX |
| 24 | GND | Ground |
| 25 | 3V3 | 3.3V power supply |
| 26 | IOB8 | RX1/GPIOB8/FULLMUX |
| 27 | IOA9 | GPIOA9/SDIO_CLK/I2S_SCLK/FLLMUX/BOOT_MODE |
| 28 | IOB9 | TX1/GPIOB9/FULLMUX/EXT_INT |
| 29 | IOB3 | GPIOB3/ADC/FULLMUX |
| 30 | IOA12 | GPIOA12/FULLMUX |

## 功能索引

| I2S_SCLK | IOA9 |
| I2S_SDI | IOA6 |
| I2S_SDO | IOA10 |
| RXD | RX |
| TXD | TX |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
