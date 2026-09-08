# Ra-08-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ra-08-Kit |
| 分类 | LoRaWAN |
| 规格书版本 | - Kit 规格书 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/LoRaWan/Ra-08/Specification/Ra-08-Kit_V1.2.0%E8%A7%84%E6%A0%BC%E4%B9%A6-20220620.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | IO8 | GPIO8/ADC_IN1 |
| 2 | IO11 | GPIO11/ADC_IN0 |
| 3 | NC | NC |
| 4 | IO9 | GPIO9/DAC_OUT |
| 5 | IO4 | GPIO4/SSP1_CLK |
| 6 | IO5 | GPIO5/SSP1_NSS |
| 7 | NC | NC |
| 8 | IO7 | GPIO7/SWD_CLK |
| 9 | IO6 | GPIO6/SWD_DATA |
| 10 | GND | 地线，连接到电源参考地 |
| 11 | 3V3 | 3.3V 供电，推荐供电电流大于 5 00mA |
| 12 | NC | NC |
| 13 | RST | RSTN_IN 外部复位 |
| 14 | GND | 地线，连接到电源参考地 |
| 15 | 5V | 5 V 供电，推荐供电电流大于 5 00mA |
| 16 | 3V3 | 3.3V 供电，推荐供电电流大于 5 00mA |
| 17 | GND | 地线，连接到电源参考地 |
| 18 | TX | GPIO17/UART TX |
| 19 | RX | GPIO60/LPUART - RX 或GPIO16/UART RX |
| 20 | NC | NC |
| 21 | NC | NC |
| 22 | NC | NC |
| 23 | NC | NC |
| 24 | GND | 地线，连接到电源参考地 |
| 25 | 3V3 | 3.3V 供电，推荐供电电流大于 5 00mA |
| 26 | IO14 | GPIO14/I2C_SCL |
| 27 | IO15 | GPIO15/I2C_SCL |
| 28 | IO2 | GPIO2/BOOT |
| 29 | NC | NC |
| 30 | NC | NC 表 6 模块启动模式说明 表 管脚 默认状态 SPI 启动模式 下载启动模式 IO2 下拉 |

## 功能索引

| GPIO11 | IO11 |
| GPIO14 | IO14 |
| GPIO15 | IO15 |
| GPIO16 | RX |
| GPIO17 | TX |
| GPIO2 | IO2 |
| GPIO4 | IO4 |
| GPIO5 | IO5 |
| GPIO6 | IO6 |
| GPIO60 | RX |
| GPIO7 | IO7 |
| GPIO8 | IO8 |
| GPIO9 | IO9 |
| I2C_SCL | IO14 |
| I2C_SDA | IO15 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12, 13）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
