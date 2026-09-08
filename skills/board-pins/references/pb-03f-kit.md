# PB-03F-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | PB-03F-Kit |
| 分类 | Bluetooth |
| 规格书版本 | PB-03F-Kit Specification V1.0.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/Bluetooth/blue_tooth_pb/Specification/PB-03F-Kit_V1.0.0%20Specification-20211202.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | P13 | GPIO13 |
| 2 | P11 | GPIO11 |
| 3 | P31 | GPIO11 |
| 4 | P7 | GPIO7 |
| 5 | P32 | GPIO32 |
| 6 | P33 | GPIO33 |
| 7 | P14 | GPIO14/ADC input 3 |
| 8 | P16 | GPIO16 |
| 9 | P17 | GPIO17 |
| 10 | GND | Ground Pin |
| 11 | 3V3 | 3.3V power supply |
| 12 | NC | Empty |
| 13 | NC | Empty |
| 14 | GND | Ground Pin |
| 15 | 5V | 5V power supply |
| 16 | 3V3 | 3.3V power supply |
| 17 | GND | Ground Pin |
| 18 | TX0 | TXD/GPIO9 |
| 19 | RX0 | RXD/GPIO10 |
| 20 | P18 | GPIO18 |
| 21 | P0 | GPIO0 |
| 22 | P34 | GPIO34 |
| 23 | NC | Empty |
| 24 | GND | Ground Pin |
| 25 | 3V3 | 3.3V power supply |
| 26 | P2 | GPIO2/SWD debug data inout |
| 27 | P3 | GPIO3/SWD debug clock |
| 28 | P20 | GPIO20/ADC input 9/PGA positive input |
| 29 | P23 | GPIO23/ADC input 1/micbias reference |
| 30 | P24 | GPIO24 |

## 功能索引

| GPIO0 | P0 |
| GPIO10 | RX0 |
| GPIO11 | P11、P31 |
| GPIO13 | P13 |
| GPIO14 | P14 |
| GPIO16 | P16 |
| GPIO17 | P17 |
| GPIO18 | P18 |
| GPIO2 | P2 |
| GPIO20 | P20 |
| GPIO23 | P23 |
| GPIO24 | P24 |
| GPIO3 | P3 |
| GPIO32 | P32 |
| GPIO33 | P33 |
| GPIO34 | P34 |
| GPIO7 | P7 |
| GPIO9 | TX0 |
| RXD | RX0 |
| TXD | TX0 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：11, 12）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
