"""WLAN Multi-Evaluation: EVM / TX power / freq error / IQ imbalance on DUT TX bursts.

Pre-req: DUT already associated to CMW-AP via AT+WLCONN; Sig1 STATe ON.
Workflow: PG1 floods CMW→DUT with ICMP; DUT replies create TX bursts at high MCS.
WLAN MEAS1 (CSP mode linked to WLAN Sig1) captures bursts via RXFrameTrigger and decodes.

KEY CONFIG (learned the hard way on FW 3.7.40 + WLAN Sig 3.7.32):
  - Sig1 EPEPower MUST be >= 30 dBm  (default 18 dBm causes RX-AGC saturation)
  - MEAS1 ENPower1 should match Sig1 EPEPower (e.g. +30 dBm)
  - PG1 MUST be ON (drives DUT to high MCS; without it, RXFrameTrigger never fires)
  - Trigger = "WLAN Sig1: RXFrameTrigger" (long-string form), CSP scenario
"""
import pyvisa, time, os, sys
for k in ('http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)

CMW = 'TCPIP0::192.0.2.10::5025::SOCKET'

rm = pyvisa.ResourceManager('@py')
inst = rm.open_resource(CMW)
inst.read_termination = '\n'; inst.write_termination = '\n'
inst.timeout = 30000
inst.write('*CLS')

def w(s): inst.write(s); time.sleep(0.15)
def q(s): return inst.query(s).strip()

print(f'IDN: {q("*IDN?")}')

# --- pre-flight ---
if q('SOURce:WLAN:SIGNaling1:STATe?') != 'ON':
    sys.exit('!! Sig1 not ON — start via wlan_bringup.py first')
dut_ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
if dut_ip in ('', '0.0.0.0', 'NAV'):
    sys.exit(f'!! DUT not associated (IP={dut_ip}). Run AT+WLCONN first.')
print(f'DUT IP: {dut_ip}')

# --- 1) Sig1 RX AGC headroom: EPEPower >= 30 dBm ---
w('CONFigure:WLAN:SIGNaling1:RFSettings:EPEPower 30')
print(f'EPEPower: {q("CONFigure:WLAN:SIGNaling1:RFSettings:EPEPower?")}')

# --- 2) PG1 ON: ICMP echo flood to DUT ---
w(f'CONFigure:WLAN:SIGNaling1:IPVFour:STATic:IPADdress:DESTination {dut_ip.replace(".",",")}')
w('CONFigure:WLAN:SIGNaling1:PGEN1:PROTocol ICMP')
w('CONFigure:WLAN:SIGNaling1:PGEN1:IPVersion IV4')
w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,10,1000,PRAN,TID0')
time.sleep(3)
print(f'PG1: {q("CONFigure:WLAN:SIGNaling1:PGEN1:CONFig?")}')
print(f'RXBP: {q("SENSe:WLAN:SIGNaling1:UESinfo:RXBPower?")} dBm  rate={q("SENSe:WLAN:SIGNaling1:UESinfo:DRATe?")}')

# --- 3) MEAS1 setup ---
w('ABORt:WLAN:MEAS1:MEValuation')
time.sleep(0.5)
w('ROUTe:WLAN:MEAS1:SCENario:CSPath "WLAN Sig1"')
w('CONFigure:WLAN:MEAS1:RFSettings:ENPower1 30')
w('CONFigure:WLAN:MEAS1:MEValuation:RESult:ALL ON,ON,ON,ON,ON,ON,ON,ON,ON')
w('CONFigure:WLAN:MEAS1:MEValuation:SCOunt:MODulation 40')
w('CONFigure:WLAN:MEAS1:MEValuation:SCOunt:PVTime 40')
w('CONFigure:WLAN:MEAS1:MEValuation:SCOunt:SPECtrum 40')
w('CONFigure:WLAN:MEAS1:MEValuation:SCOunt:TSMask 40')
w('CONFigure:WLAN:MEAS1:MEValuation:REPetition SING')
w('CONFigure:WLAN:MEAS1:MEValuation:TOUT 60')
w('TRIGger:WLAN:MEAS1:MEValuation:SOURce "WLAN Sig1: RXFrameTrigger"')
w('TRIGger:WLAN:MEAS1:MEValuation:TOUT 30')

# --- 4) INIT + wait ---
w('INITiate:WLAN:MEAS1:MEValuation')
print('\n--- Running Multi-Eval ---')
for i in range(120):
    time.sleep(0.5)
    sa = q('FETCh:WLAN:MEAS1:MEValuation:STATe:ALL?')
    if sa.startswith('RDY'):
        print(f'  RDY at t={i*0.5:.1f}s  ({sa})')
        break
    if i % 6 == 0: print(f'  t={i*0.5:4.1f}s  {sa}')

# --- 5) Results ---
mod = q('FETCh:WLAN:MEAS1:MEValuation:MODulation:OFDM:AVERage?').split(',')
print('\n=== Modulation (OFDM AVERage) ===')
if mod[0] == '0':
    field_names = ['reliab','rate','nbursts','TX_pwr_dBm','EVM_all_RMS_dB','EVM_all_peak_dB',
                   'EVM_data_dB','CF_err_Hz','IQ_imbal_dB','Phase_imbal_deg',
                   'Sym_clk_err_unit?','Sym_clk_err_ppm','field13','field14','N_symbols']
    for name, val in zip(field_names, mod):
        print(f'  {name:20s} = {val}')
else:
    print('  raw:', ','.join(mod))

print('\n=== PVTime / TSMask / SFLatness ===')
for label, cmd in [
    ('PVT REDGe', 'FETCh:WLAN:MEAS1:MEValuation:PVTime:REDGe:AVERage?'),
    ('PVT FEDGe', 'FETCh:WLAN:MEAS1:MEValuation:PVTime:FEDGe:AVERage?'),
    ('TSMask',    'FETCh:WLAN:MEAS1:MEValuation:TSMask:OFDM:AVERage?'),
    ('SFLatness', 'FETCh:WLAN:MEAS1:MEValuation:SFLatness:AVERage?'),
]:
    print(f'  {label:10s}: {q(cmd)[:160]}')

# Cleanup
w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,10,1000,PRAN,TID0')
print(f'\nfinal err: {q("SYST:ERR?")}')
inst.close()
