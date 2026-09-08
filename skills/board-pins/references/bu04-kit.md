# BU04-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | BU04-Kit |
| 分类 | UWB |
| 规格书版本 | BU04-Kit SpecificationV1.1.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/UWB/uwb_1/Specification/BU04-Kit_V1.1.0%20Specification-20240819.pdf) |

## 引脚定义表（40 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | GND | GND |
| 2 | ST_NRST | NRST |
| 3 | LED_RUN | PA1_LED_RUN，ADC_IN1 / USART2_RTS / TIM2_CH2 |
| 4 | UART2_TX | ADC_IN2 / USART2_TX / TIM2_CH3 |
| 5 | UART2_RX | ADC_IN3 / USART2_RX / TIM2_CH4 |
| 6 | PB15 | PB15,SPI2_MOSI/TIM1_CH3N |
| 7 | PB14 | PB14,SPI2_MISO/USART3_RTSTIM1_CH2N |
| 8 | PB13 | PB13,SPI2_SCK/USART3_CTS/TIM1_CH1N |
| 9 | PB12 | PB12,SPI2_NSS/I2C2_SMBAl/USART3_CK/TIM1_BKIN |
| 10 | GND | GND |
| 11 | DW_WAKEUP | PA0WKUP,PA0,WKUP/USART2_CTS(9)/ADC12_IN0/TIM2_ CH1_ETR |
| 12 | DW_RXTN | DW_RXTN |
| 13 | SPI1_CLK | ADC_IN5 / SPI1_SCK |
| 14 | SPI1_MOSI | ADC_IN7 / SPI1_MOSI / TIM3_CH2 |
| 15 | SP1_MISO | ADC_IN6 / SPI1_MISO / TIM3_CH1 |
| 16 | SPI1_CSN | ADC_IN4 / SPI1_NSS / USART2_CK |
| 17 | DW_IRQIO | DW_IRQ/GPIO8 |
| 18 | WIFI_BOOT | WIFI_BOOT |
| 19 | WIFI_RXD | WIFI_RXD |
| 20 | WIFI_TXD | WIFI_TXD |
| 21 | GND | GND |
| 22 | 5V | 5V |
| 23 | 3V3 | 3V3 |
| 24 | LEDRX | LEDRX |
| 25 | LEDTX | LEDTX |
| 26 | DW_GPIO5 | IO5/EXTTXE/SPIPOL |
| 27 | DW_GPIO6 | IO6/EXTRXE/SPIPHA |
| 28 | DW_SYNC | DW_SYNC |
| 29 | 3V3 | 3V3 page 12 of 16 |
| 30 | EXTON | EXTON_PA8 |
| 31 | UART1_TX | UART1_TX |
| 32 | UART1_RX | UART1_RX |
| 33 | USB_DM | USB_DM |
| 34 | USB_DP | USB_DP |
| 35 | I2C1_SCL | I2C1_SDA / TIM4_CH2 / USART1_RX |
| 36 | I2C1_SDA | I2C1_SCL / TIM4_CH1 / USART1_TX |
| 37 | GND | GND |
| 38 | SWDIO | SWDIO |
| 39 | SWCLK | SWCLK |
| 40 | 3V3 | 3V3 |

## 功能索引

| GPIO5 | DW_GPIO5 |
| GPIO6 | DW_GPIO6 |
| GPIO8 | DW_IRQIO |
| RXD | WIFI_RXD |
| TXD | WIFI_TXD |
| USB_DM | USB_DM |
| USB_DP | USB_DP |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：11, 12）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
