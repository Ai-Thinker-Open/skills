# Rd-Kit 开发板引脚/接口配置

> 本文件是 `board-pins` skill 的**单板参考文档**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Rd-Kit |
| 分类 | 雷达调试板 |
| 规格书版本 | Rd-Kit Specification V1.1.2 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/Radar/rd-kit/Specification/Rd-Kit_V1.1.2%20Specification-20250627.pdf) |

## 说明：引脚信息为"雷达模组接口连接器"，非编号 GPIO 引脚表

Rd-Kit 是**雷达调试底板**（BLE 调试），其接口信息在规格书中为**雷达模组连接器类型表**（表 4 Radar interface parameter table），而非按数字编号展开的 GPIO 引脚定义表，无法以"脚序/名称/功能"形式自动展开：

| 雷达模组 | 接口 |
|:---|:---|
| Rd-03D, Rd-03D_V2 | 2.54mm 单排 1x4P 公头 |
| Rd-03E | 2.54mm 单排 1x5P 母头 |
| Rd-02C | 2.54mm 单排 1x5P 母头 |
| Rd-03, Rd-03_V2, Rd-03L, Rd-03L_V2 | 2.54mm 单排 1x5P 母头 |
| Rd-04 | 2.00mm 单排 1x6P 母头 |
| Rd-02B | 详见规格书 |

**注意**：Rd-04 内置 MCU，如需与 Rd-Kit 配合需拆除 MCU 并自行连接 I2C_EN 排针（见规格书图 10）。

## 引脚数据状态

- ⏳ **未展开编号引脚表**：官方规格书中引脚以雷达模组接口连接器、板级状态灯（一红五蓝）及 BLE 固件说明呈现，无标准编号 GPIO 引脚映射。
- 如需具体引脚，请以官方规格书/原理图及 [Rd-Kit 调试板使用指导](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/Radar/rd-kit/Support/radar_rd-kit_usermanual.pdf) 为准。

## 数据来源与核对说明

> 本文件由规格书自动解析生成，**接口连接器信息以官方规格书为准**；未包含编号引脚表，需人工依据原理图补充。
