# BW60-12F-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | BW60-12F-Kit |
| 分类 | WiFi |
| 规格书版本 | NodeMCU-BW60-12F-Kit Specification V1.1.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/rtl87xx/bw60/Specification/BW60-12F-Kit_V1.1.0%20Specification-20260623.pdf) |

## 引脚定义表（21 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 8 | PB20/LOGTXD | PB20/UD_DIS; flashing port, LOG_TXD pin. Also used as a boot configuration pin; see the notes below. |
| 9 | PC3/NC | GPIO/RMII_TXD1/SPI1_MOSI/SD_D0; on the external Flash version, this IO is shared with internal Flash and not exposed |
| 10 | PC2/NC | GPIO/RMII_TXEN/SPI1_CLK/SD_D2; on the external Flash version, this IO is shared with internal Flash and not exposed |
| 11 | PC7/NC | GPIO/RMII_RXD0/SD_CLK; on the external Flash version, this IO is shared with internal Flash and not exposed |
| 12 | EN | Chip enable pin, active high |
| 13 | GND | Ground |
| 14 | 3V3 | 3.3V supply (VDD); external power supply output current recommended above 500mA |
| 15 | 5V | 5V supply (VBUS); external power supply output current recommended above 500mA |
| 16 | GND | Ground |
| 17 | PA26/TXD | GPIO/TSSI_1/RMII_REF_CLK/SD_D3 |
| 18 | PA25/RXD | GPIO/TSSI_0/RMII_RXERR |
| 19 | PA21 | GPIO/TOUCH8/SD_D3 |
| 20 | PA20 | GPIO/ADC0_TOUCH0/SD_D1 |
| 21 | PA19 | GPIO/ADC1_TOUCH1/TSSI_1/SPI0_CS/SWD_DAT/SD_CMD |
| 22 | PA18 | GPIO/ADC2_TOUCH2/TSSI_0/SPI0_MISO/SWD_CLK/SD_CLK |
| 23 | PC6/NC | SPIC(0/1)_FLASH_D0/RMII_RXD1/SD_CMD; on the external Flash version, this IO is shared with internal Flash and not exposed |
| 24 | PA5/DM | GPIO/HSDM/SPI0_MOSI/SWD_DAT/SD_D0 |
| 25 | PA4/DP | GPIO/HSDP/SPI0_CLK/SWD_CLK/SD_D2 |
| 26 | PC5/NC | SPIC(0/1)_FLASH_CLK/GPIO/RMII_CRS_DV/SPI1_CS/SD_D3; on the external Flash version, this IO is shared with internal Flash and not exposed |
| 27 | PC4/NC | GPIO/RMII_TXD0/SPI1_MISO/SD_D1; on the external Flash version, this IO is shared with internal Flash and not exposed |
| 28 | GND | Ground |

## 功能索引

| RXD | PC7/NC、PA25/RXD、PC6/NC |
| TXD | PB20/LOGTXD、PC3/NC、PA26/TXD、PC4/NC |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：17）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
