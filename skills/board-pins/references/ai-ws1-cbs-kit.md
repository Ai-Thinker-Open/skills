# Ai-WS1-CBS-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-WS1-CBS-Kit |
| 分类 | NearLink |
| 规格书版本 | Ai-WS1-CBS-Kit Specification |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/NearLink/ai-ws1/Specification/Ai-WS1-CBS-Kit_V1.0.0%20Specification-20241028.pdf) |

## 引脚定义表（16 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | IO2 | GPIO2 |
| 2 | IO1 | GPIO1 |
| 3 | IO0 | GPIO0 |
| 4 | P_on | Boot pin |
| 5 | IO10 | GPIO10 |
| 6 | NC | Hang out |
| 7 | GND | Ground |
| 8 | 3V3 | 3.3V power supply. The recommended output current of the external power supply is more than 500mA |
| 9 | NC | Hang out |
| 10 | GND | Ground |
| 11 | NC | Hang out |
| 12 | NC | Hang out |
| 13 | NC | Hang out |
| 14 | IO9 | GPIO9 |
| 15 | IO3 | GPIO3 |
| 16 | IO11 | GPIO11 Front Back |

## 功能索引

| GPIO0 | IO0 |
| GPIO1 | IO1 |
| GPIO10 | IO10 |
| GPIO11 | IO11 |
| GPIO2 | IO2 |
| GPIO3 | IO3 |
| GPIO9 | IO9 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：10）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
