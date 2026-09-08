# Ai-M62-32S-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-M62-32S-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-M62-32S-Kit Specification V1.0.1 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/ai_m62/Specification/Ai-M62-32S-Kit_V1.0.1%20Specification-20240703.pdf) |

## 引脚定义表（38 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | 3V3 | 3.3V power supply |
| 2 | EN | Chip enabled pin, high level effective |
| 3 | NC | NC |
| 4 | IO3 | GPIO3/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/ADC_CH3/PWM0 |
| 5 | 11/NC | The default is available, and the IO port is shared with Flash inside the module. If the external Flash module is customized, the IO is not usable. If you need to use it, please contact Ai-Thinker GPIO11/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 6 | 12/NC | The default is available, and the IO port is shared with Flash inside the module. If the external Flash module is customized, the IO is not usable. If you need to use it, please contact Ai-Thinker GPIO11/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 7 | IO1 | GPIO1/SPI_SCLK/I2S_FS/I2C_SCL/ADC_CH8/PWM0 |
| 8 | IO30 | GPIO30/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 9 | IO0 | GPIO0/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH9/PWM0 |
| 10 | IO13/NC | GPIO13/SPI_SCLK/I2S_FS/I2C_SCL/ADC_CH5/PWM0 |
| 11 | IO14/NC | The default is available, and the IO port is shared with Flash inside the module. If the external Flash module is customized, the IO is not usable. If you need to use it, please contact Ai-Thinker GPIO15/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 12 | IO15/NC | The default is available, and the IO port is shared with Flash inside the module. If the external Flash module is customized, the IO is not usable. If you need to use it, please contact Ai-Thinker GPIO15/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 13 | IO16 | GPIO16/SPI_SS/I2S_BCLK/I2C_SCL/XTAL_32K_IN/PWM0 |
| 14 | GND | Ground |
| 15 | NC | NC |
| 16 | NC | NC |
| 17 | NC | NC |
| 18 | NC | NC |
| 19 | 5V | 5V power supply |
| 20 | NC | NC |
| 21 | NC | NC |
| 22 | NC | NC Page 13of 17 |
| 23 | NC | NC |
| 24 | NC | NC |
| 25 | IO2/NC | Default NC, is not available |
| 26 | IO10 | GPIO10/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/ADC_CH7/PWM0 |
| 27 | IO28 | GPIO28/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH11/PWM0 |
| 28 | IO17 | GPIO17/SPI_SCLK/I2S_FS/I2C_SCL/XTAL_32K_OUT/PWM0 |
| 29 | NC | NC |
| 30 | IO27 | GPIO27/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/ADC_CH10/PWM0 |
| 31 | IO29 | GPIO29/SPI_SCLK/I2S_FS/I2C_SCL/PWM0 |
| 32 | DM | USB_DM |
| 33 | DP | USB_DP |
| 34 | RX | RXD/GPIO22/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 35 | TX | TXD/GPIO21/SPI_SCLK/I2S_FS/I2C_SCL/ADC_RCAL_VOUT/PWM0 |
| 36 | IO20 | GPIO20/SPI_SS/I2S_BCLK/I2C_SCL/ADC_CH0/PWM0 |
| 37 | NC | NC |
| 38 | GND | Ground |

## 功能索引

| ADC_CH0 | IO20 |
| ADC_CH10 | IO27 |
| ADC_CH11 | IO28 |
| ADC_CH3 | IO3 |
| ADC_CH5 | IO13/NC |
| ADC_CH7 | IO10 |
| ADC_CH8 | IO1 |
| ADC_CH9 | IO0 |
| GPIO0 | IO0 |
| GPIO1 | IO1 |
| GPIO10 | IO10 |
| GPIO11 | 11/NC、12/NC |
| GPIO13 | IO13/NC |
| GPIO15 | IO14/NC、IO15/NC |
| GPIO16 | IO16 |
| GPIO17 | IO17 |
| GPIO20 | IO20 |
| GPIO21 | TX |
| GPIO22 | RX |
| GPIO27 | IO27 |
| GPIO28 | IO28 |
| GPIO29 | IO29 |
| GPIO3 | IO3 |
| GPIO30 | IO30 |
| I2C_SCL | IO30、IO0、IO16、IO10、IO28、RX、IO20 |
| I2C_SDA | IO3、11/NC、12/NC、IO1、IO13/NC、IO14/NC、IO15/NC、IO17、IO27、IO29、TX |
| I2S_BCLK | IO0、IO16、IO28、IO20 |
| I2S_DI | IO30、IO10、RX |
| I2S_DO | IO3、11/NC、12/NC、IO14/NC、IO15/NC、IO27 |
| I2S_FS | IO1、IO13/NC、IO17、IO29、TX |
| I2S_RCLK_O | IO3、11/NC、12/NC、IO30、IO14/NC、IO15/NC、IO10、IO27、RX |
| PWM0 | IO3、11/NC、12/NC、IO1、IO30、IO0、IO13/NC、IO14/NC、IO15/NC、IO16、IO10、IO28、IO17、IO29、RX、IO20 |
| RXD | RX |
| SPI_MISO | IO30、IO10、RX |
| SPI_MOSI | IO3、11/NC、12/NC、IO14/NC、IO15/NC、IO27 |
| SPI_SCLK | IO1、IO13/NC、IO17、IO29、TX |
| SPI_SS | IO0、IO16、IO28、IO20 |
| TXD | TX |
| USB_DM | DM |
| USB_DP | DP |
| XTAL_32K_IN | IO16 |
| XTAL_32K_OUT | IO17 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12, 13）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
