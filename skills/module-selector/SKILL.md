---
name: module-selector
description: 安信可模组选型助手。当用户需要选择物联网模组、传感器模块、无线通信模组时使用。支持 Wi-Fi、BLE、LoRa、雷达、UWB、星闪(NearLink)、NB-IoT 等全系列模组的选型推荐。根据用户需求（功耗、距离、协议、接口等）推荐合适的模组型号。
---

# 安信可模组选型助手

## 数据来源

模组信息来源于安信可官方文档源仓库 `vitpress_docs_resoure`（products 分类目录：wifi / lr / lorawan / radar / uwb / nearlink / bt / nb-iot / gps / voice_module 等），确保数据准确。各模块细分与规格书链接以官方源 index 为准。

## 输出格式要求

**选型推荐必须包含以下信息:**

1. **基本信息**: 型号、芯片、协议、封装
2. **关键参数**: IO数量、尺寸、天线类型、FLASH/PSRAM
3. **规格书链接**: 必须提供中文和英文规格书链接
4. **芯片资料**: 数据手册和参考手册链接
5. **开发资源**: SDK源码、开发板原理图（如有）

**示例输出格式:**

```
## 推荐型号: Ai-M62-12F

### 基本信息
- **芯片**: BL616
- **协议**: Wi-Fi 6 + BLE 5.3 + Thread
- **封装**: SMD-22
- **尺寸**: 24.0×16.0×3.1mm
- **天线**: PCB天线

### 规格书
- 中文: https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-12f_v1.0.1_product_specification_cn.pdf
- English: https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-12f_v1.0.1_specification-20240626.pdf

### 芯片资料
- 数据手册: [中文/EN]
- 参考手册: [中文/EN]

### 开发资源
- SDK: https://github.com/bouffalolab/bouffalo_sdk/tree/master
```

## 模组分类

### 1. Wi-Fi 系列（按协议代际细分）

**Wi-Fi 4 + BLE 双模（低成本经典）**
- **Ai-WB2** (BL602): Wi-Fi 4 + BLE 5.0, 高性价比、生态最成熟
- **Ai-WB3** (亮牛 LN882H): Wi-Fi 4 + BLE 5.1, 另一起 Wi-Fi+BLE 方案
- **Ai-WB1** (联盛德 W800): Wi-Fi 4 + BLE 4.2, 早期经典（新项目建议选 Ai-WB2）

**Wi-Fi 6 + BLE 双模（新一代）**
- **Ai-M61** (BL618): Wi-Fi 6 + BLE 5.3 + Thread, 音视频/摄像头首选
- **Ai-M62** (BL616): Wi-Fi 6 + BLE 5.3 + Thread, 均衡低功耗 120μA, 封装最全
- **Ai-M64** (BL616CL): Wi-Fi 6 + BLE 5.3, 超低功耗 90μA（电池供电首选）
  - 细分: M64P（Power）/ M64L（Low-power）

**双频 Wi-Fi（2.4G + 5.8G）**
- **BW16 / BW20** (RTL8720DN / RTL8711): 双频 Wi-Fi 4 + BLE, BW20 支持 CSI/Mesh
- **BW21** (RTL8735B): 双频 + BLE 5.1, 摄像头模组（ISP + H264/H265 + 神经网络）
- **BW60** (RTL8711F): **双频 Wi-Fi 6** + BLE 5.4, 超低功耗

**经典 / 平台专供**
- **ESP8266/ESP32**: 经典 Wi-Fi 4, 生态最成熟
- **TG系列**: 直连天猫精灵等生态平台

详见: [wifi-modules.md](references/wifi-modules.md)（含"快速选型总览"矩阵表）

### 2. LoRa/LoRaWAN 系列（按应用模式细分）

**点对点 LoRa**（SPI 从设备，外挂 MCU）
- **Ra-01 系列**: 410~525MHz 经典 / 大功率 / 小尺寸
- **Ra-01SH / Ra-01SCH**: 868/915MHz 国际频段
- **Ra-05 / Ra-05U**: 2.4GHz
- **Ra-11 / Ra-20**: 多频新一代（LR11xx/LR2021）

**LoRaWAN 组网**（自带 MCU 跑节点）
- **Ra-08** (ASR6601CB) / **Ra-09** (STM32WLE5)

**LoRaWAN 网关**（建网）
- **RG-02 / RG-03H**: LoRaWAN 网关

详见: [lora-modules.md](references/lora-modules.md)（含按芯片/频段细分）

