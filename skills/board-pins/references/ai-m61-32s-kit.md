# Ai-M61-32S-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-M61-32S-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-M61-32S-Kit Specification V1.1.2 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/ai_m61/Specification/Ai-M61-32S-Kit_V1.1.2%20Specification-20240314.pdf) |

## 引脚定义表（42 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | 3V3 | 3.3V power supply; The output current of external power supply is recommended to be above 500mA. |
| 2 | EN | Default as chip enable, high level valid |
| 3 | IO0 | GPIO0/SPI_SS/I2S_BCLK/I2C_SCL/PWM0/ADC_CH9 |
| 4 | IO12 | GPIO12/SPI_SS/SDH_CLK/SF3_D0/I2S_BCLK/I2C_SCL/PWM0/ADC_C H6 |
| 5 | IO14 | GPIO14/SPI_MOSI/SPI_MISO/SDH_DAT3/SF3_D1/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0/ADC_CH4 |
| 6 | IO15 | GPIO15/SPI_MOSI/SDH_DAT2/SF3_CS/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 7 | IO1 | GPIO1/SPI_SCLK/I2S_FS/I2C_SCL/PWM0/ADC_CH8 |
| 8 | IO16 | Available by default, the IO port is shared with the PIN pin of the 32.768KHz crystal oscillator input inside the module. If the module of the internal patch 32.768KHz crystal oscillator is customized, the IO is in NC state. GPIO16/SPI_SS/I2S_BCLK/I2C_SCL/XTAL_32K_IN/PWM0 |
| 9 | IO17 | Available by default, the IO port is shared with the 32.768KHz crystal output PIN pin inside the module. If the module of the internal patch 32.768KHz crystal oscillator is customized, the IO is in NC state. GPIO17/SPI_SCLK/I2S_FS/I2C_SCL/XTAL_32K_OUT/PWM0 |
| 10 | IO18 | GPIO18/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 11 | IO19 | GPIO19/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0/ADC_CH1 |
| 12 | IO10 | GPIO10/SPI_MISO/SDH_DAT1/SF2_D3/I2S_DI/I2S_RCLK_O/I2C_SCL PWM0/ADC_CH7 |
| 13 | IO13 | GPIO13/SPI_SCLK/SDH_CMD/SF3_D2/I2S_FS/I2C_SCL/PWM0/ADC_CH5 |
| 14 | IO11 | GPIO11/SPI_MOSI/SDH_DAT0/SF3_CLK/I2S_DO/I2S_RCLK_O/I2C_S DA/PWM0 |
| 15 | IO3/NC | Default NC, not available. For use, please contact Ai-Thinker. GPIO3/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0/ADC_CH3 |
| 16 | IO20 | GPIO20/SPI_SS/I2S_BCLK/I2C_SCL/PWM0/ADC_CH0 |
| 17 | IO4/NC | Default NC, not available. The IO port is shared with the module Flash pin and cannot be used in the external FLASH state. |
| 18 | IO5/NC | Default NC, not available. The IO port is shared with the module Flash pin and cannot be used in the external FLASH state. |
| 19 | IO34/NC | Default NC, not available. For use, please contact Ai-Thinker. GPIO34/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 20 | 5V | 5V power supply; The output current of external power supply is recommended to be above 500mA. |
| 21 | GND | Grounding |
| 22 | GND | Grounding |
| 23 | IO33 | GPIO33/SPI_SCLK/I2S_FS/I2C_SCL/PWM0 |
| 24 | IO32 | GPIO32/SPI_SS/I2S_BCLK/I2C_SCL/PWM0 |
| 25 | TX | TXD/GPIO21/SPI_SCLK/I2S_FS/I2C_SCL/PWM0 |
| 26 | RX | RXD/GPIO22/SPI_MOSI/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 27 | IO31 | GPIO31/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 28 | IO30 | GPIO30/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 29 | IO25 | GPIO25/SPI_SCLK/I2S_FS/I2C_SCL/PWM0 |
| 30 | IO27 | GPIO27/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0/ADC_CH10 |
| 31 | IO29 | GPIO29/SPI_SCLK/I2S_FS/I2C_SCL/PWM0 |
| 32 | IO26 | GPIO26/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0 |
| 33 | IO28 | GPIO28/SPI_SS/I2S_BCLK/I2C_SCL/PWM0/ADC_CH11 |
| 34 | IO24 | GPIO24/SPI_SS/I2S_BCLK/I2C_SCL/PWM0 |
| 35 | IO2/NC | Default NC, not available. For use, please contact Anxin. GPIO2/SPI_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/PWM0/ADC_CH2 |
| 36 | IO23 | GPIO23/SPI_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/PWM0 |
| 37 | USB_DM | USB_DM |
| 38 | USB_DP | USB_DP |
| 39 | IO9/NC | Default NC, not available. The IO port is shared with the module Flash pin and cannot be used in the external FLASH state. |
| 40 | IO8/NC | Default NC, not available. The IO port is shared with the module Flash pin and cannot be used in the external FLASH state. |
| 41 | IO7/NC | Default NC, not available. The IO port is shared with the module Flash pin and cannot be used in the external FLASH state. |
| 42 | IO6/NC | Default NC, not available. The IO port is shared with the module Flash pin and cannot be used in the external FLASH state. |

