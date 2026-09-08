# NodeMCU-BU01-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | NodeMCU-BU01-Kit |
| 分类 | UWB |
| 规格书版本 | NodeMCU-BU01Specification V 1.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/UWB/uwb_1/Specification/BU01-Kit_V1.0%20Specification-20200520.pdf) |

## 引脚定义表（37 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 10 | universal I /O pin. |  |
| 4 | IO4 | universal I /O pin. |
| 5 | IRQ | The interrupt request output from the DWM1000 to the host processor and is connected to the MCU PB0. by default, the IRQ is a high-level efficient output, but can be configured as low-level valid if required. to run correctly in SLEEP and DEEPSLEEP mode, it should be configured to run efficiently at high levels. this pin will float in hibernation and DEEPSLEEP states and may cause a pseudo interrupt unless it is pulled low. This pin can be reconfigured as a generic I /O line GPIO8. when no IRQ function is used |
| 6 | CLK | SPI clock and connected to MCU PA5 |
| 7 | MISO | SPI data output and connected to MCU PA6 |
| 8 | MOSI | SPI data input and connected to MCU PA7 |
| 9 | CSN | SPI chip select and connect with MCU PA4. this is a low level effective enable input. SPICSn jumps from high to low indicate the beginning of a new SPI transaction. SPICSn can also be used as a wake-up signal to get DW1000 out of sleep or sleep state. |
| 11 | PB1 | PB1 on the MCU |
| 12 | PB10 | PB10 on the MCU |
| 13 | PB11 | PB11 on the MCU |
| 14 | LED1 | PA2, connection LED1 on the MCU |
| 15 | LED2 | PA1, connection LED2 on the MCU |
| 16 | BTN | PA0, connection BTN keys on the MCU |
| 17 | RESET | Reset pin on MCU, connect reset button |
| 18 | GND | Ground |
| 19 | GND | Ground |
| 20 | V3.3 | 3.3 V Power supply |
| 21 | V5 | 5V power supply |
| 22 | V3.3 | 3.3 V Power supply |
| 23 | GND | Ground grounding |
| 24 | VBAT | Vbat MCU battery power |
| 25 | SCL | SCL pin on MCU, default pull up 3.3 V, internal connect sensor SCL pin |
| 26 | SDA | SDA pin on MCU, default pull up 3.3 V, internal connect sensor SDA pin |
| 27 | PB8 | PB8 on the MCU |
| 28 | PB9 | PB9 on the MCU |
| 29 | PB5 | PB5 on the MCU |
| 30 | PB4 | PB4 on the MCU |
| 31 | PB3 | PB3 on the MCU |
| 32 | PA15 | PA15 on the MCU |
| 33 | V3.3 | 3.3 V Power supply |
| 34 | RST | Reset pin on BU01 and connected to MCU PB12 |
| 35 | WAKEUP | the wake-up pin on the BU01 and is connected to the PB13 of the MCU. when set to a valid high level state, the WAKEUP pin brings the DW1000 into working mode from a dormant or DEEPSLEEP state. If not used, the pin can be grounded |
| 36 | EXTON | The EXTON pin on the BU01 is connected to the MCU PB14 and the external device is enabled. position and remain active during wake-up until the device enters sleep mode. can be used to control external DC-DC converters or other circuits not required when the device is in sleep mode to minimize power consumption |
| 37 | U1RX | UART1-RX on the MCU |
| 38 | U1TX | UART1-TX on the MCU |
| 39 | PA8 | PA8 on the MCU |
| 40 | PB15 | PB15 on the MCU DIO Swdio SWDIO feet on MCU, default flash pin CLK Swclk SWDIO feet on MCU, default flash pin |

## 功能索引

| GPIO8 | IRQ |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：10, 11）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
