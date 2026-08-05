"""RX sensitivity sweep with PG1 keep-alive in background.

Hypothesis: leaving PG1 on at a slow rate (50 TU = ~50 ms, ~20 pps) keeps the DUT
out of power-save during the PER sweep, lowering the ~20% PER baseline.
"""
import pyvisa, time, os, sys, csv
for k in ('http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)

rm = pyvisa.ResourceManager('@py')
inst = rm.open_resource('TCPIP0::192.0.2.10::5025::SOCKET')
inst.read_termination='\n'; inst.write_termination='\n'; inst.timeout=30000
inst.write('*CLS')

def w(s): inst.write(s); time.sleep(0.15)
def q(s): return inst.query(s).strip()

if q('SOURce:WLAN:SIGNaling1:STATe?') != 'ON':
    sys.exit('Sig not ON')
dut_ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
if dut_ip in ('', '0.0.0.0'):
    sys.exit('DUT not associated')
print(f'DUT IP: {dut_ip}')

# PG1 destination = DUT IP
w(f'CONFigure:WLAN:SIGNaling1:IPVFour:STATic:IPADdress:DESTination {dut_ip.replace(".",",")}')
w('CONFigure:WLAN:SIGNaling1:PGEN1:PROTocol ICMP')
w('CONFigure:WLAN:SIGNaling1:PGEN1:IPVersion IV4')

# Enable PG1 keep-alive: 50 TU = ~51 ms, 200-byte ICMP (small + slow, just to keep DUT awake)
w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,50,200,PRAN,TID0')
print(f'PG1 keep-alive: {q("CONFigure:WLAN:SIGNaling1:PGEN1:CONFig?")}')
time.sleep(2.0)   # let DUT settle

# PER test config
w('CONFigure:WLAN:SIGNaling1:PER:PACKets 200')
w('CONFigure:WLAN:SIGNaling1:PER:FDEF NHT,BW20,Q1M12,LONG')
w('CONFigure:WLAN:SIGNaling1:PER:LIMit 100')

results = []
print(f'\n{"BOPower":>8} | {"sent":>4} | {"miss":>4} | {"PER %":>7}')
print('-'*40)
# Coarse pass first (-30 to -85), then fine (-80 to -90)
levels = list(range(-30, -86, -5)) + list(range(-78, -91, -1))
for bop in levels:
    w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower {bop}')
    time.sleep(0.5)
    if q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"') in ('', '0.0.0.0'):
        print(f'{bop:>8} | DUT lost'); results.append((bop, None, None, None)); continue
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
    print(f'{bop:>8} | {sent:>4} | {missing:>4} | {per_pct if per_pct is not None else "INV":>7}')
    results.append((bop, sent, missing, per_pct))
    if per_pct is not None and per_pct >= 99:
        break

w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,50,200,PRAN,TID0')
w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower -30')

with open('/home/zxf/keysight-test/wlan_rx_keepalive.csv','w',newline='') as f:
    wr = csv.writer(f); wr.writerow(['BOPower_dBm','sent','missing','PER_pct'])
    for r in results: wr.writerow(r)
print(f'\nfinal err: {q("SYST:ERR?")}')
inst.close()
