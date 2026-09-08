# TB-03F-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | TB-03F-Kit |
| 分类 | Bluetooth |
| 规格书版本 | TB-03F-KIT Specification |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/Bluetooth/blue_tooth/Specification/TB-03F-Kit%20Specification-20201203.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | RST | reset |
| 2 | C4 | PWM2 output/UART_CTS/PWM0 reverse output/SAR ADC input/GPIO PC4 |
| 3 | SWS | Single Line Slave/UART_RTS/GPIO PA7 |
| 4 | C3 | PWM1 output/UART_RX/I2C Serial Clock/32kHz Crystal input（selection）/GPIO PC3 |
| 5 | D7 | GPIO PD7/SPI clock（I2C_SCK） |
| 6 | B7 | SPI_DO data output/UART_RX/SAR ADC input/GPIO PB7 |
| 7 | B6 | SPI_DI data input （I2C_SCL ）/UART_RTS/SAR ADC input/GPIO PB6 |
| 8 | NC | Empty |
| 9 | NC | Empty |
| 10 | GND | Ground |
| 11 | 3V3 | 3.3V power supply TB-03F-kit specification V1.0 |
| 12 | NC | Empty |
| 13 | NC | Empty |
| 14 | GND | Ground |
| 15 | 5V | 5V power supply |
| 16 | VCC | 3.3V power supply |
| 17 | GND | Ground |
| 18 | TXD | UART_TX/GPIO PB1/PWM4 output/SAR ADC input |
| 19 | RXD | UART_RX/GPIO PA0/PWM0 reverse output |
| 20 | B5 | PWM5 output/SAR ADC input/GPIO PB5 |
| 21 | B4 | PWM4 output/SAR ADC input/GPIO PB4 |
| 22 | C2 | PWM0 output/I2C serial data/32kHz Crystal output （selection）/GPIO PC2 |
| 23 | A1 | GPIO PA1/ I2S_clock |
| 24 | GND | Ground |
| 25 | 3V3 | 3.3V power supply |
| 256 | D2 | GPIO PD2/PWM3 output/SPI Chip Selection （Low Level Effective）/I2S_LR |
| 27 | D3 | GPIO PD3/PWM1 reverse output/I2S_SDI |
| 28 | D4 | GPIO PD4/Single Line Host SWM/PWM2 Reverse output/I2S_SDO |
| 29 | C1 | I2C_CLK/PWM1 Reverse output/PWM0 output/GPIO PC1 |
| 30 | C0 | I2C_SCL/PWM4 Reverse output/UART_RTS /GPIO PC0 |

## 功能索引

| I2C_CLK | C1 |
| I2C_SCK | D7 |
| I2C_SDA | B6、C0 |
| I2S_LR | D2 |
| I2S_SDI | D3 |
| I2S_SDO | D4 |
| PWM0 | C4、RXD、C2、C1 |
| PWM1 | C3、D3、C1 |
| PWM2 | C4、D4 |
| PWM3 | D2 |
| PWM4 | TXD、B4、C0 |
| PWM5 | B5 |
| RXD | RXD |
| SPI_DI | B6 |
| SPI_DO | B7 |
| TXD | TXD |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：8, 9）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
