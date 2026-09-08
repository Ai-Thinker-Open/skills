# TB-04-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | TB-04-Kit |
| 分类 | Bluetooth |
| 规格书版本 | TB-04-KIT Specification |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/Bluetooth/blue_tooth/Specification/TB-04-Kit%20Specification-20200930.pdf) |

## 引脚定义表（9 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 12 | D3 | PWM1 reverse output/UART_TX/GPIO PD3 |
| 13 | D4 | PWM2 reverse output/SWM/GPIO PD4 |
| 14 | D7 | SPI clock/UART_TX/GPIO PD7 |
| 15 | A1 | GPIPO PA1 |
| 16 | SWS | Single line slave/UART_RTS/GPIO PA7 |
| 17 | TXD | UART TX/GPIO PB1 |
| 18 | RXD | UART RX/GPIO PA0 |
| 19 | GND | Ground |
| 20 | 3V3 | Power supply |

## 功能索引

| PWM1 | D3 |
| PWM2 | D4 |
| RXD | RXD |
| TXD | TXD |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：9）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
