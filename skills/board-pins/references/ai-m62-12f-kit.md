# Ai-M62-12F-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-M62-12F-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-M62-12F-Kit Specification V1.0.1 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/ai_m62/Specification/Ai-M62-12F-Kit_V1.0.1%20Specification-20231115.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | ADC | ADC pin，share voltage with IO 20 pin |
| 2 | IO20 | GPIO20/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH0/PWM0 |
| 3 | NC | NC |
| 4 | 17/NC | Default available, the IO port is shared with the 32.768KHz crystal vibration output PIN foot inside the module. If the module of the internal patch 32.768KHz crystal vibration is customized, the IO is in the NC state.GPIO17/SPI_SCLK/I2S_FS/I2C_SCL/XTAL_32K_OUT/PWM0 |
| 5 | IO1 | GPIO1/SPI_SCLK/I2S_FS/I2C_SCL/ADC_CH8/PWM0 |
| 6 | IO30 | GPIO30/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 7 | IO0 | GPIO0/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH9/PWM0 |
| 8 | IO15/NC | Default available，the IO port is shared with Flash inside the module. If the external Flash module is customized, the IO is not usable. If you need to use it, please contact Ai-Thinker. GPIO15/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 9 | IO14/NC | Default available，the IO port is shared with Flash inside the module. If the external Flash module is customized, the IO is not usable. If you need to use it, please contact Ai-Thinker. GPIO14/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/ADC_CH4/PWM0 |
| 10 | GND | Ground |
| 11 | 3V3 | 3.3V power supply |
| 12 | EN | Chip enabled pin, high level effective |
| 13 | RST/NC | Default NC, is not usable |
| 14 | GND | Ground |
| 15 | 5V | 5V power supply |
| 16 | 3V3 | 3.3V power supply |
| 17 | GND | Ground |
| 18 | TX | TXD/GPIO21/SPI_SCLK/I2S_FS/I2C_SCL/ADC_RCAL_VOUT/PW |
| 19 | RX | RXD/GPIO22/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 20 | IO11/NC | Default available，the IO port is shared with Flash inside the module. If the external Flash module is customized, the IO is not usable. If you need to use it, please contact Ai-Thinker. GPIO11/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 21 | IO12/NC | Default available，the IO port is shared with Flash inside the module. If the external Flash module is customized, the IO is not usable. If you need to use it, please contact Ai-Thinker. GPIO12/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH6/PWM0 |
| 22 | USB_DP | USB_DP |
| 23 | USB_DM | USB_DM |
| 24 | GND | Ground |
| 25 | 3V3 | 3.3V power supply |
| 26 | IO28 | GPIO28/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH11/PWM0 |
| 27 | IO2/NC | Default NC，is not usable |
| 28 | IO3 | GPIO3/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/ADC_CH3/PWM0 |
| 29 | IO29 | GPIO29/SPI_SCLK/I2S_FS/I2C_SCL/PWM0 |
| 30 | IO27 | GPIO27/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/ADC_CH10/PWM0 |

## 功能索引

| ADC_CH0 | IO20 |
| ADC_CH10 | IO27 |
| ADC_CH11 | IO28 |
| ADC_CH3 | IO3 |
| ADC_CH4 | IO14/NC |
| ADC_CH6 | IO12/NC |
| ADC_CH8 | IO1 |
| ADC_CH9 | IO0 |
| GPIO0 | IO0 |
| GPIO1 | IO1 |
| GPIO11 | IO11/NC |
| GPIO12 | IO12/NC |
| GPIO14 | IO14/NC |
| GPIO15 | IO15/NC |
| GPIO17 | 17/NC |
| GPIO20 | IO20 |
| GPIO21 | TX |
| GPIO22 | RX |
| GPIO27 | IO27 |
| GPIO28 | IO28 |
| GPIO29 | IO29 |
| GPIO3 | IO3 |
| GPIO30 | IO30 |
| I2C_SCL | IO20、IO30、IO0、IO14/NC、RX、IO12/NC、IO28 |
| I2C_SDA | 17/NC、IO1、IO15/NC、TX、IO11/NC、IO3、IO29、IO27 |
| I2S_BCLK | IO20、IO0、IO12/NC、IO28 |
| I2S_DI | IO30、IO14/NC、RX |
| I2S_DO | IO15/NC、IO11/NC、IO3、IO27 |
| I2S_FS | 17/NC、IO1、TX、IO29 |
| I2S_RCLK_O | IO30、IO15/NC、IO14/NC、RX、IO11/NC、IO3、IO27 |
| PWM0 | IO20、17/NC、IO1、IO30、IO0、IO15/NC、IO14/NC、RX、IO11/NC、IO12/NC、IO28、IO3、IO29 |
| RXD | RX |
| SPI_MISO | IO30、IO14/NC、RX |
| SPI_MOSI | IO15/NC、IO11/NC、IO3、IO27 |
| SPI_SCLK | 17/NC、IO1、TX、IO29 |
| SPI_SS | IO20、IO0、IO12/NC、IO28 |
| TXD | TX |
| USB_DM | USB_DM |
| USB_DP | USB_DP |
| XTAL_32K_OUT | 17/NC |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12, 13）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
