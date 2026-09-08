# Ai-BS21-32S-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-BS21-32S-Kit |
| 分类 | NearLink |
| 规格书版本 | Ai-BS21-32S-Kit Specification V1.1.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/NearLink/sle-bs21/Specification/Ai-BS21-32S-Kit_V1.1.0%20Specification-20250829.pdf) |

## 引脚定义表（34 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | 3V3 | Positive power supply |
| 2 | RST | RESET/GPIO21/UART_H0_CTS/EXTLNA_RX_EN |
| 3 | IO25 | GPIO25/O32M/I2C0_CLK/RESERVED |
| 4 | IO11 | GPIO11/High-speed SPI_TXD/SPI2_TXD/PWM4 |
| 5 | IO12 | GPIO12/High-speed SPI_RXD/SPI2_CS0/PWM5 |
| 6 | IO13 | GPIO13/High-speed SPI_CS/SPI2_CS1/PWM6 |
| 7 | IO2 | GPIO2/AIN0/SPI0_TXD/DMIC_CLK/RESERVED |
| 8 | IO26 | GPIO26/I2C0_DATA/BT_WIFI_SW |
| 9 | IO27 | GPIO27/I2C1_CLK/BT_WIFI_SW |
| 10 | IO28 | GPIO28/AIN4/I2C1_DATA/RESERVED |
| 11 | IO29 | GPIO29/AIN5/QDEC_A/BT_STATUS |
| 12 | IO30 | GPIO30/AIN6/QDEC_B/RESERVED |
| 13 | IO31 | GPIO31/AIN7/LED_OUT/RESERVED |
| 16 | IO0 | GPIO0/XL1/SPI0_RXD/DMIC_DIN/EXTLNA_CTRL |
| 17 | IO1 | GPIO1/XL2/SPI0_TXD/DMIC_CLK/RESERVED |
| 18 | IO3 | GPIO3/AIN1/SPI0_CS0/I2S_SCLK/RESERVED |
| 20 | 5V | 5V power supply |
| 22 | IO4 | GPIO4/AIN2/SPI0_CS1/I2S_DOUT/BT_FEM_TX_EN |
| 23 | IO5 | GPIO5/AIN3/SPI1_RXD/I2S_DIN/RESERVED |
| 24 | IO6 | GPIO6/SPI1_TXD/I2S_MCLK |
| 25 | IO9 | GPIO9/NFC1/SPI1_CLK/PWM2 |
| 29 | IO10 | GPIO10/NFC2/SPI2_RXD/PWM3 |
| 30 | IO22 | GPIO22/UART_H0_RX_D/BT_FREQ |
| 31 | IO18 | GPIO18/UART_L1_TXD/PWM11 |
| 32 | IO17 | GPIO17/UART_L1_RTS/PWM10 |
| 33 | IO14 | GPIO14/High speed SPI_CLK/SPI2_CLK/PWM7 |
| 34 | IO15 | GPIO15/UART_L0_RXD/PWM8 |
| 35 | IO16 | GPIO16/UART_L0_TXD/PWM9 |
| 36 | S_CLK | SWD_CLK |
| 37 | S_DAT | SWD_DAT |
| 38 | RXD | GPIO20/UART_L1_RXD/PLUSE_CAPTURE |
| 39 | TXD | GPIO19/UART_L1_CTS/KEY_SCAN_BIR[0:31] |
| 40 | IO23 | GPIO23/UART_H0_RXD/BT_FREQ |
| 41 | IO24 | GPIO24/UART_H0_TXD/WLAN_ACTIVE |

## 功能索引

| GPIO0 | IO0 |
| GPIO1 | IO1 |
| GPIO10 | IO10 |
| GPIO11 | IO11 |
| GPIO12 | IO12 |
| GPIO13 | IO13 |
| GPIO14 | IO14 |
| GPIO15 | IO15 |
| GPIO16 | IO16 |
| GPIO17 | IO17 |
| GPIO18 | IO18 |
| GPIO19 | TXD |
| GPIO2 | IO2 |
| GPIO20 | RXD |
| GPIO21 | RST |
| GPIO22 | IO22 |
| GPIO23 | IO23 |
| GPIO24 | IO24 |
| GPIO25 | IO25 |
| GPIO26 | IO26 |
| GPIO27 | IO27 |
| GPIO28 | IO28 |
| GPIO29 | IO29 |
| GPIO3 | IO3 |
| GPIO30 | IO30 |
| GPIO31 | IO31 |
| GPIO4 | IO4 |
| GPIO5 | IO5 |
| GPIO6 | IO6 |
| GPIO9 | IO9 |
| I2S_DIN | IO5 |
| I2S_DOUT | IO4 |
| I2S_MCLK | IO6 |
| I2S_SCLK | IO3 |
| PWM10 | IO17 |
| PWM11 | IO18 |
| PWM2 | IO9 |
| PWM3 | IO10 |
| PWM4 | IO11 |
| PWM5 | IO12 |
| PWM6 | IO13 |
| PWM7 | IO14 |
| PWM8 | IO15 |
| PWM9 | IO16 |
| RXD | IO0、IO5、IO10、IO15、RXD、IO23 |
| SPI_CLK | IO14 |
| SPI_CS | IO13 |
| SPI_RXD | IO12 |
| SPI_TXD | IO11 |
| TXD | IO11、IO2、IO1、IO6、IO18、IO16、TXD、IO24 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：11, 12）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
