#!/usr/bin/env python3
"""Compare WCOUNTRY=0 vs WCOUNTRY=5 TX-power matrices -> Markdown document with delta tables."""
import csv, sys, os
WC0=os.environ.get("WC0_CSV","/home/zxf/keysight-test/wlan_tx_matrix_122_wc0.csv")
WC5=os.environ.get("WC5_CSV","/home/zxf/keysight-test/wlan_tx_matrix_122.csv")
OUT=os.environ.get("OUT_MD","/home/zxf/keysight-test/WLAN_TX_MATRIX_REPORT.md")
MODULE=os.environ.get("MODULE","Ai-Thinker aiio SDK Wi-Fi+BLE (AT+WJAP)")
TITLE=os.environ.get("TITLE","CMW-500 WLAN 发射功率测试报告 — 国家码 China (WCOUNTRY=5) 前后对比")
COLA=os.environ.get("COL_A","WCOUNTRY=0")
COLB=os.environ.get("COL_B","WCOUNTRY=5 (China)")
COND=os.environ.get("COND_ROW","对比 `AT+WCOUNTRY=0`(默认/world) vs `AT+WCOUNTRY=5`(China, 持久保存)")
DATE=sys.argv[1] if len(sys.argv)>1 else "2026-07-27"
RATES=["CCK11","OFDM54","MCS7"]
RLBL={"CCK11":"CCK 11 Mbps (11b)","OFDM54":"OFDM 54 Mbps (11g/a)","MCS7":"MCS-7 (11n HT)"}

def load(p):
    d={}; order=[]; band={}
    for r in csv.DictReader(open(p)):
        ch=int(r["channel"])
        if ch not in d: d[ch]={}; order.append(ch)
        band[ch]=r["band"]; d[ch][r["rate"]]=(r["tx_dbm"],r["status"])
    return d,order,band
d0,order,band=load(WC0)
d5,_,_=load(WC5)

def val(d,ch,rate):
    v=d.get(ch,{}).get(rate)
    if not v: return None,"—"
    tx,st=v
    if tx: return float(tx),tx
    return None,("N/A" if "N/A" in st else "FAIL")

L=[]
L.append("# %s"%TITLE)
L.append("")
L.append("| 项目 | 说明 |")
L.append("|---|---|")
L.append("| 测试仪 | R&S CMW-500 @ 192.0.2.10 (FW 3.7.40, WLAN Signaling) |")
L.append("| 被测模组 | %s, @ 921600 |"%MODULE)
L.append("| 条件 | %s |"%COND)
L.append("| 连接/射频 | WLAN Sig AP CMW-AP/WPA2, 直连同轴 RF2 COM, EATT IN/OUT 1 dB |")
L.append("| 测量 | Multi-Eval CSP, 按速率码过滤(CCK11/Q6M54/Q6R56), ≥3 burst 均值, reliab=0 |")
L.append("| 日期 | %s |"%DATE)
L.append("")
L.append("> 单位 dBm。Δ = [%s] − [%s]。"%(COLB,COLA))

for rate in RATES:
    L.append("")
    L.append("## %s"%RLBL[rate])
    L.append("")
    L.append("| 信道 | 频段 | %s | %s | Δ (dB) |"%(COLA,COLB))
    L.append("|:---:|:---:|:---:|:---:|:---:|")
    for ch in order:
        f0,s0=val(d0,ch,rate); f5,s5=val(d5,ch,rate)
        b="2.4 GHz" if band[ch]=="B24G" else "5 GHz"
        if f0 is None or f5 is None:
            delta="—"
        else:
            delta="%+.2f"%(f5-f0)
        L.append("| %d | %s | %s | %s | %s |"%(ch,b,
            ("+%s"%s0 if f0 is not None else s0),
            ("**+%s**"%s5 if f5 is not None else s5), delta))
L.append("")
L.append("## 说明")
L.append("")
L.append("- **CCK 11M 仅 2.4 GHz**；5 GHz(ch36/64/149/165) CCK 列为 N/A。")
for note in os.environ.get("NOTES","WCOUNTRY=5 (China) 已持久写入模组 flash，复位后仍生效；每次关联前 boot 自动加载。|Δ 为负表示中国法规域下模组按 EIRP 上限做了功率回退；Δ≈0 表示不受国家码约束。").split("|"):
    if note.strip(): L.append("- "+note.strip())
L.append("- 5 GHz 线损按 1 dB 补偿(实测≈1.97 dB)，5G 绝对值偏保守 ~1 dB；对比 Δ 不受影响(同通路)。")
open(OUT,"w").write("\n".join(L))
print("wrote",OUT)
print("\n".join(L))
