# TB-02-Kit(DIP) 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | TB-02-Kit(DIP) |
| 分类 | Bluetooth |
| 规格书版本 | TB-02-Kit V2.0 Specification V1.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/Bluetooth/blue_tooth/Specification/TB-02-Kit%28DIP-20%29_V2.0%20Specification-20260722A.docx.pdf) |

## 引脚定义表（10 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | RXD | UART_RX/GPIO PA0/PWM0 inverted output |
| 2 | TXD | UART_TX/GPIO PB1/PWM4 output/SAR ADC input |
| 3 | PB7 | SPI_DO (data output)/UART_RX/SAR ADC Input/GPIO PB7 |
| 4 | GND | Ground |
| 5 | PB6 | SPI_DI (data input, I2C_SCL)/UART_RTS/SAR ADC input/GPIO PB6 |
| 6 | 3V3 | Power supply |
| 7 | PB5 | Cool/warm LED port C/PWM5 output/SAR ADC input/GPIO PB5 |
| 8 | PB4 | Cool/warm LED port W/PWM4 Output/SAR ADC input/GPIO PB4 |
| 9 | RST | Reset (active low) |
| 10 | GND | Ground |

## 功能索引

| I2C_SDA | PB6 |
| PWM0 | RXD |
| PWM4 | TXD、PB4 |
| PWM5 | PB5 |
| RXD | RXD |
| SPI_DI | PB6 |
| SPI_DO | PB7 |
| TXD | TXD |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：10）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
