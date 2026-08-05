---
name: cmw-wlan-test
description: Run WLAN signaling-based TX power / EVM / RX-sensitivity measurements on the R&S CMW-500 + Realtek AmebaDplus DUT bench. Pure-SCPI workflow covers 802.11a/b/g/n on both 2.4 GHz (ch 1-14, BSTD/GSTD/GNST modes) and 5 GHz (ch 36-165, ASTD/ANST). FW 3.7.40 limitations and workarounds documented inline. Uses the working scripts at /home/zxf/keysight-test.
argument-hint: tx|evm|rx|mcs|cck|bringup|compliance|all [--channel N] [--standard ASTD|BSTD|GSTD|ANST|GNST] [--rate Q6M54|Q1M12|MCS7|C11M] [--phase A|B]
allowed-tools: [Bash, Read, Edit, Write]
---

# CMW-500 WLAN signaling measurement SOP

Project memory already covers the bench. Read `[[cmw500-wlan-signaling]]`, `[[dut-realtek-amebadplus]]`, `[[cmw500-pitfalls]]` before changing anything — every "obvious" SCPI path on this FW has at least one trap.

Before any bash call:
1. Strip proxy env: `env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY ...` or `os.environ.pop(...)` for those keys. WSL otherwise routes LAN traffic through Clash and gets timeouts.
2. Source `/home/zxf/keysight-test/venv` for `pyvisa` + `pywinrm`.
3. Confirm: `ping 192.0.2.10` + TCP 5025/5985 reachable.

## PG1 frame rate (`DFRControl`) — IMPORTANT

PG1 packets are NOT sent at the rate set by `PER:FDEF`. PG1's PHY rate is controlled by **`CONFigure:WLAN:SIGNaling1:CONNection:DFRControl <ENAB|DIS>,<rate>`**. Default is `ENAB,BR12` (Basic Rate 12 Mbps).

When testing a specific modulation/rate, set DFRControl to match — otherwise PG1 keep-alive frames keep DUT in BR12 RX state, and only DUT-side TX rate (which is auto-adapted) is at the test rate.

DFRControl rate code acceptance depends on `CONNection:STANdard`:
- **NHT modes** (ASTD/BSTD/GSTD): `BR1/2/55/11/6/9/12/18/24/36/48/54`, `Q1M12/Q1M34/Q6M23/Q6M34`, `D1MB/D2MB/C55M/C11M`. MCS codes rejected.
- **HT/AC modes** (ANST/GNST/ACST): All of the above PLUS **`MCS1` .. `MCS7`** ✓. Detailed form via `:CONNection:DFDef ENAB,HTM,BW20,MCS<n>,LONG|SHORt`.

**HT on PG1 + PER — fully verified 2026-05-14**: DFRControl `ENAB,MCS<n>` + PER:FDEF `HTM,BW20,MCS<n>,LONG|SHORt` BOTH work fine in compatible STANdard×channel pairings (GNST ch1, ANST ch36). Tested MCS1/4/7 — all PER tests complete in ~2.2 s, no deadlock. The earlier "HT FDEF triggers deadlock" attribution was misdiagnosed — the real cause was ANST + ch1 channel mismatch (see below).

DUT (AmebaDplus) shows ~55% PER baseline on HT MCS regardless of MCS index — a DUT/test-frame artifact (not SCPI deadlock). Needs more investigation for compliance-grade HT PER. The configuration itself is stable.

**STANdard × Channel pairing rule** (the real source of "ANST deadlock"):
- 2.4 GHz channels (1-13): BSTD / GSTD / **GNST** only.
- 5 GHz channels (36-165): ASTD / **ANST** / **ACST** only.
- Wrong pairings (e.g. ANST + ch1) leave Sig1 in inconsistent state — `INITiate:WLAN:SIGNaling1:PER` then hangs the SCPI subtree for 3+ min, only clearable by CMW reboot. GUI dropdown enforces this; SCPI doesn't.

**Verified-clean PER:INITiate (PER 0% / 100 packets / ~17 s):**
| STANdard | Channel | Use case |
|---|---|---|
| ASTD | 165 | 5 GHz 802.11a |
| BSTD | 1 | 2.4 GHz CCK |
| GSTD | 1 | 2.4 GHz OFDM |
| GNST | 1 | 2.4 GHz a/g/n |
| ANST | 36 | 5 GHz a/n |
| ACST | 36 | 5 GHz a/n/ac |

