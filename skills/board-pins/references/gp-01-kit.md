# GP-01-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | GP-01-Kit |
| 分类 | GPS |
| 规格书版本 | GP-01-Kit Specification |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/GPS/gps_1/Specification/GP-01-Kit_V1.0%20Specification-20210729.pdf) |

## 引脚定义表（9 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | GND | Grounded |
| 2 | VCC | 5Vpower supply |
| 3 | RX1 | General GPIO，the default is RXD of UART0 |
| 4 | TX1 | General GPIO，the default is TXD of UART0 |
| 5 | GND | Grounded |
| 6 | VCC | 5Vpower supply |
| 7 | N/F | Shutdown control, keep high level during normal operation; internal pull-up |
| 8 | PPS | Time pulse signal |
| 9 | Micro USB | This interface only provides power supply function 5. Schematic diagram Figure 5 Schematic diagram of the development board |

## 功能索引

| RXD | RX1 |
| TXD | TX1 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：10）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
