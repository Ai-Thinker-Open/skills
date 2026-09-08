# TG-12F-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | TG-12F-Kit |
| 分类 | WiFi |
| 规格书版本 | TG-12F-KIT Development Board Specification V1.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/tg/Specification/TG-12F-Kit%20Specification-20201126.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | NC | Empty Pin |
| 2 | IO0 | SDIO,SFLASH,SPI,I2C,UART,PWM,GPIO |
| 3 | IO11 | SPI,I2C,UART,PWM,AUXADC,GPIO |
| 4 | IO3 | SDIO,SPI,I2C,UART,PWM,GPIO |
| 5 | IO4 | SDIO,SPI,I2C,UART,PWM,GPIO |
| 6 | IO5 | SDIO,SPI,I2C,UART,PWM,GPIO |
| 7 | IO12 | SPI,I2C,UART,PWM,AUXADC,GPIO |
| 8 | IO14 | SPI,I2C,UART,PWM,AUXADC,GPIO |
| 9 | IO17 | SFLASH,SPI,I2C,UART,PWM,GPIO |
| 10 | GND | Ground Pin Function Definition Table 第7 页共11 页 |
| 11 | 3V3 | Power supply |
| 12 | EN | Chip enable |
| 13 | NC | Empty Pin |
| 14 | GND | Ground |
| 15 | 5V | Power supply |
| 16 | 3V3 | Power supply |
| 17 | GND | Ground |
| 18 | TX | SPI,I2C,UART,PWM,GPIO |
| 19 | RX | SPI,I2C,UART,PWM,AUXADC,GPIO |
| 20 | NC | Empty pin |
| 21 | NC | Empty pin |
| 22 | NC | Empty pin |
| 23 | NC | Empty pin |
| 24 | GND | Ground |
| 25 | 3V3 | Power supply |
| 26 | IO21 | GPIO4, ADC2_CH0, TOUCH0, RTC_GPIO10, HSPIHD, |
| 27 | IO22 | SFLASH,SPI,I2C,UART,PWM,GPIO |
| 28 | IO8 | SPI,I2C,UART,PWM,AUXADC,GPIO |
| 29 | IO1 | SDIO,SFLASH,SPI,I2C,UART,PWM,GPIO |
| 30 | IO2 | SDIO,SFLASH,SPI,I2C,UART,PWM,GPIO |

## 功能索引

| GPIO10 | IO21 |
| GPIO4 | IO21 |
| PWM | IO0、IO11、IO3、IO4、IO5、IO12、IO14、IO17、TX、RX、IO22、IO8、IO1、IO2 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：7, 8）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
