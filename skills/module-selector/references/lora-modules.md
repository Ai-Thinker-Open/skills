# LoRa/LoRaWAN 模组选型参考

数据来源: https://github.com/Ai-Thinker-Open/Ai-Thinker-Docs

## LoRa 系列

### 频段支持
- 410MHz~525MHz
- 803MHz~930MHz

### 型号列表

| 型号 | 频段 | 特点 |
|------|------|------|
| Ra-01 | 433MHz | SX1278, SPI接口 |
| Ra-01S | 433MHz | SX1278, SPI接口 |
| Ra-01S-P | 433MHz | SX1278, 大功率 |
| Ra-01SC | 433MHz | SX1278, 小尺寸 |
| Ra-01SCH-P | 433MHz | SX1278, 小尺寸大功率 |
| Ra-01H | 433MHz | SX1278, 大功率 |
| Ra-01SH | 868/915MHz | SX1276, 国际频段 |
| Ra-05U | 433MHz | SX1278, USB接口 |
| Ra-11 | 433MHz | LLCC68, 新一代芯片 |
| Ra-20 | 433MHz | LoRa模组 |

### LoRa-Kit 开发板
- LoRa 系列开发调试板

---

## LoRaWAN 系列

### 型号列表

| 型号 | 芯片 | 频段 | 通信距离 |
|------|------|------|----------|
| Ra-08 | ASR6601CB | 410~525MHz / 803~930MHz | 6.1km (吸盘天线) |
| Ra-09 | STM32WLE5CCU6 | 410~525MHz / 803~930MHz | 4.8km (吸盘天线) |

---

## LoRaWAN 网关系列

### 型号列表

| 型号 | 特点 |
|------|------|
| RG-02 | LoRaWAN 网关 |
| RG-03H | LoRaWAN 网关 |

---

## 选型建议

| 需求 | 推荐型号 |
|------|----------|
| 433MHz 点对点通信 | Ra-01 / Ra-01S |
| 大功率远距离 | Ra-01S-P / Ra-01H |
| 小尺寸设计 | Ra-01SC |
| 868/915MHz 国际频段 | Ra-01SH |
| 新一代芯片 | Ra-11 (LLCC68) |
| LoRaWAN 组网 | Ra-08 / Ra-09 |
| 网关应用 | RG-02 / RG-03H |
