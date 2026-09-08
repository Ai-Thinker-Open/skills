# Ai-M62-13-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-M62-13-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-M62-13-Kit Specification V1.0.1 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/ai_m62/Specification/Ai-M62-13-Kit_V1.0.1%20Specification-20240628.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | ADC | ADC pin，share voltage with IO 3 pin |
| 2 | IO30 | GPIO30/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 3 | IO0 | GPIO0/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH9/PWM0 |
| 4 | IO1 | GPIO1/SPI_SCLK/I2S_FS/I2C_SCL/ADC_CH8/PWM0 |
| 5 | IO28 | GPIO28/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH11/PWM0 |
| 6 | IO17 | Default available, the IO port is shared with the 32.768KHz crystal vibration output PIN foot inside the module. If the module of the internal patch 32.768KHz crystal vibration is customized, the IO is in the NC state.GPIO17/SPI_SCLK/I2S_FS/I2C_SCL/XTAL_32K_OUT/PWM0 |
| 7 | NC | NC |
| 8 | NC | NC |
| 9 | NC | NC |
| 10 | GND | Ground |
| 11 | 3V3 | 3.3V power supply |
| 12 | EN | Chip enabled pin, high level effective, cannot be used simultaneously with the RST |
| 13 | RTS/NC | Default NC, can be customized to reset pin, low level effective, if you need to use please contact Anxinke |
| 14 | GND | Ground |
| 15 | 5V | 5V power supply |
| 16 | 3V3 | 3.3Vpower supply |
| 17 | GND | Ground |
| 18 | TX | TXD/GPIO21/SPI_SCLK/I2S_FS/I2C_SCL/ADC_RCAL_VOUT/PWM0 |
| 19 | RX | RXD/GPIO22/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 20 | NC | NC |
| 21 | IO29 | GPIO29/SPI_SCLK/I2S_FS/I2C_SCL/PWM0 |
| 22 | IO27 | GPIO27/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/ADC_CH10/PWM0 |
| 23 | IO3 | GPIO3/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/ADC_CH3/PWM0 |
| 24 | GND | Ground |
| 25 | 3V3 | 3.3V power supply |
| 26 | NC | NC |
| 27 | IO2/NC | Default NC，not available to use，if need please contact Anxinke. If to pin out , it support Bootstrap/GPIO2/SPI_MISO/I2S_DI/I2S_RCLK_O/ I2C_SCL/ADC_CH2/PWM0 |
| 28 | IO20 | GPIO20/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH0/PWM0 |
| 29 | USB_DP | USB_DP |
| 30 | USB_DM | USB_DM |

## 功能索引

| ADC_CH0 | IO20 |
| ADC_CH10 | IO27 |
| ADC_CH11 | IO28 |
| ADC_CH2 | IO2/NC |
| ADC_CH3 | IO3 |
| ADC_CH8 | IO1 |
| ADC_CH9 | IO0 |
| GPIO0 | IO0 |
| GPIO1 | IO1 |
| GPIO17 | IO17 |
| GPIO2 | IO2/NC |
| GPIO20 | IO20 |
| GPIO21 | TX |
| GPIO22 | RX |
| GPIO27 | IO27 |
| GPIO28 | IO28 |
| GPIO29 | IO29 |
| GPIO3 | IO3 |
| GPIO30 | IO30 |
| I2C_SCL | IO30、IO0、IO28、RX、IO2/NC、IO20 |
| I2C_SDA | IO1、IO17、TX、IO29、IO27、IO3 |
| I2S_BCLK | IO0、IO28、IO20 |
| I2S_DI | IO30、RX、IO2/NC |
| I2S_DO | IO27、IO3 |
| I2S_FS | IO1、IO17、TX、IO29 |
| I2S_RCLK_O | IO30、RX、IO27、IO3、IO2/NC |
| PWM0 | IO30、IO0、IO1、IO28、IO17、RX、IO29、IO3、IO2/NC、IO20 |
| RXD | RX |
| SPI_MISO | IO30、RX、IO2/NC |
| SPI_MOSI | IO27、IO3 |
| SPI_SCLK | IO1、IO17、TX、IO29 |
| SPI_SS | IO0、IO28、IO20 |
| TXD | TX |
| USB_DM | USB_DM |
| USB_DP | USB_DP |
| XTAL_32K_OUT | IO17 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12, 13）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
