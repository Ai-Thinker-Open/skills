# BU03-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | BU03-Kit |
| 分类 | UWB |
| 规格书版本 | BU03-Kit SpecificationV1.1.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/UWB/uwb_1/Specification/BU03-Kit_V1.1.0%20Specification-20240905.pdf) |

## 引脚定义表（40 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | PB12 | PB12,SPI2_NSS/I2C2_SMBAl/USART3_CK/TIM1_BKIN |
| 2 | PB13 | PB13,SPI2_SCK/USART3_CTS/TIM1_CH1N |
| 3 | PB14 | PB14,SPI2_MISO/USART3_RTSTIM1_CH2N |
| 4 | PB15 | PB15,SPI2_MOSI/TIM1_CH3N |
| 5 | EXTON | EXTON_PA8 |
| 6 | TX1 | UART1_TX |
| 7 | RX1 | UART1_RX |
| 8 | WAKEUP | PA0WKUP,PA0,WKUP/USART2_CTS(9)/ADC12_IN0/TIM2_ CH1_ETR |
| 9 | LED_RUN | PA1_LED_RUN |
| 10 | PA15 | JTDI,,TIM2_CH1_ETR/PA15/SPI1_NSS |
| 11 | PA3 | PA3,,USART2_RX/ADC12_IN3/TIM2_CH4 |
| 12 | PB4 | JNTRST,TIM3_CH1/PB4/SPI1_MISO |
| 13 | PB8 | PB8,TIM4_CH3,I2C1_SCL/CANRX |
| 14 | PB9 | PB9,TIM4_CH4,I2C1_SDA/CANTX |
| 15 | V-BAT | V-BAT |
| 16 | GND | GND |
| 17 | SWDIO | SWDIO |
| 18 | SWCLK | SWCLK |
| 19 | 3V3 | 3V3 power supply |
| 20 | 5V | 5V power supply |
| 21 | 3V3 | 3V3 power supply |
| 22 | GND | GND |
| 23 | PC13 | PC13-TAMPER-RTC,PC13,TAMPER-RTC |
| 24 | NRST | NRST |
| 25 | I2C1_SCL | I2C1_SCL/PB7 |
| 26 | I2C1_SDA | I2C1_SDA/PB7 |
| 27 | DW_RSTN | RSTN |
| 28 | I2C3_SDA | PB11,I2C2_SDA/USART3_RX,TIM2_CH4 |
| 29 | I2C2_SCL | PB10,I2C2_SCL/USART3_TX,TIM2_CH3 |
| 30 | PA2 | PA2,USART2_TX/ADC12_IN2/TIM2_CH3 |
| 31 | PA3 | PA3,USART2_RX/ADC12_IN3/TIM2_CH4 |
| 32 | SPI1_CSN | SPI1_CSN |
| 33 | SPI1_MOSI | SPI1_MOSI |
| 34 | SPI1_MISO | SPI1_MISO |
| 35 | SPI1_CLK | SPI1_CLK |
| 36 | DW_IRQ | DW_IRQ/GPIO8 |
| 37 | IO4 | IO4/EXTPA |
| 38 | IO5 | IO5/EXTTXE/SPIPOL |
| 39 | IO6 | IO6/EXTRXE/SPIPHA |
| 40 | IO7 | DW_SYNC |

## 功能索引

| GPIO8 | DW_IRQ |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：11, 12）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
