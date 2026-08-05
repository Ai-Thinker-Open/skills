"""DUT RX sensitivity sweep: CMW PER test at decreasing BOPower; find 10%-PER threshold.

CMW WLAN Sig1 PER test sends N packets to the DUT and counts missing ACKs.
We sweep BOPower from start_dbm down by step_db until PER >= 10% (sensitivity).
"""
import pyvisa, time, os, sys, csv
for k in ('http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)

CMW       = 'TCPIP0::192.0.2.10::5025::SOCKET'
START_DBM = -30
STOP_DBM  = -95
STEP_DB   =  5     # coarse first; refine near threshold
PACKETS   = 100    # per power level (200 was slow)
TIMEOUT_S = 30     # per-level test timeout
FDEF      = 'NHT,BW20,Q1M12,LONG'   # 802.11a 6 Mbps BPSK 1/2 (most robust)

rm = pyvisa.ResourceManager('@py')
inst = rm.open_resource(CMW)
inst.read_termination = '\n'
inst.write_termination = '\n'
inst.timeout = 30000
inst.write('*CLS')

def w(s): inst.write(s); time.sleep(0.15)
def q(s): return inst.query(s).strip()

print(f'IDN: {q("*IDN?")}')
print(f'Sig STATe: {q("SOURce:WLAN:SIGNaling1:STATe?")}')
dut_ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
print(f'DUT IP   : {dut_ip}')
if dut_ip in ('', '0.0.0.0'):
    sys.exit('!! DUT not associated. Run AT+WLCONN first.')

# Make sure PG1 is OFF — PER test runs its own traffic
w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,10,1000,PRAN,TID0')

# Configure PER: low-rate frame, generous packet count, no early stop
w(f'CONFigure:WLAN:SIGNaling1:PER:PACKets {PACKETS}')
w(f'CONFigure:WLAN:SIGNaling1:PER:FDEF {FDEF}')
w('CONFigure:WLAN:SIGNaling1:PER:LIMit 100')   # 100% (don't stop early)
print(f'PER:PACKets = {q("CONFigure:WLAN:SIGNaling1:PER:PACKets?")}')
print(f'PER:FDEF    = {q("CONFigure:WLAN:SIGNaling1:PER:FDEF?")}')

results = []
print(f'\n{"BOPower(dBm)":>13} | {"sent":>5} | {"missing":>7} | {"PER %":>6} | {"RSSI@DUT~":>10}')
print('-' * 60)

bop = START_DBM
while bop >= STOP_DBM:
    w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower {bop}')
    time.sleep(0.6)            # allow new power to settle
    # Re-check DUT still associated (low BOPower may drop link)
    cur_ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
    if cur_ip in ('', '0.0.0.0'):
        print(f'  BOPower={bop} dBm -> DUT lost association')
        results.append((bop, None, None, None))
        bop -= STEP_DB
        continue
    # Start PER, wait for RDY
    w('INITiate:WLAN:SIGNaling1:PER')
    t0 = time.time()
    while time.time() - t0 < TIMEOUT_S:
        time.sleep(0.5)
        st = q('FETCh:WLAN:SIGNaling1:PER:STATe?')
        if st == 'RDY':
            break
    else:
        print(f'  BOPower={bop} dBm -> PER timeout, abort')
        w('ABORt:WLAN:SIGNaling1:PER')
        results.append((bop, None, None, None))
        bop -= STEP_DB
        continue
    fields = q('FETCh:WLAN:SIGNaling1:PER?').split(',')
    # Returns: <reliab>, <PER_pct>, <sent>, <missing>, <duration_s>
    rel = fields[0]
    per_pct = float(fields[1]) if fields[1] != 'INV' else None
    sent    = int(float(fields[2])) if fields[2] != 'INV' else None
    missing = int(float(fields[3])) if fields[3] != 'INV' else None
    # Indicative RSSI at DUT (assuming small cable EATT) ≈ BOPower
    rssi_est = bop - 1   # rough: subtract 1 dB cable loss
    print(f'{bop:>13.1f} | {str(sent):>5} | {str(missing):>7} | {per_pct if per_pct is not None else "INV":>6} | {rssi_est:>10.1f}')
    results.append((bop, sent, missing, per_pct))
    # Mark first crossing but keep sweeping to map full curve
    if per_pct is not None and per_pct >= 10.0 and not any(r[3] is not None and r[3] >= 10 for r in results[:-1]):
        print(f'  ** PER crossed 10% at BOPower={bop} dBm (PER={per_pct}%)')
    # Stop once PER is essentially 100% (link lost) -- nothing more to learn
    if per_pct is not None and per_pct >= 95.0:
        print(f'  ** link lost at BOPower={bop} dBm')
        break
    bop -= STEP_DB

# Cleanup
w('ABORt:WLAN:SIGNaling1:PER')
w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower {START_DBM}')

# Save CSV
csv_path = '/home/zxf/keysight-test/wlan_rx_sensitivity.csv'
with open(csv_path, 'w', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(['BOPower_dBm', 'sent', 'missing', 'PER_pct'])
    for r in results: wr.writerow(r)
print(f'\nCSV: {csv_path}')
print(f'final err: {q("SYST:ERR?")}')
inst.close()