**MCS testing**: use GNST (2.4 GHz) or ANST/ACST (5 GHz). DUT will negotiate up to its highest supported MCS under PG1 flood. PER:FDEF=`HTM,BW20,MCS<n>,LONG|SHORt` works in the correct pairing.

**Bandwidth on FW 3.7.40 (verified 2026-05-14)**:
- **BW20**: ✓ all modes (HT MCS1-7, VHT MCS3-8 single-stream).
- **BW40 / BW80 / BW160**: ❌ license-locked. SCPI returns `-203 Command protected; option missing` for `HTM,BW40,...` / `VHT,BW40|80|160,...` and `-221 Settings conflict` for `MEAS1:ISIGnal:BWIDth BW40|BW80`. Needs an additional KS option (likely KS850-class) not present on this bench.
- HT MCS0 (`HTM,BW20,MCS0,LONG`) rejected `-141` — use NHT `Q1M12` for 6 Mbps equivalent. MCS8-15 → `-221 Settings conflict` (DUT is 1×1).
- VHT MCS9 BW20 → conflict (legitimate spec restriction); MCS0-2 also rejected (`-141`).

**Reboot persistence**: `CH` and `PER:FDEF` survive a reboot. `STANdard` and `DFRControl`/`DFDef` reset to defaults (`GSTD` and `BR12`). Always re-set these after a reboot or when entering a new session.

Recommended: every rate-specific test sets `DFRControl ENAB,<matching_rate>` before INIT, so DUT stays in that PHY rate continuously:

```python
inst.write('CONFigure:WLAN:SIGNaling1:CONNection:DFRControl ENAB,Q6M34')  # 54 Mbps
inst.write('CONFigure:WLAN:SIGNaling1:PER:FDEF NHT,BW20,Q6M34,LONG')      # match
inst.write('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,10,1000,PRAN,TID0') # PG1 ON
```

`DFDef` (Default Frame Definition, query `CONNection:DFDef?`) returns the expanded form `ENAB,NHT,BW20,BR12,LONG` — same info, more verbose.

## STANdard / Channel / Standard-switch workflow

`CONFigure:WLAN:SIGNaling1:CONNection:STANdard` accepts these enums on FW 3.7.40 (verified — many "obvious" forms like `HSTD`, `ANSTD`, `BGN` are rejected; below are the ones that actually take):

| Enum | GUI label | Band | DUT mode |
|---|---|---|---|
| `ASTD` | IEEE 802.11a | 5 GHz | NHT OFDM only |
| `BSTD` | IEEE 802.11b | 2.4 GHz | DSSS/CCK only |
| `GSTD` | IEEE 802.11g | 2.4 GHz | NHT OFDM only |
| `ANST` | IEEE 802.11a/n | 5 GHz | NHT + HT MCS |
| `GNST` | IEEE 802.11g/n | 2.4 GHz | NHT + HT MCS |
| `ACST` | IEEE 802.11ac | 5 GHz | NHT + HT + VHT (untested) |

Switching STANdard requires `SOURce:WLAN:SIGNaling1:STATe OFF` first, then write new STANdard + channel, then `STATe ON` (poll ~15 s PEND→ON). DUT will drop association — re-issue `AT+WLCONN=ssid,CMW-AP,ch,<n>` after.

`OMCSconf` query returns `NOTS,NOTS,...` regardless of STANdard — that field appears read-only on this FW; the actual HT-enable is the STANdard switch itself.

## Critical FW 3.7.40 limits (read first!)

This firmware (`CMW_WLAN_Sig/Meas V3.7.32` on `Base V3.7.40`) is *older* than what most R&S example scripts assume. Vendor support docs and newer-FW SCPI paths often **do not exist** here. Verified by grepping the full `SYSTem:HELP:HEADers?` dump (855 KB definite-length block, see [[cmw500-wlan-signaling]] for how to fetch via raw TCP).

