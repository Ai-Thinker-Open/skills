# LLCC68 SPI 命令参考(完整版)

> 来源:Semtech DS_LLCC68 V1.0 手册第 10~13 章。所有命令通过 SPI(CPOL=0, CPHA=0)发送,opcode 1 字节 + 参数 n 字节,NSS 上升沿结束事务。发送前必须等 BUSY 拉低。读命令需发 NOP(0x00)取数据。

## 命令总览

### 模式控制命令

| 命令 | Opcode | 参数 | 说明 |
|------|--------|------|------|
| SetSleep | 0x84 | sleepConfig | 进入 SLEEP。sleepConfig bit2=1 保留配置(warm start),bit0=1 使能 RTC 唤醒。进入后约 500μs 不可接收命令 |
| SetStandby | 0x80 | standbyConfig | 0=STDBY_RC(RC13M),1=STDBY_XOSC(32MHz 晶振) |
| SetFs | 0xC1 | - | 进入频率合成模式,PLL 锁定到 SetRfFrequency 设置频率 |
| SetTx | 0x83 | timeout[23:0] | 进入发射。0x000000=无超时单次;其他=超时模式(15.625μs/步,最大 262s) |
| SetRx | 0x82 | timeout[23:0] | 进入接收。0x000000=单次;0xFFFFFF=连续;其他=超时(15.625μs/步,≤262s)。检测到包后计时器自动停止 |
| StopTimerOnPreamble | 0x9F | stopOnPreambleParam | 0x00=同步字/头检测停计时(默认);0x01=前导码检测即停计时 |
| SetRxDutyCycle | 0x94 | rxPeriod[23:0], sleepPeriod[23:0] | 侦听模式(RX/SLEEP 交替),均为 15.625μs/步 |
| SetCad | 0xC5 | - | 执行 CAD 信道活动检测(LoRa 专用),结束后回 STDBY_RC |
| SetTxContinuousWave | 0xD1 | - | 测试:连续载波 |
| SetTxInfinitePreamble | 0xD2 | - | 测试:无限前导码(LoRa 前导符号 / FSK 0x55) |
| SetRegulatorMode | 0x96 | regModeParam | 0=仅 LDO(默认);1=DC-DC+LDO。须在 STDBY_RC 下设置 |
| Calibrate | 0x89 | calibParam | 按位校准:bit0=RC64k,bit1=RC13M,bit2=PLL,bit3=ADC脉冲,bit4=ADC bulk N,bit5=ADC bulk P,bit6=Image。全部校准约 3.5ms |
| CalibrateImage | 0x98 | freq1, freq2 | 频段镜像校准(见寄存器文档校准频段表) |
| SetPaConfig | 0x95 | paDutyCycle, hpMax, deviceSel, paLut | 功放配置。deviceSel 恒 0x00,paLut 恒 0x01。**paDutyCycle 不得高于 0x04** |
| SetRxTxFallbackMode | 0x93 | fallbackMode | 收发结束后进入模式:0x40=FS,0x30=STDBY_XOSC,0x20=STDBY_RC(默认) |

### 寄存器与缓冲访问

| 命令 | Opcode | 参数 | 说明 |
|------|--------|------|------|
| WriteRegister | 0x0D | address[15:0], data[0:n] | 写寄存器,地址自动递增 |
| ReadRegister | 0x1D | address[15:0] | 读寄存器。2 字节地址后需发 NOP 才开始返回数据 |
| WriteBuffer | 0x0E | offset, data[0:n] | 写数据缓冲(FIFO),地址超 255 回绕 |
| ReadBuffer | 0x1E | offset | 读数据缓冲。offset 后需发 NOP 取数据 |

### DIO 与 IRQ 控制

