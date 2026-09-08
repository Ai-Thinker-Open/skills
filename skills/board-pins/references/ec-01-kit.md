# EC-01-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | EC-01-Kit |
| 分类 | NB-IoT |
| 规格书版本 | - Kit Specification |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ec-01-kit_v2.0.1specification.pdf) |

## 引脚定义表（8 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | IO6 | GPIO |
| 2 | IO7 | GPIO |
| 3 | R X0 | GPIO8/UART0_RXD |
| 4 | TX0 | GPIO9/UART0_TXD |
| 5 | IO10 | G PIO10 |
| 6 | IO11 | G PIO11 |
| 7 | GND | G round connection |
| 8 | 3V3 |  |

## 功能索引

| GPIO8 | R X0 |
| GPIO9 | TX0 |
| RXD | R X0 |
| TXD | TX0 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：13）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