| Newer-FW path | Our FW 3.7.40 | Notes |
|---|---|---|
| `SYSTem:SELect 'WLAN Meas'` | `-113 Undefined header` | App auto-loads via `SOURce:WLAN:SIGNaling1:STATe ON` (~15 s PEND→ON) |
| `INSTrument:ACTivate "WLAN Meas1"` | `-200 Execution error` | UI-layer activation blocked; SCPI works without it |
| `CONFigure:WLAN:MEAS1:MEValuation:FREQuency` | `-113` | Use `:RFSettings:FREQuency` instead |
| `CONFigure:WLAN:MEAS1:MEValuation:EXPected:POWer` | `-113` | Use `:RFSettings:ENPower1` instead |
| `CONFigure:WLAN:MEAS1:MEValuation:TRIGger:SOURce FREE` | `-113` (CONFigure form) | Use `TRIGger:WLAN:MEAS1:MEValuation:SOURce "Free Run"` |
| `:MODulation:LOFDm:AVERage?` | `-113` | Use `:MODulation:OFDM:AVERage?` for all 802.11a |
| `:PVTime:LOFDm:REDGe:AVERage?` | `-113` | Use `:PVTime:REDGe:AVERage?` (no standard suffix) |
| `:LIMit:TSMask:LOFDm:STATe` | `-113` | Use `:LIMit:TSMask:LOFDm:ENABle` |
| `RESult:MODulation ON` | `-113` | MOD is implicit via EVM/IQConst/MSCalar individual toggles |

**Multi-Eval result-type availability** (verified 4-way matrix Scenario × Sig1):

| Result | CSP+Sig1 ON | SAL+Sig1 ON | SAL+Sig1 OFF | Notes |
|---|---|---|---|---|
| MODulation (EVM/TX/CF) | ✅ | reliab 26 | reliab 6 (no signal) | **stick to CSP** |
| Spectral Flatness | ✅ | reliab 26 | reliab 6 | works in CSP |
| PVTime | toggle ON but NCAP | reliab 26 | reliab 6 | not capturable on this FW |
| TSMask | toggle silently OFF | toggle ON, reliab 26 | toggle ON, reliab 6 | only SAL accepts; needs DUT in chip-level continuous-TX mode (vendor MP test cmd, not yet probed) |
| SPECtrum | same as TSMask | same | same | same |

So **pure-SCPI Multi-Eval delivers**: EVM, TX power, CF error, IQ/phase imbalance, symbol clock error, Spectral Flatness. PVTime / TSMask / SPECtrum need FW upgrade or a vendor continuous-TX command on the DUT.

## Pre-flight bring-up (`bringup`)

`python /home/zxf/keysight-test/wlan_bringup.py` — turns Sig1 STATe ON, polls until ON (~15 s), confirms persisted config (SSID `CMW-AP`, ch 165, BOPower −30, EATT IN/OUT 1 dB, route RF2C/RX1/RF2C/TX1).

If config got wiped (e.g. *RST), re-set:

```python
inst.write("SOURce:WLAN:SIGNaling1:STATe OFF")
inst.write("ROUTe:WLAN:SIGNaling1:SCENario:SCELl RF2C,RX1,RF2C,TX1")   # note SCELl (Standard-Cell), NOT SALone
inst.write("CONFigure:WLAN:SIGNaling1:CONNection:OMODe AP")
inst.write("CONFigure:WLAN:SIGNaling1:CONNection:STANdard ASTD")
inst.write("CONFigure:WLAN:SIGNaling1:CONNection:SSID 'CMW-AP'")
inst.write("CONFigure:WLAN:SIGNaling1:CONNection:SECurity:TYPE DIS")
inst.write("CONFigure:WLAN:SIGNaling1:RFSettings:CHANnel 165")
inst.write("CONFigure:WLAN:SIGNaling1:RFSettings:BOPower -30")
inst.write("CONFigure:WLAN:SIGNaling1:RFSettings:EPEPower 30")          # ≥30, default 18 saturates AGC
inst.write("CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:OUTPut 1")
inst.write("CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:INPut 1")  # default 35.1, wrong for direct cable
inst.write("SOURce:WLAN:SIGNaling1:STATe ON")                            # then poll STATe? for ~15s
```

