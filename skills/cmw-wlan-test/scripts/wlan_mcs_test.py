"""MCS 1-7 testing in ANST (802.11a/n) mode on ch1."""
import pyvisa, time, os, csv
for k in ('http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)

rm = pyvisa.ResourceManager('@py')
inst = rm.open_resource('TCPIP0::192.0.2.10::5025::SOCKET')
inst.read_termination='\n'; inst.write_termination='\n'; inst.timeout=20000
inst.write('*CLS')

def w(s): inst.write(s); time.sleep(0.15)
def q(s): return inst.query(s).strip()

# Verify state
print(f'STANdard: {q("CONFigure:WLAN:SIGNaling1:CONNection:STANdard?")}')
print(f'CH      : {q("CONFigure:WLAN:SIGNaling1:RFSettings:CHANnel?")}')
print(f'DUT IP  : {q("SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?")}')

# PG1 ON for traffic
dut_ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
w(f'CONFigure:WLAN:SIGNaling1:IPVFour:STATic:IPADdress:DESTination {dut_ip.replace(".",",")}')
w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,10,1000,PRAN,TID0')
time.sleep(3)
print(f'RXBP    : {q("SENSe:WLAN:SIGNaling1:UESinfo:RXBPower?")} dBm')
print(f'DRATe   : {q("SENSe:WLAN:SIGNaling1:UESinfo:DRATe?")}')

# PER test for each MCS1-7
print('\n=== MCS PER sweep ===')
print(f'{"MCS":>5} {"FDEF":>30} {"TX(dBm)":>9} {"sent":>5} {"miss":>5} {"PER%":>6} {"DRATe":>30}')

results = []
for mcs in range(1, 8):
    fdef = f'HTM,BW20,MCS{mcs},LONG'
    w(f'CONFigure:WLAN:SIGNaling1:PER:FDEF {fdef}')
    w('CONFigure:WLAN:SIGNaling1:PER:PACKets 100')
    w('CONFigure:WLAN:SIGNaling1:PER:LIMit 100')

    # Sample DUT TX power
    samples = []
    t0 = time.time()
    while time.time() - t0 < 2:
        try:
            p = float(q('SENSe:WLAN:SIGNaling1:UESinfo:RXBPower?'))
            if p > -100: samples.append(p)
        except: pass
        time.sleep(0.3)
    tx_pwr = sum(samples)/len(samples) if samples else None
    drate = q('SENSe:WLAN:SIGNaling1:UESinfo:DRATe?')

    # Run PER
    w('INITiate:WLAN:SIGNaling1:PER')
    t0 = time.time()
    while time.time() - t0 < 30:
        time.sleep(0.4)
        if q('FETCh:WLAN:SIGNaling1:PER:STATe?') == 'RDY': break
    f = q('FETCh:WLAN:SIGNaling1:PER?').split(',')
    per = float(f[1]) if f[1] != 'INV' else None
    sent = int(float(f[2])) if f[2] != 'INV' else 0
    missing = int(float(f[3])) if f[3] != 'INV' else 0
    tx_s = f'{tx_pwr:+.2f}' if tx_pwr else '—'
    per_s = f'{per:.1f}' if per is not None else '—'
    print(f'{f"MCS{mcs}":>5} {fdef:>30} {tx_s:>9} {sent:>5} {missing:>5} {per_s:>6} {drate:>30}')
    results.append({'mcs': mcs, 'fdef': fdef, 'tx_pwr': tx_pwr, 'sent': sent, 'missing': missing, 'per_pct': per, 'drate': drate})

# Multi-Eval at MCS7 (highest rate, where DUT likely operates)
print('\n=== Multi-Eval @ MCS7 (HTOFDM modulation fetch) ===')
w('ABORt:WLAN:MEAS1:MEValuation')
w('ROUTe:WLAN:MEAS1:SCENario:CSPath "WLAN Sig1"')
w('CONFigure:WLAN:MEAS1:RFSettings:FREQuency 2412000000')
w('CONFigure:WLAN:MEAS1:RFSettings:ENPower1 30')
# Try HT-OFDM standard on MEAS
for s in ['HTOFdm','HOFDm','HTOFDM','HT','HTM','MIXed','LOFDm']:
    inst.write(f'CONFigure:WLAN:MEAS1:ISIGnal:STANdard {s}')
    e = inst.query('SYST:ERR?').strip()
    if e.startswith('0,'):
        rb = inst.query('CONFigure:WLAN:MEAS1:ISIGnal:STANdard?').strip()
        print(f'  MEAS1 ISIG STAN {s} -> {rb}')
        break
w('CONFigure:WLAN:MEAS1:ISIGnal:BWIDth BW20')
w('TRIGger:WLAN:MEAS1:MEValuation:SOURce "WLAN Sig1: RXFrameTrigger"')
w('CONFigure:WLAN:MEAS1:MEValuation:RESult:EVM ON')
w('CONFigure:WLAN:MEAS1:MEValuation:RESult:SFLatness ON')
w('CONFigure:WLAN:MEAS1:MEValuation:SCOunt:MODulation 20')
w('CONFigure:WLAN:MEAS1:MEValuation:REPetition SING')
w('CONFigure:WLAN:MEAS1:MEValuation:TOUT 30')

w('INITiate:WLAN:MEAS1:MEValuation')
t0 = time.time()
while time.time() - t0 < 30:
    time.sleep(0.5)
    if q('FETCh:WLAN:MEAS1:MEValuation:STATe?') == 'RDY': break
# Try HTOFdm fetch path
for path in ['FETCh:WLAN:MEAS1:MEValuation:MODulation:HTOFdm:AVERage?',
             'FETCh:WLAN:MEAS1:MEValuation:MODulation:OFDM:AVERage?',
             'FETCh:WLAN:MEAS1:MEValuation:MODulation:AVERage?']:
    try:
        r = q(path)
        print(f'  {path.split(":")[-2]}: {r[:240]}')
    except Exception as e:
        print(f'  {path.split(":")[-2]}: TMO')
        time.sleep(5)

# Save CSV
with open('/home/zxf/keysight-test/wlan_mcs_results.csv','w',newline='') as fp:
    wr = csv.DictWriter(fp, fieldnames=['mcs','fdef','tx_pwr','sent','missing','per_pct','drate'])
    wr.writeheader()
    for r in results: wr.writerow(r)

w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,10,1000,PRAN,TID0')
print(f'\nCSV: /home/zxf/keysight-test/wlan_mcs_results.csv')
print(f'final err: {q("SYST:ERR?")}')
