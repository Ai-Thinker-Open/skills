# Ai-WB2-32S-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-WB2-32S-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-WB2-32S-Kit Specification V1.0.1 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/wb2/Specification/Ai-WB2-32S-Kit_V1.0.1%20Specification-20220720.pdf) |

## 引脚定义表（38 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | 3V3 | 3.3V power supply; The output current of the external power supply is recommended to be above 500mA |
| 2 | EN | By default, it is enabled as a chip, and the high level is effective |
| 3 | NC | Empty feet |
| 4 | IO11 | GPIO11/SPI_SCLK/IIC_SDA/ADC_CH10/JTAG_TDI/TDO |
| 5 | NC | Empty feet |
| 6 | Empty feet | Empty feet |
| 7 | IO14 | GPIO14/SPI_SS/IIC_SCL/PWM_CH4/ADC_CH2/JTAG_TCK/TMS |
| 8 | IO17 | GPIO17/SPI_MOSI/MISO/IIC_SDA/PWM_CH2/JTAG_TCK/TMS |
| 9 | IO3 | GPIO3/SPI_SCLK/IIC_SDA/PWM_CH3/JTAG_TDO/TDI |
| 10 | IO20/NC | The default NC is unavailable |
| 11 | IO22/NC | The default NC is unavailable |
| 12 | IO0/NC | The default NC is unavailable |
| 13 | IO21/NC | The default NC is unavailable |
| 14 | GND | Ground |
| 15 | NC | Empty feet |
| 16 | NC | Empty feet |
| 17 | NC | Empty feet |
| 18 | NC | Empty feet |
| 19 | 5V | 5V power supply; External power supply output current is recommended to be above 500mA |
| 20 | NC | Empty feet |
| 21 | NC | Empty feet |
| 22 | NC | Empty feet |
| 23 | NC | Empty feet |
| 24 | NC | Empty feet |
| 25 | IO8/NC | The default NC is unavailable. |
| 26 | NC | Empty feet |
| 27 | IO4 | GPIO4/SPI_MOSI/MISO/IIC_SCL/PWM_CH4/ADC_CH1 |
| 28 | IO2/NC | The default NC is unavailable |
| 29 | NC | Empty feet |
| 30 | IO1/NC | The default NC is unavailable |
| 31 | IO5 | GPIO5/SPI_MOSI/MISO/IIC_SDA/PWM_CH0/ADC_CH4/JTAG_T |
| 32 | NC | Empty feet |
| 33 | NC | Empty feet |
| 34 | RX | RXD/GPIO7/SPI_SCLK/IIC_SDA/PWM_CH2/JTAG_TDO/TDI |
| 35 | TX | TXD/GPIO16/SPI_MOSI/MISO/IIC_SCL/PWM_CH1/JTAG_TMS/T |
| 36 | IO12 | GPIO12/SPI_MOSI/MISO/IIC_SCL/PWM_CH2/ADC_CH0/JTAG_T |
| 37 | NC | Empty feet |
| 38 | GND | Ground |

## 功能索引

| ADC_CH0 | IO12 |
| ADC_CH1 | IO4 |
| ADC_CH10 | IO11 |
| ADC_CH2 | IO14 |
| ADC_CH4 | IO5 |
| GPIO11 | IO11 |
| GPIO12 | IO12 |
| GPIO14 | IO14 |
| GPIO16 | TX |
| GPIO17 | IO17 |
| GPIO3 | IO3 |
| GPIO4 | IO4 |
| GPIO5 | IO5 |
| GPIO7 | RX |
| PWM | IO14、IO17、IO3、IO4、IO5、RX、TX、IO12 |
| RXD | RX |
| SPI_MOSI | IO17、IO4、IO5、TX、IO12 |
| SPI_SCLK | IO11、IO3、RX |
| SPI_SS | IO14 |
| TXD | TX |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12, 13）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
