# PB-04-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | PB-04-Kit |
| 分类 | Bluetooth |
| 规格书版本 | PB-04-Kit Specification V1.0.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/Bluetooth/blue_tooth_pb/Specification/PB-04-Kit_V1.0.0%20Specification-20260604A.pdf) |

## 引脚定义表（22 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | 3V3 | 3.3V power supply |
| 2 | DIO / P2 | GPIO 2 / SWD debug data input/output port |
| 3 | CLK / P3 | GPIO 3 / SWD debug clock port |
| 4 | GND | Ground |
| 5 | P23 | GPIO 23 / ADC input 1 / Micbias output reference |
| 6 | P24 | GPIO 24 / ADC input 2 |
| 7 | P25 | GPIO 25 / ADC Input 8 |
| 8 | P20 | GPIO 20 / ADC input 9 / PGA positive input |
| 9 | P15 | GPIO 15 / ADC input 4 / Micbias output |
| 10 | GND | Ground |
| 11 | 5V | 5V power supply |
| 12 | GND | Ground |
| 13 | P16 | GPIO16 / 32.768kHz crystal input |
| 14 | P17 | GPIO17 / 32.768kHz crystal output |
| 15 | P14 | GPIO 14 / ADC input 3 |
| 16 | P11 | GPIO 11 / ADC input 0 |
| 17 | TM | Test mode enable |
| 18 | RST | Reset, active low |
| 19 | 3V3 | 3.3V power supply |
| 20 | P9 / TX | TXD / GPIO 9 |
| 21 | P10 / RX | RXD / GPIO 10 |
| 22 | GND | Ground Note: 1. The bottom test point is the TM pin, which functions as the Test Mode Enable pin. When TM is pulled high and RST is reset, the module enters download mode. If the pin is high at the moment of power-on, the module enters flashing mode. If the pin is low at the moment of power-on, the module boots normally. |

## 功能索引

| GPIO16 | P16 |
| GPIO17 | P17 |
| RXD | P10 / RX |
| TXD | P9 / TX |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：14）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
