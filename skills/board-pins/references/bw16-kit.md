# BW16-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | BW16-Kit |
| 分类 | WiFi |
| 规格书版本 | BW16-Kit Specification V1.2.3 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/rtl87xx/bw16/Specification/BW16-Kit_V1.2.3%20Specification-20240325.pdf) |

## 引脚定义表（22 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | GND | Conductive earth |
| 2 | PA30 | LP_PWM1 |
| 3 | PA27 | SWD_DATA |
| 4 | PA25 | LP_I2C_SCL/LP_PWM4/HSDM |
| 5 | PA26 | LP_I2C_SCL/LP_PWM5/HSDP |
| 6 | PA8_LOG_RX0 | UART_LOG_RXD |
| 7 | PA7_LOG_TX0 | UART_LOG_TXD |
| 8 | EN | Chip Enable terminal |
| 9 | GND | Conductive earth |
| 10 | 3V3 | 3.3V power supply |
| 11 | 5V | 5V power supply |
| 12 | 5V | 5V power supply |
| 13 | 3V3 | 3.3V power supply |
| 14 | GND | Conductive earth |
| 15 | PB1_TX1 | LP_UART_TXD |
| 16 | PB2_RX1 | LP_UART_RXD |
| 17 | PB3 | ADC/SWD_CLK |
| 18 | PA12 | LP_PWM0/SPI1_MOSI |
| 19 | PA13 | LP_PWM1/SPI1_MISO |
| 20 | PA14 | SPI1_CLK |
| 21 | PA15 | SPI1_CS |
| 22 | GND | Conductive earth |

## 功能索引

| I2C_SCL | PA25 |
| I2C_SDA | PA26 |
| PWM0 | PA12 |
| PWM1 | PA30、PA13 |
| PWM4 | PA25 |
| PWM5 | PA26 |
| RXD | PA8_LOG_RX0、PB2_RX1 |
| TXD | PA7_LOG_TX0、PB1_TX1 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
