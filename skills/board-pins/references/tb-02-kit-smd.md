# TB-02-Kit(SMD) 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | TB-02-Kit(SMD) |
| 分类 | Bluetooth |
| 规格书版本 | TB-02-Kit Specification V1.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/Bluetooth/blue_tooth/Specification/TB-02-Kit%28DIP-16%29_V1.0%20Specification-20260721A.pdf) |

## 引脚定义表（10 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | GND | Ground |
| 2 | RST | Reset pin |
| 3 | GND | Ground |
| 4 | 3V3 | Power supply |
| 5 | RXD | UART RX |
| 6 | TXD | UART TX |
| 7 | GND | Ground |
| 8 | 5V | 5V power supply |
| 9 | SWS | Single-wire slave/UART_RTS/GPIO PA7 |
| 10 | PD2 | SPI chip select (active low)/PWM3 output/GPIO PD2 |

## 功能索引

| PWM3 | PD2 |
| RXD | RXD |
| TXD | TXD |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：10）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