| 命令 | Opcode | 参数 | 说明 |
|------|--------|------|------|
| SetDioIrqParams | 0x08 | irqMask[15:0], dio1Mask[15:0], dio2Mask[15:0], dio3Mask[15:0] | IRQ 使能与 DIO 映射(每 DIO 可映射任意位,OR 逻辑) |
| GetIrqStatus | 0x12 | - | 返回 irqStatus[15:0](2 字节,NOP 读)。**大端返回:第 1 字节=IRQ[15:8](如 Timeout=bit9 在此字节 bit1),第 2 字节=IRQ[7:0](如 TxDone/RxDone/CrcErr)** |
| ClearIrqStatus | 0x02 | clearIrqParam[15:0] | 对应位置 1 清除 IRQ,参数同样大端(高字节在前) |
| SetDIO2AsRfSwitchCtrl | 0x9D | enable | 1=使能 DIO2 控制外部 RF 开关(TX 时高,其余模式低) |
| SetDIO3AsTcxoCtrl | 0x97 | tcxoVoltage, delay[23:0] | TCXO 模式。tcxoVoltage:0x00=1.6V,0x01=1.7V,0x02=1.8V,0x03=2.2V,0x04=2.4V,0x05=2.7V,0x06=3.0V,0x07=3.3V;delay 15.625μs/步。TCXO 模式下需冷启动复位才能回到 XTAL |

### RF/调制/包命令

| 命令 | Opcode | 参数 | 说明 |
|------|--------|------|------|
| SetRfFrequency | 0x86 | rfFreq[31:0] | 频率寄存器值 = FRF × 2^25 / 32MHz |
| SetPacketType | 0x8A | packetType | 0x00=GFSK,0x01=LoRa。**必须最先调用** |
| GetPacketType | 0x11 | - | 返回当前包类型 |
| SetTxParams | 0x8E | power, rampTime | power=-9(0xF7)~+22(0x16) dBm;rampTime:0x00=10μs,0x01=20μs,0x02=40μs,0x03=80μs,0x04=200μs,0x05=800μs,0x06=1700μs,0x07=3400μs |
| SetModulationParams | 0x8B | modParam1~8 | LoRa:4 字节(SF,BW,CR,LDRO);GFSK:8 字节(br[23:0],pulseShape,bw,fdev[23:0]) |
| SetPacketParams | 0x8C | packetParam1~9 | LoRa:6 字节;GFSK:9 字节(详见下文) |
| SetCadParams | 0x88 | cadSymbolNum, cadDetPeak, cadDetMin, cadExitMode, cadTimeout[23:0] | CAD 参数(LoRa)。cadSymbolNum:0=1符号,1=2,2=4,3=8,4=16;cadExitMode:0x00=CAD_ONLY,0x01=CAD_RX;cadTimeout 仅 CAD_RX 有效,15.625μs/步 |
| SetBufferBaseAddress | 0x8F | txBaseAddr, rxBaseAddr | TX/RX FIFO 基地址(0~255) |
| SetLoRaSymbNumTimeout | 0xA0 | symbNum | LoRa 锁定验证符号数,0=检测到符号即锁定(默认) |

### 状态命令

| 命令 | Opcode | 参数 | 说明 |
|------|--------|------|------|
| GetStatus | 0xC0 | - | 状态字节:bits[6:4]=模式(0x2=STBY_RC,0x3=STBY_XOSC,0x4=FS,0x5=RX,0x6=TX);bits[3:1]=命令状态 |
| GetRssiInst | 0x15 | - | 瞬时 RSSI,实际值 = -RssiInst/2 dBm |
| GetRxBufferStatus | 0x13 | - | 返回 payloadLengthRx, rxStartBufferPointer(2 字节) |
| GetPacketStatus | 0x14 | - | LoRa:rssiPkt, snrPkt(SNR = snrPkt/4 dB,补码), signalRssiPkt;FSK:rxStatus, rssiSync, rssiAvg |
| GetDeviceErrors | 0x17 | - | opError[15:0]:bit0=RC64K校准错,bit1=RC13M校准错,bit2=PLL校准错,bit3=ADC校准错,bit4=IMG校准错,bit5=XOSC启动错,bit6=PLL锁定错,bit8=PA斜坡错 |
| ClearDeviceErrors | 0x07 | 0x00, 0x00 | 清除全部错误(不可单独清除) |
| GetStats | 0x10 | - | LoRa:nbPktReceived, nbPktCrcError, nbPktHeaderErr;FSK:nbPktReceived, nbPktCrcError, nbPktLengthError |
| ResetStats | 0x00 | 0x00×6 | 复位统计 |

## 调制参数详解(SetModulationParams 0x8B)

### LoRa 模式(4 字节)

