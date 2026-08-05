"""Focused test: 802.11g OFDM 54 Mbps on ch1 (2.412 GHz).
- Switch STANdard to GSTD
- DUT reassociates
- PG1 flood drives DUT to 54 Mbps
- Multi-Eval averages 40 bursts for EVM/IQ/CF
- PER sweep at 54 Mbps to find sensitivity cliff
"""
import pyvisa, time, os, sys, subprocess, csv
for k in ('http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)

rm = pyvisa.ResourceManager('@py')
inst = rm.open_resource('TCPIP0::192.0.2.10::5025::SOCKET')
inst.read_termination='\n'; inst.write_termination='\n'; inst.timeout=20000
inst.write('*CLS')
def w(s): inst.write(s); time.sleep(0.15)
def q(s): return inst.query(s).strip()

# 1) Switch to GSTD ch1
print('=== Switch STANdard to GSTD ===')
w('SOURce:WLAN:SIGNaling1:STATe OFF')
t0 = time.time()
while time.time() - t0 < 30:
    if q('SOURce:WLAN:SIGNaling1:STATe?') == 'OFF': break
    time.sleep(0.5)
w('CONFigure:WLAN:SIGNaling1:CONNection:STANdard GSTD')
w('CONFigure:WLAN:SIGNaling1:RFSettings:CHANnel 1')
w('CONFigure:WLAN:SIGNaling1:RFSettings:BOPower -30')
w('CONFigure:WLAN:SIGNaling1:RFSettings:EPEPower 30')
w('CONFigure:WLAN:SIGNaling1:CONNection:DFRControl ENAB,Q6M34')  # PG1 frames at 54 Mbps
w('SOURce:WLAN:SIGNaling1:STATe ON')
t0 = time.time()
while time.time() - t0 < 60:
    if q('SOURce:WLAN:SIGNaling1:STATe?') == 'ON': break
    time.sleep(2)
print(f'  Sig back ON in {time.time()-t0:.1f}s')

# 2) DUT reassociate
print('\n=== Reconnect DUT ===')
subprocess.run(['python','/tmp/winrm_run_ps_file.py','/tmp/dut_reconnect.ps1',
                'C:\\\\Users\\\\<CMW_WINRM_USER>\\\\Documents\\\\dut_reconnect.ps1'], capture_output=True)
time.sleep(6)
ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
print(f'  DUT IP: {ip}')
if ip in ('', '0.0.0.0', 'NAV'):
    print('  !! DUT not connected'); sys.exit(1)

# 3) PG1 flood
w(f'CONFigure:WLAN:SIGNaling1:IPVFour:STATic:IPADdress:DESTination {ip.replace(".",",")}')
w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,10,1000,PRAN,TID0')
time.sleep(3)
print(f'  RXBP    : {q("SENSe:WLAN:SIGNaling1:UESinfo:RXBPower?")} dBm')
print(f'  DRATe   : {q("SENSe:WLAN:SIGNaling1:UESinfo:DRATe?")}')

# 4) Multi-Eval @ 54 Mbps (40 bursts averaging)
print('\n=== Multi-Eval (40 bursts) ===')
w('ABORt:WLAN:MEAS1:MEValuation')
w('ROUTe:WLAN:MEAS1:SCENario:CSPath "WLAN Sig1"')
w('CONFigure:WLAN:MEAS1:RFSettings:FREQuency 2412000000')
w('CONFigure:WLAN:MEAS1:RFSettings:ENPower1 30')
w('CONFigure:WLAN:MEAS1:RFSettings:EATTenuation1 1')
w('CONFigure:WLAN:MEAS1:ISIGnal:STANdard LOFDm')
w('CONFigure:WLAN:MEAS1:ISIGnal:BWIDth BW20')
w('TRIGger:WLAN:MEAS1:MEValuation:SOURce "WLAN Sig1: RXFrameTrigger"')
w('TRIGger:WLAN:MEAS1:MEValuation:TOUT 30')
w('CONFigure:WLAN:MEAS1:MEValuation:RESult:EVM ON')
w('CONFigure:WLAN:MEAS1:MEValuation:RESult:SFLatness ON')
w('CONFigure:WLAN:MEAS1:MEValuation:SCOunt:MODulation 40')
w('CONFigure:WLAN:MEAS1:MEValuation:REPetition SING')
w('CONFigure:WLAN:MEAS1:MEValuation:TOUT 60')
w('INITiate:WLAN:MEAS1:MEValuation')
t0 = time.time()
while time.time() - t0 < 30:
    time.sleep(0.5)
    if q('FETCh:WLAN:MEAS1:MEValuation:STATe?') == 'RDY': break

mod = q('FETCh:WLAN:MEAS1:MEValuation:MODulation:OFDM:AVERage?').split(',')
labels = ['reliab','rate','Nbursts','TX_dBm','EVM_rms_dB','EVM_pk_dB','EVM_data_dB',
          'CF_err_Hz','IQ_imb_dB','Phase_imb_deg','field11','Sclk_ppm','field13','field14','Nsym']
for L, v in zip(labels, mod):
    print(f'  {L:18s} = {v}')

sfl = q('FETCh:WLAN:MEAS1:MEValuation:SFLatness:AVERage?')
print(f'\n  SFLatness AVER: {sfl}')

# 5) PER sweep for 54 Mbps RX sensitivity
print('\n=== PER sweep @ Q6M34 (54 Mbps) ===')
w('CONFigure:WLAN:SIGNaling1:PER:PACKets 100')
w('CONFigure:WLAN:SIGNaling1:PER:FDEF NHT,BW20,Q6M34,LONG')
w('CONFigure:WLAN:SIGNaling1:PER:LIMit 100')

results = []
print(f'{"BOPower(dBm)":>12} | {"sent":>4} | {"miss":>4} | {"PER %":>6}')
print('-'*40)
levels = list(range(-30, -86, -5)) + list(range(-72, -86, -1))
for bop in levels:
    w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower {bop}')
    time.sleep(0.6)
    cur_ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
    if cur_ip in ('','0.0.0.0','NAV'):
        print(f'{bop:>12} | DUT lost')
        results.append((bop, None, None, None)); continue
    w('INITiate:WLAN:SIGNaling1:PER')
    t0 = time.time()
    while time.time() - t0 < 25:
        time.sleep(0.4)
        if q('FETCh:WLAN:SIGNaling1:PER:STATe?') == 'RDY': break
    f = q('FETCh:WLAN:SIGNaling1:PER?').split(',')
    per = float(f[1]) if f[1] != 'INV' else None
    sent = int(float(f[2])) if f[2] != 'INV' else 0
    missing = int(float(f[3])) if f[3] != 'INV' else 0
    per_s = f'{per:.1f}' if per is not None else '—'
    print(f'{bop:>12} | {sent:>4} | {missing:>4} | {per_s:>6}')
    results.append((bop, sent, missing, per))
    if per is not None and per >= 99: break

# Restore BOPower
w('CONFigure:WLAN:SIGNaling1:RFSettings:BOPower -30')
w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,10,1000,PRAN,TID0')

# Save
with open('/home/zxf/keysight-test/wlan_ch1_ofdm54.csv','w',newline='') as fp:
    wr = csv.writer(fp)
    wr.writerow(['BOPower_dBm','sent','missing','PER_pct'])
    for r in results: wr.writerow(r)
print('\nCSV: /home/zxf/keysight-test/wlan_ch1_ofdm54.csv')
print(f'err: {q("SYST:ERR?")}')
