# EC-01F-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | EC-01F-Kit |
| 分类 | NB-IoT |
| 规格书版本 | Specification |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ec-01f-kit_v2.0.1specification.pdf) |

## 引脚定义表（14 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | 3V3 | 3.3V power supply |
| 2 | RX1 | GPIO14/UART1_RXD |
| 3 | TX1 | GPIO15/UART1_TXD |
| 4 | ADC4 | ADC Channel AIO4 |
| 5 | SWDIO | SWDIO/Serial Wire Debug Data |
| 6 | SWCLK | SWCLK/Serial Wire Debug Clock |
| 7 | IO1 | GPIO1 |
| 8 | RX0 | GPIO8/UART0_RXD |
| 9 | TX0 | GPIO9/UART0_TXD |
| 10 | NC | NC |
| 11 | IO6 | GPIO6/UART0_RSTn |
| 12 | IO5 | GPIO5 |
| 13 | IO3V3 | IO3V3 |
| 14 | GND | Ground Connection |

## 功能索引

| GPIO1 | IO1 |
| GPIO14 | RX1 |
| GPIO15 | TX1 |
| GPIO5 | IO5 |
| GPIO6 | IO6 |
| GPIO8 | RX0 |
| GPIO9 | TX0 |
| RXD | RX1、RX0 |
| TXD | TX1、TX0 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：13）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