| 参数 | 取值 | 说明 |
|------|------|------|
| modParam1 - SF | 0x05~0x0B | SF5~SF11。SF5/SF6 建议前导码 12 符号。注意:SF6 与 SX1276 的 SF6 不兼容 |
| modParam2 - BW | 0x04=125kHz, 0x05=250kHz, 0x06=500kHz | 双边带。低于 400MHz 部分带宽不可用 |
| modParam3 - CR | 0x01=4/5, 0x02=4/6, 0x03=4/7, 0x04=4/8 | 编码率。4/5 综合最佳 |
| modParam4 - LDRO | 0x00=关, 0x01=开 | 符号时间 ≥16.38ms 时建议开启(如 SF11/BW125) |

### GFSK 模式(8 字节)

| 参数 | 公式/取值 | 说明 |
|------|-----------|------|
| modParam1~3 - br[23:0] | br = 32 × Fxtal / bitrate | 比特率 0.6~300kbps,默认 4.8kbps(0x34133) |
| modParam4 - pulseShape | 0x00=无滤波, 0x08=BT0.3, 0x09=BT0.5, 0x0A=BT0.7, 0x0B=BT1.0 | 高斯滤波 |
| modParam5 - BW | 0x1F=4.8kHz ~ 0x09=467kHz(21 档) | 接收带宽,**必须满足 BW ≥ BR + 2×Fdev + 频偏误差** |
| modParam6~8 - fdev[23:0] | fdev = FreqDev_Hz × 2^25 / Fxtal | 频偏 0.6~200kHz,最小调制指数 0.5 |

## 包参数详解(SetPacketParams 0x8C)

### LoRa 模式(6 字节)

| 参数 | 取值 | 说明 |
|------|------|------|
| packetParam1~2 - preambleLength[15:0] | 10~65535 | 前导码符号数,收发须一致,接收侧未知时设最大 |
| packetParam3 - headerType | 0x00=显式头(默认), 0x01=隐式头 | 隐式头需收发两侧手动一致配置 |
| packetParam4 - payloadLength | 0~255 | 发送:本包字节数;接收:可接受最大长度 |
| packetParam5 - crcType | 0x00=关, 0x01=开 | 16-bit 载荷 CRC |
| packetParam6 - invertIQ | 0x00=标准, 0x01=反向 | 反向 IQ 见 Known Limitations #4 |

### GFSK 模式(9 字节)

| 参数 | 取值 | 说明 |
|------|------|------|
| packetParam1~2 - preambleLength[15:0] | 8~65535 bit | 建议最小 16bit |
| packetParam3 - preambleDetectorLength | 0x00=关, 0x04=8bit, 0x05=16bit, 0x06=24bit, 0x07=32bit | 建议 8/16bit,须小于同步字长 |
| packetParam4 - syncWordLength | 0x00~0x40 bit(0~8 字节) | 同步字写入寄存器 0x06C0~0x06C7 |
| packetParam5 - addrComp | 0x00=关, 0x01=节点地址, 0x02=节点+广播 | 地址过滤,节点地址寄存器 0x06CD,广播 0x06CE。启用后载荷上限 254 |
| packetParam6 - packetType | 0x00=定长, 0x01=变长 | 变长包首字节为长度 |
| packetParam7 - payloadLength | 0~255 | 载荷长度 |
| packetParam8 - crcType | 0x01=关, 0x00=1字节, 0x02=2字节, 0x04=1字节反相, 0x06=2字节反相 | 多项式/初值可编程(0x06BC~0x06BF) |
| packetParam9 - whitening | 0x00=关, 0x01=开 | 白化,初值寄存器 0x06B8/0x06B9 |

## SPI 时序要点

- NSS 下降沿到首个 SCK:≥32ns;SCK 周期 ≥62.5ns(≤16MHz);NSS 高电平 ≥125ns
- 从 SLEEP 苏醒(NSS 下降沿)到 STBY_RC:冷启动 3.5ms / 热启动 340μs(BUSY 拉低后才行)
- 模式切换典型耗时:STBY_RC→TX 126μs,STBY_RC→RX 83μs,STBY_RC→FS 50μs
- 写命令:opcode+参数一次事务发完,NSS 中途不可拉高