### 3. 雷达系列（按频段/功能细分）
- **Rd-01**: 24GHz, WiFi+BLE+雷达三合一, 人体存在
- **Rd-03**: 24GHz 人体检测（V2 多版本：Rd-03D 轨迹 / Rd-03L 低功耗 / Rd-03E 测距手势 / Rd-03H 极窄）
- **Rd-04**: 10GHz, 微动检测
- **Rd-6X**: 60GHz（Rd-60/Rd-61）, 高精度/测距/手势
- **Rd-100**: 24GHz 感应（Rd-101A/103A, 矽典微, 6m）
- **Rd-Kit**: 调试板

详见: [radar-modules.md](references/radar-modules.md)

### 4. 其他系列（按技术细分）
- **UWB**: BU01/BU03/BU04, 高精度定位 10cm
- **NearLink 星闪**: Ai-BS21 / Ai-WS1
- **蓝牙**: PB 系列(奉加微) / TB 系列(泰凌微) / 蓝牙网关 ESP32-G
- **NB-IoT**: EC-01/EC-01G/EC-01F（EC616S）
- **GPS/BDS**: GP-01/GP-02
- **AI 语音**: VC-01/VC-02（云知声）
- **RF433**: Si4432

详见: [other-modules.md](references/other-modules.md)

## 选型流程

### 步骤 1: 确认需求

向用户询问:
1. **应用场景**: 智能家居/工业控制/穿戴设备/定位追踪?
2. **通信协议**: Wi-Fi/蓝牙/LoRa/蜂窝?
3. **关键指标**: 功耗/距离/速率/定位精度?
4. **接口需求**: UART/SPI/I2C/USB?
5. **封装要求**: 尺寸/天线类型?

### 步骤 2: 匹配推荐

| 需求关键词 | 推荐系列 | 参考文件 |
|-----------|----------|----------|
| WiFi、智能家居 | Ai-WB2 / Ai-M62 | wifi-modules.md |
| 音视频、摄像头 | Ai-M61 | wifi-modules.md |
| 低功耗、电池供电 | Ai-M64 / Ai-M62 | wifi-modules.md |
| 双频、5GHz | BW系列(CBW60为Wi-Fi6) | wifi-modules.md |
| 经典、生态最成熟 | ESP8266/ESP32 | wifi-modules.md |
| 直连生态平台(天猫精灵) | TG系列 | wifi-modules.md |
| 远距离、农村(点对点) | LoRa Ra-01 系列 | lora-modules.md |
| 组网、多节点 | LoRaWAN Ra-08/Ra-09 | lora-modules.md |
| 建 LoRaWAN 网络 | RG 网关 | lora-modules.md |
| 人体检测、雷达 | Rd-01 / Rd-03 | radar-modules.md |
| 精准测距/手势 | Rd-60/Rd-61 | radar-modules.md |
| 高精度定位 | UWB BU 系列 | other-modules.md |
| 星闪协议 | NearLink Ai-BS21 | other-modules.md |
| 蓝牙 BLE 家电 | PB/TB 系列 | other-modules.md |
| NB-IoT 物联 | EC 系列 | other-modules.md |
| 定位导航 | GP 系列 | other-modules.md |
| 离线语音控制 | VC 系列 | other-modules.md |

### 步骤 3: 提供详细信息

根据推荐结果，从参考文件中提取:
- 具体型号和封装
- 引脚数量和尺寸
- 供电要求
- 工作温度
- **规格书链接（必须提供）**

### 步骤 4: 提供开发评估

根据 [dev-guide.md](references/dev-guide.md) 提供:
- **开发难度评分**: ⭐~⭐⭐⭐⭐⭐
- **文档完善度**: 规格书、教程、FAQ
- **社区活跃度**: 问题响应速度
- **供货稳定性**: 是否现货、长期供货

### 步骤 5: 提供应用案例

推荐典型应用场景:
- 智能家居: 插座、开关、照明、门锁
- 工业控制: 传感器、监控、远程控制
- 消费电子: 穿戴设备、音频设备
- 新能源: 充电桩、光伏监控

### 步骤 6: 对比分析

当多个型号可选时，提供对比表:
- 性能差异
- 开发难度
- 供应链情况

## 参考文件

| 文件 | 内容 |
|------|------|
| [wifi-modules.md](references/wifi-modules.md) | WiFi 模组详细规格 + 规格书链接 |
| [lora-modules.md](references/lora-modules.md) | LoRa/LoRaWAN 模组 |
| [radar-modules.md](references/radar-modules.md) | 雷达模组 |
| [other-modules.md](references/other-modules.md) | UWB/NearLink/NB-IoT/蓝牙/GPS |
| [dev-guide.md](references/dev-guide.md) | 开发评估、FAQ、应用案例 |