Then connect DUT (serial on CMW's CH340 / COM28 @ 115200, **not** the FT232 COM57 used for BT):

```
AT+WLDISCONN
AT+WLCONN=ssid,CMW-AP,ch,165
```

Verify via `SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?` — should return a non-empty IP like `"192.168.48.129"`. RXBPower should read ~+9 dBm. `EAPStat = IDLE,IDEN` is normal for OPEN security.

If DUT auth fails (`+WLCONN:ERROR:4 / Fail:-13`) → check EATT (must be ~1 dB not 35), TX BOPower (need ≥ −50 dBm at DUT, the link budget is tight at 5 GHz UNII-3).

## TX power test (`tx`)

`python /home/zxf/keysight-test/wlan_tx_power.py` — fastest path. Loops `SENSe:WLAN:SIGNaling1:UESinfo:RXBPower?` while PG1 floods. No Multi-Eval needed for just TX power; the GUI's "Burst Power" widget reads the same number.

Result format: instantaneous burst power in dBm (5 Hz polling, averaged in script). Typical AmebaDplus result: **+9 to +10 dBm avg**.

Notes:
- `SENSe:UESinfo:ARXBpower?` (rolling avg) is *not* updated to match `RXBPower?` (instant); rely on instant samples for true mean.
- Add ~1 dB for the cable when reporting DUT actual TX (EATT already compensates internally for the configured 1 dB).

## EVM / modulation / spectral flatness (`evm`)

`python /home/zxf/keysight-test/wlan_multi_eval.py` runs the proven sequence:

```python
# critical: EPEPower 30 + ENPower1 30 + PG1 ON + CSP + RXFrameTrigger
inst.write('CONFigure:WLAN:SIGNaling1:RFSettings:EPEPower 30')
inst.write('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,10,1000,PRAN,TID0')
inst.write('ROUTe:WLAN:MEAS1:SCENario:CSPath "WLAN Sig1"')                    # quoted!
inst.write('CONFigure:WLAN:MEAS1:RFSettings:ENPower1 30')
inst.write('TRIGger:WLAN:MEAS1:MEValuation:SOURce "WLAN Sig1: RXFrameTrigger"')
inst.write('INITiate:WLAN:MEAS1:MEValuation')
# poll FETCh:WLAN:MEAS1:MEValuation:STATe? until "RDY" (~1 s)
```

Fetch result format for `FETCh:WLAN:MEAS1:MEValuation:MODulation:OFDM:AVERage?` (15 fields):

```
0,    Q6M54,  40,  +12.58, -34.92, -34.84, -36.04, 16261 Hz, 3.29, -37.60, 0.011, 0.158, 0, NCAP, 100
^     ^       ^    ^       ^        ^        ^       ^         ^     ^       ^       ^     ^  ^     ^
relia rate    Nb   TXpwr   EVMrms  EVMpeak  EVMdata CFerr     IQimb Phimb   ?       Sclk  ?  ?     Nsym
                   dBm     dB      dB       dB      Hz        dB    deg              ppm
```

Reliability code reference:
- 0 = OK
- 3 = trigger timeout / no captures
- 6 = no signal (DUT not transmitting or wrong freq/BW)
- 8 = Input Overdriven (ADC saturated — bump ENPower1)
- 26 = resource conflict (SAL trying to share RF2C with Sig1)

Spectral Flatness: `FETCh:WLAN:MEAS1:MEValuation:SFLatness:AVERage?` returns `reliab, dev1, dev2, dev3, dev4, dev5` — 5 subcarrier-deviation values in dB. 802.11a spec: ±2 dB inner, ±4 dB outer carriers.

**PVTime / TSMask / SPECtrum**: don't bother on this FW — see limits table above. If user insists, attempting in SAL mode with `SOURce:WLAN:SIGNaling1:STATe OFF` first will let toggles take but the DUT immediately stops TX (lost AP beacon) → reliab=6. The chip-level continuous-TX command for AmebaDplus has not been confirmed working on this DUT yet.

## RX sensitivity sweep (`rx`)

Three variants in `/home/zxf/keysight-test/`:

- `wlan_rx_sensitivity.py` — 5 dB coarse sweep, finds cliff range
- `wlan_rx_fine.py` — 1 dB sweep `−77 … −90`
- `wlan_rx_keepalive.py` — keeps PG1 on at 50 TU during the sweep, drops baseline PER from ~20% to ~9% (more reliable threshold)

PER test SCPI essentials:

```python
inst.write("CONFigure:WLAN:SIGNaling1:PER:PACKets 200")
inst.write("CONFigure:WLAN:SIGNaling1:PER:FDEF NHT,BW20,Q1M12,LONG")    # 6 Mbps BPSK 1/2
inst.write("CONFigure:WLAN:SIGNaling1:PER:LIMit 100")                   # don't stop early
inst.write("CONFigure:WLAN:SIGNaling1:RFSettings:BOPower <dBm>")        # sweep this
inst.write("INITiate:WLAN:SIGNaling1:PER")
# poll FETCh:...:PER:STATe? until "RDY" (~12 s for 200 packets)
# FETCh:WLAN:SIGNaling1:PER? → <reliab>,<PER_pct>,<sent>,<missing>,<duration_s>
```

PER FDEF rate codes depend on `CONNection:STANdard`:
- **NHT-OFDM** (ASTD/GSTD): `NHT,BW20,Q1M12|Q1M34|Q6M23|Q6M34,LONG` = 6/9/48/54 Mbps. Intermediate QPSK/16QAM not exposed (-141).
- **DSSS/CCK** (BSTD): `NHT,BW20,D1MB|D2MB|C55M|C11M,LONG` = 1/2/5.5/11 Mbps 11b.
- **HT-MIXED** (ANST/GNST): `HTM,BW20,MCS<n>,LONG|SHORt` with **n=1..7** (MCS0 / MCS8-15 / BW40 all rejected on this FW — 1-stream 20 MHz HT only).
- **VHT** (ACST): not yet probed — likely `VHT,BW20,MCS<n>,...` style.

For sensitivity testing at maximum range use Q1M12 (6 Mbps BPSK 1/2) — most robust. For higher-rate margin check use Q6M34 (54 Mbps 64QAM) — drops to ~−75 dBm cliff.

**Typical sensitivity (AmebaDplus on this bench)**:
- 6 Mbps BPSK 1/2 @ 5 GHz: **−87.5 dBm** 50% PER (−82 dBm spec, +5.5 dB margin)
- 54 Mbps 64QAM 5/6 @ 2.4 GHz: **−75 dBm** 50% PER (−65 dBm spec, +10 dB margin)

## CCK / 802.11b mode (`cck`)

Use `wlan_ch1_multirate.py` which auto-switches STANdard → BSTD ch 1 and runs all 4 CCK rates. Quirks specific to DSSS:

- DUT auto-rates to CCK11 (11 Mbps) regardless of CMW PER:FDEF setting — the FDEF only controls what *CMW* sends, the DUT picks its own TX rate.
- `SENSe:UESinfo:DRATe?` returns `NHT,INV,BW20,NSS1` (rate field INV) because CCK doesn't map to NHT MBxx codes.
- Multi-Eval fetch uses `MODulation:DSSS:AVERage?` (NOT OFDM); field positions shift due to extra "format" (`LONG`/`SHORt`) field at index 2:
  ```
  0, CCK11, LONG, 558, +14.48, +16.84, 7.44, 8890 Hz, 2.87, -30.36, ...
  ^  ^      ^     ^    ^       ^       ^     ^         ^     ^
  reli rate fmt   Nb   TX      Peak    EVM   CFerr     IQimb Phimb
                      dBm      dBm     dB    Hz                deg
  ```
  Note: DSSS EVM uses **positive dB** convention (bigger = worse).

## HT/MCS / 802.11n mode (`mcs`)

Use `wlan_mcs_test.py` after switching STANdard to **ANST** (5 GHz a/n) or **GNST** (2.4 GHz g/n). MCS0/MCS8-15/BW40 not supported on this FW — only MCS1-7 at BW20 1-stream.

```python
inst.write("SOURce:WLAN:SIGNaling1:STATe OFF")            # standard switch requires OFF
inst.write("CONFigure:WLAN:SIGNaling1:CONNection:STANdard ANST")  # or GNST for 2.4 GHz
inst.write("SOURce:WLAN:SIGNaling1:STATe ON")             # wait PEND→ON
# DUT must reassociate after this
# Then PER FDEF goes:
inst.write("CONFigure:WLAN:SIGNaling1:PER:FDEF HTM,BW20,MCS7,SHORt")
```

DUT (AmebaDplus) auto-negotiates to HT MCS7 SHORt-GI under PG1 flood; `SENSe:UESinfo:DRATe?` returns `HT,MCS7,BW20,NSS1`. Multi-Eval fetch is still **`MODulation:OFDM:AVERage?`** — the `HTOFdm` path doesn't exist on this FW. Returned rate code field shows `Q6R56` (64QAM 5/6) for MCS7 SGI vs `Q6M34` for NHT 54 Mbps LGI.

Typical AmebaDplus result @ MCS7 2.4 GHz: TX +15.56 dBm, EVM RMS −35 dB, CF Error 3.5 kHz, 0% PER at MCS1-6 / 1% PER at MCS7 (BOPower −30 dBm).

## All-in-one (`all`)

Run the full chain: bringup → DUT reconnect → TX power → EVM → RX sensitivity. The user should keep CMW GUI in normal mode (any app open, even BT) — Sig1 SCPI works without it being on screen.

## Common failure modes and recovery

- **DUT auth fails (-13 / ERROR:4)**: EATT defaults are wrong. Set `:EATTenuation:OUTPut 1` and `:INPut 1` for direct cable. Default `INPut 35.11 dB` makes CMW expect a +35 dB stronger DUT than reality, AGC backs off, DUT receives only −76 dBm, auth times out.
- **Multi-Eval immediate RDY + reliab 8 ("Input Overdriven" on GUI)**: ENPower1 too low. Bump to 30 dBm (matches Sig1 EPEPower). UMARgin1 default 12 dB adds PAPR headroom.
- **Multi-Eval RDY in 0.5s + reliab 3 (Measurement Timeout on GUI)**: trigger source wrong (e.g. pointing to `WLAN Sig2: RXFrameTrigger` from a prior session). Explicitly write `"WLAN Sig1: RXFrameTrigger"` — trigger source persists across reboots.
- **`Reliability 26`**: SAL scenario fighting Sig1 for RF2C. Switch back to CSP linked to Sig1.
- **SCPI deadlock (everything TMOs after a `-113`)**: wait 30-60 s, don't `*RST`. CMW recovers. See [[cmw500-pitfalls]].
- **PG1 won't generate traffic**: destination IP must be in comma-separated bytes format: `192,168,48,129` NOT `"192.168.48.129"`. Use `dut_ip.replace('.', ',')`. Strings get `-104 Data type error`.
- **DUT keeps disassociating mid-test**: changing BOPower / EPEPower while Sig1 is ON triggers signaling restart → DUT drops. Configure RF settings *before* Sig1 STATe ON, or accept the brief dropout and re-issue `AT+WLCONN`.
- **CMW unreachable (ping fails)**: WinRM in via 192.0.2.10:5985, check Win7 OS state. Possibly `shutdown /r /t 0 /f` if hung. SCPI typically back ~4 min after reboot, see `cmw_reboot.py` in `/tmp/`.

## Key bench facts

- CMW SCPI: `TCPIP0::192.0.2.10::5025::SOCKET` (raw socket, pyvisa-py works)
- CMW WinRM: `<CMW_WINRM_USER>` / `<CMW_WINRM_PASS>`, ntlm, port 5985 (Win7 inside)
- DUT serial: `COM28` (CH340 on CMW) @ `115200 8N1`. **NOT** the FT232 `COM57` used for BT — that may not be plugged in.
- DUT: Realtek AmebaDplus (RTL8721Dx+), MAC `AA:BB:CC:DD:EE:FF`, AT-CLI shell.
- RF: direct coax CMW RF2 COM → DUT antenna port, ~1 dB loss.
- CMW AP DHCP subnet: 192.168.48.0/24, gateway .100, DUT typically gets .129.

## Measured AmebaDplus reference numbers (sanity-check against your run)

Direct coax CMW RF2 COM ↔ DUT antenna, EATT IN/OUT 1 dB, BOPower −30 dBm, EPEPower 30 dBm:

| Test | STANdard | CH | Result |
|---|---|---|---|
| TX power 54 Mbps OFDM | GSTD | 1 | +15.95 dBm |
| EVM RMS 54 Mbps | GSTD | 1 | −36.49 dB |
| CF Error 54 Mbps | GSTD | 1 | +48.9 Hz (0.02 ppm) |
| RX sensitivity 54 Mbps (50% PER) | GSTD | 1 | −75 dBm (spec −65) |
| TX power 11 Mbps CCK | BSTD | 1 | +14.43 dBm |
| DSSS EVM 11 Mbps | BSTD | 1 | 7.9 dB |
| TX power MCS7 HT | GNST | 1 | +15.56 dBm |
| EVM MCS7 64QAM 5/6 SGI | GNST | 1 | −35.17 dB |
| CF Error MCS7 | GNST | 1 | 3.48 kHz |
| TX power 54 Mbps OFDM | ASTD | 165 | +12.58 dBm |
| EVM RMS 54 Mbps | ASTD | 165 | −34.92 dB |
| CF Error 54 Mbps | ASTD | 165 | 16.3 kHz (2.8 ppm) |
| RX sensitivity 6 Mbps (50% PER) | ASTD | 165 | −87.5 dBm (spec −82) |

Pattern: this DUT's 2.4 GHz path is ~3 dB stronger TX, ~1.6 dB cleaner EVM, and **300× more accurate CF** than its 5 GHz path. PER cliffs follow normal modulation hierarchy (BPSK > QPSK > 16QAM > 64QAM in sensitivity ≈ 6 dB per step).

## Full compliance run (`compliance`)

`wlan_full_compliance.py` — automated TX + RX matrix across the full DUT capability set, with checkpoint/resume + auto-reboot recovery.

```bash
python wlan_full_compliance.py --phase A          # TX all + RX at 3 representative ch per band (~2 h)
python wlan_full_compliance.py --phase A --resume # pick up after crash/interrupt
python wlan_full_compliance.py --phase B --resume # full RX matrix (~10 h, overnight)
python generate_compliance_report.py              # CSV → WLAN_FULL_COMPLIANCE_REPORT.md
```

Test matrix (auto-iterates mode-outer / channel-inner):
- 2.4 GHz BSTD/GSTD/GNST × ch {1,3,6,9,11}
- 5 GHz ASTD/ANST × ch {36,40,52,64,100,132,149,165} — DFS channels skip gracefully as `SKIP_REGDOMAIN`
- HT MCS {1,4,7} forced via DFRControl + DFDef in GNST/ANST modes

Output CSVs (resumable):
- `wlan_full_compliance_tx.csv` — TX per (ch,mode[,mcs])
- `wlan_full_compliance_rx_coarse.csv` / `_rx_fine.csv` — PER raw points
- `wlan_full_compliance_rx_summary.csv` — 10% / 50% PER thresholds per cell
- `wlan_full_compliance_progress.csv` — checkpoint state (done/skip/fail/recovered)

## Reusable scripts under `/home/zxf/keysight-test/`

| Script | Function |
|---|---|
| `wlan_bringup.py` | SCPI-only Sig1 STATe ON + state verify |
| `wlan_tx_power.py` | PG1 ICMP flood + Sig1 SENSe sampling for TX power |
| `wlan_multi_eval.py` | Multi-Eval EVM/CF/IQ + Spectral Flatness (CSP mode) |
| `wlan_rx_sensitivity.py` | PER sweep at 5 dB step (ch165 6 Mbps) |
| `wlan_rx_fine.py` | PER sweep at 1 dB step around cliff |
| `wlan_rx_keepalive.py` | PER sweep w/ PG1 keep-alive — lowers baseline PER |
| `wlan_ch1_multirate.py` | All 8 rates on ch1 (4 CCK BSTD + 4 OFDM GSTD), CSV out |
| `wlan_ch1_ofdm54.py` | Focused 54 Mbps OFDM (GSTD ch1) full Multi-Eval + PER sweep |
| `wlan_mcs_test.py` | All 7 MCS rates in ANST mode + MEAS at MCS7 |
| `WLAN_TEST_REPORT.md` | Last full result snapshot |

## Final test report

`/home/zxf/keysight-test/WLAN_TEST_REPORT.md` — confirmed result snapshot. Update by re-running scripts and pasting new field values.