## 功能索引

| ADC_CH0 | IO20 |
| ADC_CH1 | IO19 |
| ADC_CH10 | IO27 |
| ADC_CH11 | IO28 |
| ADC_CH2 | IO2/NC |
| ADC_CH3 | IO3/NC |
| ADC_CH4 | IO14 |
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
| GPIO18 | IO18 |
| GPIO19 | IO19 |
| GPIO2 | IO2/NC |
| GPIO20 | IO20 |
| GPIO21 | TX |
| GPIO22 | RX |
| GPIO23 | IO23 |
| GPIO24 | IO24 |
| GPIO25 | IO25 |
| GPIO26 | IO26 |
| GPIO27 | IO27 |
| GPIO28 | IO28 |
| GPIO29 | IO29 |
| GPIO3 | IO3/NC |
| GPIO30 | IO30 |
| GPIO31 | IO31 |
| GPIO32 | IO32 |
| GPIO33 | IO33 |
| GPIO34 | IO34/NC |
| I2C_S | IO11 |
| I2C_SCL | IO0、IO12、IO14、IO16、IO18、IO10、IO20、IO34/NC、IO32、RX、IO30、IO26、IO28、IO24、IO2/NC |
| I2C_SD | IO15 |
| I2C_SDA | IO1、IO17、IO19、IO13、IO3/NC、IO33、TX、IO31、IO25、IO27、IO29、IO23 |
| I2S_BCLK | IO0、IO12、IO16、IO20、IO32、IO28、IO24 |
| I2S_DI | IO14、IO18、IO10、IO34/NC、RX、IO30、IO26、IO2/NC |
| I2S_DO | IO15、IO19、IO11、IO3/NC、IO31、IO27、IO23 |
| I2S_FS | IO1、IO17、IO13、IO33、TX、IO25、IO29 |
| I2S_RCLK_ | IO14 |
| I2S_RCLK_O | IO15、IO18、IO19、IO10、IO11、IO3/NC、IO34/NC、RX、IO31、IO30、IO27、IO26、IO2/NC、IO23 |
| PWM0 | IO0、IO12、IO14、IO15、IO1、IO16、IO17、IO18、IO19、IO10、IO13、IO11、IO3/NC、IO20、IO34/NC、IO33、IO32、TX、IO31、IO30、IO25、IO27、IO29、IO26、IO28、IO24、IO2/NC、IO23 |
| RXD | RX |
| SDH_CLK | IO12 |
| SDH_CMD | IO13 |
| SDH_DAT0 | IO11 |
| SDH_DAT1 | IO10 |
| SDH_DAT2 | IO15 |
| SDH_DAT3 | IO14 |
| SF2_D3 | IO10 |
| SF3_CLK | IO11 |
| SF3_CS | IO15 |
| SF3_D0 | IO12 |
| SF3_D1 | IO14 |
| SF3_D2 | IO13 |
| SPI_MISO | IO14、IO18、IO10、IO34/NC、RX、IO30、IO26、IO2/NC |
| SPI_MOSI | IO14、IO15、IO19、IO11、IO3/NC、RX、IO31、IO27、IO23 |
| SPI_SCLK | IO1、IO17、IO13、IO33、TX、IO25、IO29 |
| SPI_SS | IO0、IO12、IO16、IO20、IO32、IO28、IO24 |
| TXD | TX |
| USB_DM | USB_DM |
| USB_DP | USB_DP |
| XTAL_32K_IN | IO16 |
| XTAL_32K_OUT | IO17 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12, 13）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
