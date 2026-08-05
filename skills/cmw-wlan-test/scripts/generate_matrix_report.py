#!/usr/bin/env python3
"""Read wlan_tx_matrix_122.csv -> Markdown table document (channel x rate pivot)."""
import csv, sys, os
CSVP=os.environ.get("MATRIX_CSV","/home/zxf/keysight-test/wlan_tx_matrix_122.csv")
OUT=os.environ.get("OUT_MD","/home/zxf/keysight-test/WLAN_TX_MATRIX_REPORT.md")
MODULE=os.environ.get("MODULE","Ai-Thinker aiio SDK Wi-Fi+BLE (AT+WJAP), COM9/CH343 @ 921600")
TITLE=os.environ.get("TITLE","CMW-500 WLAN 发射功率测试报告 — 多信道 × 多速率")
DATE=sys.argv[1] if len(sys.argv)>1 else "2026-07-27"

rows=list(csv.DictReader(open(CSVP)))
RATES=["CCK11","OFDM54","MCS7"]
RLBL={"CCK11":"CCK 11M (11b)","OFDM54":"OFDM 54M (11g/a)","MCS7":"MCS-7 (11n HT)"}
# pivot[ch][rate] = (tx, status)
pivot={}; bands={}
order=[]
for r in rows:
    ch=int(r["channel"])
    if ch not in pivot: pivot[ch]={}; order.append(ch)
    bands[ch]=r["band"]
    pivot[ch][r["rate"]]=(r["tx_dbm"], r["status"])

def cell(ch,rate):
    v=pivot.get(ch,{}).get(rate)
    if not v: return "—"
    tx,st=v
    if tx: return "**%s**"%tx
    if "N/A" in st: return "N/A"
    return "FAIL"

L=[]
L.append("# %s"%TITLE)
L.append("")
L.append("| 项目 | 说明 |")
L.append("|---|---|")
L.append("| 测试仪 | R&S CMW-500 @ 192.0.2.10 (FW 3.7.40, WLAN Signaling) |")
L.append("| 被测模组 (DUT) | %s |"%MODULE)
L.append("| 连接方式 | WLAN 信令 AP (SSID CMW-AP, WPA2-PSK 12345678) |")
L.append("| 射频通路 | 直连同轴 CMW RF2 COM ↔ 模组天线口; EATT IN/OUT 各 1 dB (已补偿) |")
L.append("| 下行功率 / RX 期望 | BOPower −30 dBm (5GHz), 2.4GHz 钳到频段上限; EPEPower 30 dBm |")
L.append("| 速率强制 | SRATes DIS + DFRControl (C11M / Q6M34 / MCS7); 灌 PG1 逼模组自适应 |")
L.append("| 测量 | Multi-Eval CSP, 按捕获速率码过滤 (CCK11 / Q6M54 / Q6R56), 取 ≥3 个 burst 均值 |")
L.append("| 日期 | %s |"%DATE)
L.append("")
L.append("## 发射功率 (dBm)")
L.append("")
L.append("| 信道 | 频段 | CCK 11M | OFDM 54M | MCS-7 |")
L.append("|:---:|:---:|:---:|:---:|:---:|")
for ch in order:
    b="2.4 GHz" if bands[ch]=="B24G" else "5 GHz"
    L.append("| %d | %s | %s | %s | %s |"%(ch,b,cell(ch,"CCK11"),cell(ch,"OFDM54"),cell(ch,"MCS7")))
L.append("")
L.append("## 说明")
L.append("")
L.append("- **CCK 11M 仅 2.4 GHz**：802.11b 不存在于 5 GHz，故 ch36/64/149/165 的 CCK 列为 N/A。")
L.append("- **速率码**：CMW 捕获的调制码 `CCK11`=11b CCK, `Q6M54`=64QAM 3/4 (54M OFDM), `Q6R56`=64QAM 5/6 (MCS7 HT)。")
L.append("- **ch64 (DFS, UNII-2A) 关联并测量成功**，无需跳过。全部 17 个测量点 reliab=0。")
L.append("- **功率规律**：同信道 CCK11 > OFDM54 > MCS7（PAPR/回退递减，约 1~2 dB/档）；5 GHz 的 ch36/64 明显高于 ch149/165（约 5~6 dB），为模组各 UNII 子频段功率表差异（非仪表误差）。")
L.append("- **5 GHz 线损提示**：EATT 固定按 1 dB 补偿，而实测 5 GHz 同轴线损约 1.97 dB（见 E5071C 记录），故 5 GHz 各值约偏保守 ~1 dB（真实模组 TX 略高）；2.4 GHz 线损≈0.96 dB，补偿基本吻合。")
L.append("- 功率为突发功率均值 (reliab=0)，EATT 已补偿 ≈ 模组端口实际 TX。")
L.append("")
open(OUT,"w").write("\n".join(L))
print("wrote",OUT)
print("\n".join(L))
