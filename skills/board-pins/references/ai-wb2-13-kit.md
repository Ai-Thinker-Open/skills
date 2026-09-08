# Ai-WB2-13-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-WB2-13-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-WB2-13-Kit Specification V1.0.1 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/wb2/Specification/Ai-WB2-13-Kit_V1.0.1%20Specification-20220720.pdf) |

## 引脚定义表（29 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 2 | IO17 | GPIO17/SPI_MOSI/MISO/IIC_SDA/PWM_CH2 |
| 3 | IO3 | GPIO3/SPI_SCLK/IIC_SDA/PWM_CH3 |
| 4 | NC | Empty feet |
| 5 | IO4 | GPIO4/SPI_MOSI/MISO/IIC_SCL/PWM_CH4/ADC_CH4 |
| 6 | IO2/NC | It is not recommended and is shared with the internal Flash of the module. If you need to use it, please contact Ai-Thinker GPIO2/SPI_SS/IIC_SCL/PWM_CH2 |
| 7 | NC | Empty feet |
| 8 | NC | Empty feet |
| 9 | NC | Empty feet |
| 10 | GND | Ground |
| 11 | 3V3 | 3.3V power supply |
| 12 | EN/NC | By default, it is enabled as a chip. The high level is effective and cannot be used together with RST. |
| 13 | RST/NC | By default, it is suspended and can be customized as a reset pin. It is valid at a low level. If you need to use it, please contact Ai-Thinker |
| 14 | GND | Conductive earth |
| 15 | 5V | 5V power supply |
| 16 | 3V3 | 3.3V power supply |
| 17 | GND | Ground |
| 18 | TX | TXD/GPIO16/SPI_MOSI/MISO/IIC_SCL/PWM_CH1 |
| 19 | RX | RXD/GPIO7/SPI_SCLK/IIC_SDA/PWM_CH2 |
| 20 | NC | Empty feet |
| 21 | IO5 | GPIO5/SPI_MOSI/MISO/IIC_SDA/PWM_CH0/ADC_CH4 |
| 22 | IO1/NC | It is not recommended and is shared with the internal Flash of the module. If you need to use it, please contact Ai-Thinker GPIO1/SPI_MOSI/MISO/IIC_SDA/PWM_CH1 |
| 23 | NC | Empty feet |
| 24 | GND | Ground |
| 25 | 3V3 | 3.3V power supply |
| 26 | IO14 | GPIO14/SPI_SS/IIC_SCL/PWM_CH4/ADC_CH2 |
| 27 | IO8/NC | The default NC is unavailable |
| 28 | IO12 | GPIO12/SPI_MOSI/MISO/IIC_SCL/PWM_CH2/ADC_CH0 |
| 29 | IO11 | GPIO11/SPI_SCLK/IIC_SDA/ADC_CH10 |
| 30 | NC | Empty feet |

## 功能索引

| ADC_CH0 | IO12 |
| ADC_CH10 | IO11 |
| ADC_CH2 | IO14 |
| ADC_CH4 | IO4、IO5 |
| GPIO1 | IO1/NC |
| GPIO11 | IO11 |
| GPIO12 | IO12 |
| GPIO14 | IO14 |
| GPIO16 | TX |
| GPIO17 | IO17 |
| GPIO2 | IO2/NC |
| GPIO3 | IO3 |
| GPIO4 | IO4 |
| GPIO5 | IO5 |
| GPIO7 | RX |
| PWM | IO17、IO3、IO4、IO2/NC、TX、RX、IO5、IO1/NC、IO14、IO12 |
| RXD | RX |
| SPI_MOSI | IO17、IO4、TX、IO5、IO1/NC、IO12 |
| SPI_SCLK | IO3、RX、IO11 |
| SPI_SS | IO2/NC、IO14 |
| TXD | TX |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
