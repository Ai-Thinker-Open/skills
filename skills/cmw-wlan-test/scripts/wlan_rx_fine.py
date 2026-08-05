"""Fine 1-dB sweep between -78 and -86 dBm to localize 10% PER threshold."""
import pyvisa, time, os, sys, csv
for k in ('http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)
rm = pyvisa.ResourceManager('@py')
inst = rm.open_resource('TCPIP0::192.0.2.10::5025::SOCKET')
inst.read_termination='\n'; inst.write_termination='\n'; inst.timeout=30000
inst.write('*CLS')
def w(s): inst.write(s); time.sleep(0.15)
def q(s): return inst.query(s).strip()

# Verify state
if q('SOURce:WLAN:SIGNaling1:STATe?') != 'ON':
    sys.exit('Sig not ON')
dut_ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
if dut_ip in ('', '0.0.0.0'):
    sys.exit('DUT not associated')
print(f'DUT IP: {dut_ip}')

w('CONFigure:WLAN:SIGNaling1:PER:PACKets 300')   # more packets for better statistics near threshold
w('CONFigure:WLAN:SIGNaling1:PER:FDEF NHT,BW20,Q1M12,LONG')
w('CONFigure:WLAN:SIGNaling1:PER:LIMit 100')

results = []
print(f'\n{"BOPower":>8} | {"sent":>4} | {"miss":>4} | {"PER %":>6}')
print('-'*42)
for bop in range(-77, -90, -1):
    w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower {bop}')
    time.sleep(0.6)
    # re-check association
    if q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"') in ('', '0.0.0.0'):
        print(f'{bop:>8.1f} | DUT lost')
        results.append((bop, None, None, None))
        continue
    w('INITiate:WLAN:SIGNaling1:PER')
    t0 = time.time()
    while time.time() - t0 < 30:
        time.sleep(0.4)
        if q('FETCh:WLAN:SIGNaling1:PER:STATe?') == 'RDY':
            break
    f = q('FETCh:WLAN:SIGNaling1:PER?').split(',')
    per_pct = float(f[1]) if f[1] != 'INV' else None
    sent    = int(float(f[2])) if f[2] != 'INV' else 0
    missing = int(float(f[3])) if f[3] != 'INV' else 0
    print(f'{bop:>8.1f} | {sent:>4} | {missing:>4} | {per_pct if per_pct is not None else "INV":>6}')
    results.append((bop, sent, missing, per_pct))
    if per_pct is not None and per_pct >= 95:
        break

# Save & summarize
with open('/home/zxf/keysight-test/wlan_rx_fine.csv','w',newline='') as f:
    wr = csv.writer(f); wr.writerow(['BOPower_dBm','sent','missing','PER_pct'])
    for r in results: wr.writerow(r)

# Find 10% crossing by linear interpolation
crossing = None
for i in range(1, len(results)):
    p_prev = results[i-1][3]
    p_curr = results[i][3]
    if p_prev is None or p_curr is None: continue
    if p_prev < 10 <= p_curr:
        bop_prev = results[i-1][0]
        bop_curr = results[i][0]
        frac = (10 - p_prev) / (p_curr - p_prev)
        crossing = bop_prev + frac * (bop_curr - bop_prev)
        break
print(f'\n10% PER crossing (linear interp): {crossing:.2f} dBm' if crossing else '\nno 10% crossing in this range')
print(f'final err: {q("SYST:ERR?")}')
w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower -30')
inst.close()
