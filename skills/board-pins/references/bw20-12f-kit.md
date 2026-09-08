# BW20-12F-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | BW20-12F-Kit |
| 分类 | WiFi |
| 规格书版本 | BW20-12F-KitSpecification V1.0.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/rtl87xx/bw20/Specification/BW20-12F-Kit_V1.0.0%20Specification-20240807.pdf) |

## 引脚定义表（28 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | GND | Connect to ground |
| 2 | PB17 | SPI1_CS/SD_D3 |
| 3 | PB18 | SPI1_CLK/SD_CMD |
| 4 | PB19 | SPI1_MOSI/SD_CLK |
| 5 | PB20 | SPI1_MISO/SWD_CLK/SD_D0 |
| 6 | PB21 | SPI1_CS/SWD_DAT/SD_D1 |
| 7 | LOG_RX | UART_LOG_RXD，RX pin for download firmware |
| 8 | LOG_TX | UART_LOG_TXD，EX pin for download firmware |
| 9 | PA8 | TIM8_TRIG |
| 10 | PA12 | SPI0_CS/SD_D2/TIM9_TRIG |
| 11 | EN | The chip enables pin and pull up effectively |
| 12 | GND | Connect to ground |
| 13 | 3V3 | For 3.3V power supply (VDD), the output current of external power supply is recommended to be above 500 mA |
| 14 | 5V | For 5V power supply (VBUS), the output current of the external power supply is recommended to be above 500 mA |
| 15 | GND | Connect to ground |
| 16 | PB31/TXD | UART1_TXD |
| 17 | PB30/RXD | UART1_RXD |
| 18 | PA31 | SPI 1 _ MISO / SWD _ DAT / SD_D1, the default function is SWD DATA, which can be configured as PA31 after IC boot |
| 19 | PA30 | SPI 1 _ MOSI / SWD _ CLK / SD_D0, the default function is SWD DATA, which can be configured as PA30 after IC boot |
| 20 | PA27 | SPI0_MOSI/SD_D3 |
| 21 | PA26 | SPI0_CLK/SD_D2 |
| 22 | DM | PA28/SPI0_MISO/SD_CMD/FSDM |
| 23 | DP | PA29/SPI1_CLK/SD_CLK/FSDP |
| 24 | PA16 | The default is not available and the IO is occupied by Flash inside the module. If you need to use it, please contact Ai-Thinker. SPI 0 _ MISO _ SD / CLK / external Flash |
| 25 | PA13 | The default is not available and the IO is occupied by Flash inside the module. If you need to use it, please contact Ai-Thinker. SD_D2 / External Flash |
| 26 | GND | Connect to ground |
| 27 | 3V3 | For 3.3V power supply (VDD), the output current of external power supply is recommended to be above 500 mA |
| 28 | 5V | For 5V power supply (VBUS), the output current of the external power supply is recommended to be above 500 mA |

## 功能索引

| RXD | LOG_RX、PB30/RXD |
| TXD | LOG_TX、PB31/TXD |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
