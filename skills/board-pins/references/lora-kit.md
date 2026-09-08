# LoRa-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | LoRa-Kit |
| 分类 | LoRa |
| 规格书版本 | LoRa-Kit Specification V1.0.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/LoRa/lora/Specification/LoRa-Kit_V1.0.0%20Specification-20240410.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | GND | Ground |
| 2 | 3V3 | 3.3 V power supply; external power supply input current is recommended to be above 500 mA |
| 3 | RESET | LORA_RESET: Reset pin for LoRa module |
| 4 | DIO0 | LORA_DIO0: Digital IO0 software configuration for LoRa module |
| 5 | DIO1 | LORA_DIO1: Digital IO1 software configuration for LoRa module |
| 6 | CTR1 | CTR1: Applied to the driving of Ra-03SCH RF switch |
| 7 | CTR2 | CTR2: Applied to the driving of Ra-03SCH RF switch |
| 8 | GND | Ground |
| 9 | DIO4 | LORA_DIO4: Digital IO4 software configuration for LoRa module |
| 10 | NC | NC |
| 11 | SCK | SPI_SCK: SPI clock input for LoRa module |
| 12 | MISO | SPI_MISO: SPI data output for LoRa module |
| 13 | MOSI | SPI_MOSI: SPI data input for LoRa module |
| 14 | NSS | SPI_NSS：SPI chip select input for LoRa module |
| 15 | GND | Ground |
| 16 | GND | Ground |
| 17 | SWCLK | SWCLK: Programming interface for the STM32F103CBT6 chip |
| 18 | SWDIO | SWDIO: Programming interface for the STM32F103CBT6 chip |
| 19 | 3V3 | 3.3 V power supply; external power supply input current is recommended to be above 500 mA |
| 20 | GND | Ground |
| 21 | RX3 | UART3_RX: Reserved UART interface |
| 22 | TX3 | UART3_TX: Reserved UART interface |
| 23 | 5V | 5 V power supply; external power supply input current is recommended to be above 500 mA |
| 24 | GND | Ground |
| 25 | BT_TX | BLE_TX: STM32F103CBT6 and TB-05 communication port |
| 26 | BT_RX | BLE_RX: STM32F103CBT6 and TB-05 communication port |
| 27 | BT_RX | BLE_RX: TB-05 programming control pin |
| 28 | SWS | SWS: TB-05 programming control pin |
| 29 | LORA_3V3 | 3.3 V power supply; external power supply input current is recommended to be above 500 mA |
| 30 | 3V3 | 3.3 V power supply; external power supply input current is recommended to be above 500 mA Note: Short-circuit pins 29 and 30 with a jumper cap to supply power to the LoRa module. Table 9 Ra-01 Adapter Board Pin Function Definition PinNo. Name FunctionDescription |

## 功能索引

| SPI_MISO | MISO |
| SPI_MOSI | MOSI |
| SPI_NSS | NSS |
| SPI_SCK | SCK |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：11, 12, 15）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
