"""Channel 1 (2.412 GHz) multi-rate test: CCK (11b) + OFDM (11g) per-rate metrics.

Per rate measures:
- DUT TX burst power (Sig1 SENSe RXBPower while DUT replies to PG1 ping)
- PER at default BOPower (RX quality at strong link)
- EVM via Multi-Eval MODulation:OFDM (only valid for OFDM rates; DSSS uses different fetch)

NOTE: FW 3.7.40 WLAN_Sig V3.7.32 only supports STANdard = ASTD / BSTD / GSTD.
MCS (802.11n HT) is NOT available — skipped here.
"""
import pyvisa, time, os, sys, csv, subprocess, threading
for k in ('http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)

CMW = 'TCPIP0::192.0.2.10::5025::SOCKET'

# Rate plan
RATES = [
    # (label, STANdard, FDEF, mod_type)
    ('1 Mbps DBPSK',  'BSTD', 'NHT,BW20,D1MB,LONG', 'DSSS'),
    ('2 Mbps DQPSK',  'BSTD', 'NHT,BW20,D2MB,LONG', 'DSSS'),
    ('5.5 Mbps CCK',  'BSTD', 'NHT,BW20,C55M,LONG', 'DSSS'),
    ('11 Mbps CCK',   'BSTD', 'NHT,BW20,C11M,LONG', 'DSSS'),
    ('6 Mbps BPSK',   'GSTD', 'NHT,BW20,Q1M12,LONG', 'OFDM'),
    ('9 Mbps BPSK',   'GSTD', 'NHT,BW20,Q1M34,LONG', 'OFDM'),
    ('48 Mbps 64QAM', 'GSTD', 'NHT,BW20,Q6M23,LONG', 'OFDM'),
    ('54 Mbps 64QAM', 'GSTD', 'NHT,BW20,Q6M34,LONG', 'OFDM'),
]

rm = pyvisa.ResourceManager('@py')
inst = rm.open_resource(CMW)
inst.read_termination='\n'; inst.write_termination='\n'; inst.timeout=20000
inst.write('*CLS')

def w(s): inst.write(s); time.sleep(0.15)
def q(s): return inst.query(s).strip()

def sig_off_on(target_std, channel):
    """Restart Sig1 with new STANdard + channel (DUT will drop, must reconnect)."""
    w('SOURce:WLAN:SIGNaling1:STATe OFF')
    t0 = time.time()
    while time.time() - t0 < 30:
        if q('SOURce:WLAN:SIGNaling1:STATe?') == 'OFF': break
        time.sleep(0.5)
    w(f'CONFigure:WLAN:SIGNaling1:CONNection:STANdard {target_std}')
    w(f'CONFigure:WLAN:SIGNaling1:RFSettings:CHANnel {channel}')
    w('SOURce:WLAN:SIGNaling1:STATe ON')
    t0 = time.time()
    while time.time() - t0 < 60:
        if q('SOURce:WLAN:SIGNaling1:STATe?') == 'ON': break
        time.sleep(2)
    return time.time() - t0

def reconnect_dut(channel):
    """Force DUT to disconnect + reconnect to CMW-AP on given channel."""
    ps = f'''
$p = New-Object System.IO.Ports.SerialPort 'COM28', 115200, 'None', 8, 'One'
$p.ReadTimeout = 1500; $p.DtrEnable = $true; $p.RtsEnable = $true
$p.Open(); Start-Sleep -Milliseconds 200
$p.Write("AT+WLDISCONN`r`n"); Start-Sleep -Milliseconds 500
$p.DiscardInBuffer() | Out-Null
$p.Write("AT+WLCONN=ssid,CMW-AP,ch,{channel}`r`n")
Start-Sleep -Milliseconds 500
$p.Close()
Write-Output "WLCONN sent"
'''
    with open('/tmp/_reconnect.ps1','w') as f: f.write(ps)
    subprocess.run(['python','/tmp/winrm_run_ps_file.py','/tmp/_reconnect.ps1',
                    'C:\\\\Users\\\\<CMW_WINRM_USER>\\\\Documents\\\\_reconnect.ps1'], capture_output=True)
    # Wait for DUT to get IP
    for i in range(20):
        time.sleep(1)
        ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
        if ip not in ('', '0.0.0.0', 'NAV'): return ip
    return None

def measure_rate(label, std, fdef, mod_type):
    """Run a single rate's measurement battery."""
    print(f'\n========== {label} ({std}, {fdef}) ==========')
    # PER configuration
    w(f'CONFigure:WLAN:SIGNaling1:PER:FDEF {fdef}')
    w('CONFigure:WLAN:SIGNaling1:PER:PACKets 100')
    w('CONFigure:WLAN:SIGNaling1:PER:LIMit 100')

    # Ensure DUT IP for PG1
    dut_ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
    if dut_ip in ('', '0.0.0.0', 'NAV'):
        print('  DUT not associated — skip')
        return {'rate': label, 'std': std, 'fdef': fdef, 'state': 'no DUT'}
    w(f'CONFigure:WLAN:SIGNaling1:IPVFour:STATic:IPADdress:DESTination {dut_ip.replace(".",",")}')

    # PG1 ICMP flood ON (drives DUT TX + makes Sig1 RX active)
    w('CONFigure:WLAN:SIGNaling1:PGEN1:PROTocol ICMP')
    w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,10,500,PRAN,TID0')
    time.sleep(2)

    # Sample DUT TX burst power 3 seconds
    samples = []
    t0 = time.time()
    while time.time() - t0 < 3:
        try:
            p = float(q('SENSe:WLAN:SIGNaling1:UESinfo:RXBPower?'))
            if p > -100: samples.append(p)
        except: pass
        time.sleep(0.3)
    tx_pwr = sum(samples)/len(samples) if samples else None
    drate = q('SENSe:WLAN:SIGNaling1:UESinfo:DRATe?')
    print(f'  TX burst power : {tx_pwr:+.2f} dBm  (n={len(samples)})' if tx_pwr else '  TX burst power : (no samples)')
    print(f'  DUT actual rate: {drate}')

    # PER test
    w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,10,500,PRAN,TID0')   # PER runs its own packets
    w('INITiate:WLAN:SIGNaling1:PER')
    t0 = time.time()
    per_pct = None; sent = missing = 0
    while time.time() - t0 < 30:
        time.sleep(0.4)
        if q('FETCh:WLAN:SIGNaling1:PER:STATe?') == 'RDY': break
    try:
        fields = q('FETCh:WLAN:SIGNaling1:PER?').split(',')
        per_pct = float(fields[1]) if fields[1] != 'INV' else None
        sent = int(float(fields[2])) if fields[2] != 'INV' else 0
        missing = int(float(fields[3])) if fields[3] != 'INV' else 0
    except: pass
    print(f'  PER @ BOPower={q("CONFigure:WLAN:SIGNaling1:RFSettings:BOPower?")} dBm  ->  {per_pct}%  ({missing}/{sent} missing)')

    # EVM via Multi-Eval (OFDM only — DSSS uses :MODulation:DSSS fetch path)
    evm_rms = tx_pwr_meas = cf_err = sfl_field2 = None
    if mod_type == 'OFDM':
        w('ABORt:WLAN:MEAS1:MEValuation')
        w('ROUTe:WLAN:MEAS1:SCENario:CSPath "WLAN Sig1"')
        w('CONFigure:WLAN:MEAS1:RFSettings:FREQuency 2412000000')
        w('CONFigure:WLAN:MEAS1:RFSettings:ENPower1 30')
        w('CONFigure:WLAN:MEAS1:RFSettings:EATTenuation1 1')
        w('CONFigure:WLAN:MEAS1:ISIGnal:STANdard LOFDm')
        w('CONFigure:WLAN:MEAS1:ISIGnal:BWIDth BW20')
        w('TRIGger:WLAN:MEAS1:MEValuation:SOURce "WLAN Sig1: RXFrameTrigger"')
        w('CONFigure:WLAN:MEAS1:MEValuation:RESult:EVM ON')
        w('CONFigure:WLAN:MEAS1:MEValuation:RESult:SFLatness ON')
        w('CONFigure:WLAN:MEAS1:MEValuation:SCOunt:MODulation 20')
        w('CONFigure:WLAN:MEAS1:MEValuation:REPetition SING')
        w('CONFigure:WLAN:MEAS1:MEValuation:TOUT 40')
        w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,10,500,PRAN,TID0')   # back on for MEAS triggering
        time.sleep(2)
        w('INITiate:WLAN:MEAS1:MEValuation')
        t0 = time.time()
        while time.time() - t0 < 30:
            time.sleep(0.5)
            if q('FETCh:WLAN:MEAS1:MEValuation:STATe?') == 'RDY': break
        try:
            fields = q('FETCh:WLAN:MEAS1:MEValuation:MODulation:OFDM:AVERage?').split(',')
            if fields[0] == '0':
                tx_pwr_meas = float(fields[3])
                evm_rms = float(fields[4])
                cf_err = float(fields[7])
            print(f'  EVM (Multi-Eval): rms={evm_rms} dB  TX={tx_pwr_meas} dBm  CF={cf_err} Hz')
        except: pass
        try:
            sfl = q('FETCh:WLAN:MEAS1:MEValuation:SFLatness:AVERage?').split(',')
            if sfl[0] == '0':
                sfl_field2 = float(sfl[1])
                print(f'  SFLatness max neg deviation: {sfl_field2} dB')
        except: pass
        w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,10,500,PRAN,TID0')
    else:
        # DSSS — try the DSSS modulation fetch
        w('ABORt:WLAN:MEAS1:MEValuation')
        w('ROUTe:WLAN:MEAS1:SCENario:CSPath "WLAN Sig1"')
        w('CONFigure:WLAN:MEAS1:RFSettings:FREQuency 2412000000')
        w('CONFigure:WLAN:MEAS1:RFSettings:ENPower1 30')
        w('CONFigure:WLAN:MEAS1:ISIGnal:STANdard DSSS')
        w('CONFigure:WLAN:MEAS1:MEValuation:RESult:EVM ON')
        w('CONFigure:WLAN:MEAS1:MEValuation:SCOunt:MODulation 20')
        w('CONFigure:WLAN:MEAS1:MEValuation:REPetition SING')
        w('CONFigure:WLAN:MEAS1:MEValuation:TOUT 40')
        w('TRIGger:WLAN:MEAS1:MEValuation:SOURce "WLAN Sig1: RXFrameTrigger"')
        w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,10,500,PRAN,TID0')
        time.sleep(2)
        w('INITiate:WLAN:MEAS1:MEValuation')
        t0 = time.time()
        while time.time() - t0 < 30:
            time.sleep(0.5)
            if q('FETCh:WLAN:MEAS1:MEValuation:STATe?') == 'RDY': break
        try:
            fields = q('FETCh:WLAN:MEAS1:MEValuation:MODulation:DSSS:AVERage?').split(',')
            if fields[0] == '0':
                evm_rms = float(fields[3]) if len(fields) > 3 else None
                tx_pwr_meas = float(fields[4]) if len(fields) > 4 else None
                print(f'  EVM (Multi-Eval DSSS): {q("FETCh:WLAN:MEAS1:MEValuation:MODulation:DSSS:AVERage?").strip()[:160]}')
            else:
                print(f'  EVM DSSS fetch: reliab={fields[0]}, raw={q("FETCh:WLAN:MEAS1:MEValuation:MODulation:DSSS:AVERage?").strip()[:160]}')
        except: pass
        w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,10,500,PRAN,TID0')

    return {
        'rate': label, 'std': std, 'fdef': fdef, 'mod_type': mod_type,
        'tx_pwr_sig1': tx_pwr,
        'drate': drate,
        'per_pct': per_pct, 'per_sent': sent, 'per_missing': missing,
        'evm_rms': evm_rms, 'tx_pwr_meas': tx_pwr_meas, 'cf_err': cf_err,
        'sfl': sfl_field2,
    }

# Main flow
print(f'IDN: {q("*IDN?")}')

# Switch to ch1 + BSTD first
print('\n=== Switching to BSTD ch1 ===')
elapsed = sig_off_on('BSTD', 1)
print(f'  Sig restart took {elapsed:.1f}s')
ip = reconnect_dut(1)
print(f'  DUT IP: {ip}')
if not ip:
    print('  !! DUT failed to associate at ch1 (BSTD)')
    sys.exit(1)

# Test all BSTD rates
results = []
for label, std, fdef, mt in [r for r in RATES if r[1] == 'BSTD']:
    results.append(measure_rate(label, std, fdef, mt))

# Switch to GSTD (still ch1, just standard change — DUT may need re-assoc)
print('\n=== Switching to GSTD ch1 ===')
elapsed = sig_off_on('GSTD', 1)
print(f'  Sig restart took {elapsed:.1f}s')
ip = reconnect_dut(1)
print(f'  DUT IP: {ip}')

if ip:
    for label, std, fdef, mt in [r for r in RATES if r[1] == 'GSTD']:
        results.append(measure_rate(label, std, fdef, mt))

# Save CSV
print('\n=== Summary ===')
fields = ['rate','std','fdef','mod_type','drate','tx_pwr_sig1','per_pct','per_sent','per_missing','evm_rms','tx_pwr_meas','cf_err','sfl']
with open('/home/zxf/keysight-test/wlan_ch1_multirate.csv','w',newline='') as f:
    wr = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    wr.writeheader()
    for r in results: wr.writerow(r)

# Print table
print(f'{"Rate":18s} {"DRATe":24s} {"TX (Sig1)":10s} {"PER%":6s} {"EVM RMS":8s}')
for r in results:
    print(f'  {r.get("rate",""):18s}'
          f' {str(r.get("drate","")):24s}'
          f' {(f"{r["tx_pwr_sig1"]:+.2f} dBm" if r.get("tx_pwr_sig1") else "—"):10s}'
          f' {(f"{r["per_pct"]:.1f}" if r.get("per_pct") is not None else "—"):6s}'
          f' {(f"{r["evm_rms"]:.1f} dB" if r.get("evm_rms") else "—"):8s}')

print('\nCSV: /home/zxf/keysight-test/wlan_ch1_multirate.csv')
inst.close()
