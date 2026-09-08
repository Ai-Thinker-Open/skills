# Ai-M62-M2-I-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-M62-M2-I-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-M62-M2-I-Kit Specification V1.1.1 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/ai_m62/Specification/Ai-M62-M2-I-Kit_V1.1.1%20Specification-20240626.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | IO10 | GPIO10/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/ADC_CH7/PWM0 |
| 2 | IO16 | Default available, the IO port is shared with the 32.768KHz crystal vibration output PIN foot inside the module. If the module of the internal patch 32.768KHz crystal vibration is customized, the IO is in the NC state.GPIO16/SPI_SS/I2S_BCLK/I2C_SCL/XTAL_32K_IN/PWM0 |
| 3 | IO17 | Default available, the IO port is shared with the 32.768KHz crystal vibration output PIN foot inside the module. If the module of the internal patch 32.768KHz crystal vibration is customized, the IO is in the NC state.GPIO17/SPI_SCLK/I2S_FS/I2C_SCL/XTAL_32K_OUT/PWM0 |
| 4 | IO11 | GPIO11/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 5 | IO12 | GPIO12/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH6/PWM0 |
| 6 | IO13 | GPIO13/SPI_SCLK/I2S_FS/I2C_SCL/ADC_CH5/PWM0 |
| 7 | USB+ | USB_DM |
| 8 | USB- | USB_DP |
| 9 | IO20 | GPIO20/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH0/PWM0 |
| 10 | IO14 | GPIO14/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/ADC_CH4/PWM0 |
| 11 | IO15 | GPIO15/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 12 | NC | NC |
| 13 | EN | Default as a chip enabled, high level effective |
| 14 | IO2/NC | Default NC, not available, if you want to use, please contact Ai-Thinker. If pin out, it support the Bootstrap/GPIO2/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/ADC_CH2/P WM0 |
| 15 | 5V | 5V power supply |
| 16 | 3V3 | 3.3Vpower supply |
| 17 | GND | Ground |
| 18 | TX | TXD/GPIO21/SPI_SCLK/I2S_FS/I2C_SCL/ADC_RCAL_VOUT/PWM0 |
| 19 | RX | RXD/GPIO22/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 20 | IO30 | GPIO30/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 21 | IO1 | GPIO1/SPI_SCLK/I2S_FS/I2C_SCL/ADC_CH8/PWM0 |
| 22 | IO0 | GPIO0/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH9/PWM0 |
| 23 | IO3 | GPIO3/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/ADC_CH3/PWM0 |
| 24 | IO27 | GPIO27/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/ADC_CH10/PWM0 |
| 25 | IO28 | GPIO28/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH11/PWM0 |
| 26 | IO29 | GPIO29/SPI_SCLK/I2S_FS/I2C_SCL/PWM0 |
| 27 | NC | NC |
| 28 | NC | NC |
| 29 | NC | NC |
| 30 | NC | NC |

## 功能索引

| ADC_CH0 | IO20 |
| ADC_CH10 | IO27 |
| ADC_CH11 | IO28 |
| ADC_CH2 | IO2/NC |
| ADC_CH3 | IO3 |
| ADC_CH4 | IO14 |
| ADC_CH5 | IO13 |
| ADC_CH6 | IO12 |
| ADC_CH7 | IO10 |
| ADC_CH8 | IO1 |
| ADC_CH9 | IO0 |
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
| GPIO2 | IO2/NC |
| GPIO20 | IO20 |
| GPIO21 | TX |
| GPIO22 | RX |
| GPIO27 | IO27 |
| GPIO28 | IO28 |
| GPIO29 | IO29 |
| GPIO3 | IO3 |
| GPIO30 | IO30 |
| I2C_SCL | IO10、IO16、IO12、IO20、IO14、IO2/NC、RX、IO30、IO0、IO28 |
| I2C_SDA | IO17、IO11、IO13、IO15、TX、IO1、IO3、IO27、IO29 |
| I2S_BCLK | IO16、IO12、IO20、IO0、IO28 |
| I2S_DI | IO10、IO14、IO2/NC、RX、IO30 |
| I2S_DO | IO11、IO15、IO3、IO27 |
| I2S_FS | IO17、IO13、TX、IO1、IO29 |
| I2S_RCLK_O | IO10、IO11、IO14、IO15、IO2/NC、RX、IO30、IO3、IO27 |
| PWM0 | IO10、IO16、IO17、IO11、IO12、IO13、IO20、IO14、IO15、TX、RX、IO30、IO1、IO0、IO3、IO27、IO28、IO29 |
| RXD | RX |
| SPI_MISO | IO10、IO14、IO2/NC、RX、IO30 |
| SPI_MOSI | IO11、IO15、IO3、IO27 |
| SPI_SCLK | IO17、IO13、TX、IO1、IO29 |
| SPI_SS | IO16、IO12、IO20、IO0、IO28 |
| TXD | TX |
| USB_DM | USB+ |
| USB_DP | USB- |
| XTAL_32K_IN | IO16 |
| XTAL_32K_OUT | IO17 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12, 13）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
