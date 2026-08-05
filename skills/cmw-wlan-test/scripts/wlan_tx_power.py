"""DUT TX power: PG1 pings DUT, read DUT's reply burst power via Sig1 RX sensor.

Pre-req: DUT already associated to CMW-AP via AT+WLCONN.
"""
import pyvisa, time, os, sys
for k in ('http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)

CMW = 'TCPIP0::192.0.2.10::5025::SOCKET'
BOPOWER_DBM = -30.0
EPEPOWER_DBM = 18.0
DURATION_S  = 5     # seconds of traffic to average over

rm = pyvisa.ResourceManager('@py')
inst = rm.open_resource(CMW)
inst.read_termination = '\n'
inst.write_termination = '\n'
inst.timeout = 20000
inst.write('*CLS')

def w(s): inst.write(s); time.sleep(0.2)
def q(s): return inst.query(s).strip()
def err_ok():
    e = q('SYST:ERR?')
    if not e.startswith('0,'):
        print(f'  !! SCPI err: {e}'); sys.exit(1)

print(f'IDN: {q("*IDN?")}')

# --- 1) Verify association ----------------------------------
print('\n--- DUT association ---')
print(f'  Sig STATe   = {q("SOURce:WLAN:SIGNaling1:STATe?")}')
dut_ip = q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
print(f'  DUT IP      = {dut_ip}')
if dut_ip in ('', '0.0.0.0'):
    sys.exit('  !! DUT not associated. Run AT+WLCONN first.')

# --- 2) RF settings (idempotent) ----------------------------
print('\n--- RF settings ---')
cur_bo = float(q('CONFigure:WLAN:SIGNaling1:RFSettings:BOPower?'))
cur_ep = float(q('CONFigure:WLAN:SIGNaling1:RFSettings:EPEPower?'))
print(f'  current BOPower={cur_bo:.1f} dBm, EPEPower={cur_ep:.1f} dBm')
if abs(cur_bo - BOPOWER_DBM) > 0.5:
    w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower {BOPOWER_DBM}'); err_ok()
if abs(cur_ep - EPEPOWER_DBM) > 0.5:
    w(f'CONFigure:WLAN:SIGNaling1:RFSettings:EPEPower {EPEPOWER_DBM}'); err_ok()

# --- 3) PG1 destination = DUT IP -----------------------------
dut_ip_csv = dut_ip.replace('.', ',')
w(f'CONFigure:WLAN:SIGNaling1:IPVFour:STATic:IPADdress:DESTination {dut_ip_csv}')
err_ok()
w('CONFigure:WLAN:SIGNaling1:PGEN1:PROTocol ICMP'); err_ok()
w('CONFigure:WLAN:SIGNaling1:PGEN1:IPVersion IV4'); err_ok()

# --- 4) Enable PG1: 10 TU interval, 1000-byte ICMP echo ------
print('\n--- Start PG1 (ICMP ping to DUT) ---')
w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,10,1000,PRAN,TID0'); err_ok()
print(f'  PGEN1 cfg   = {q("CONFigure:WLAN:SIGNaling1:PGEN1:CONFig?")}')

# --- 5) Sample DUT TX burst power for DURATION_S seconds -----
print(f'\n--- Sampling DUT TX burst power over {DURATION_S} s ---')
samples = []
t_start = time.time()
while time.time() - t_start < DURATION_S:
    inst_p  = float(q('SENSe:WLAN:SIGNaling1:UESinfo:RXBPower?'))   # instant
    avg_p   = float(q('SENSe:WLAN:SIGNaling1:UESinfo:ARXBpower?'))  # rolling avg
    samples.append((time.time() - t_start, inst_p, avg_p))
    print(f'  t={samples[-1][0]:4.1f}s  inst={inst_p:6.2f} dBm  rolling-avg={avg_p:6.2f} dBm')
    time.sleep(0.5)

# --- 6) Stats over sampled instants ---------------------------
inst_vals = [s[1] for s in samples if s[1] > -100]
print(f'\nSamples: n={len(inst_vals)}')
if inst_vals:
    print(f'  mean   = {sum(inst_vals)/len(inst_vals):+.2f} dBm')
    print(f'  min    = {min(inst_vals):+.2f} dBm')
    print(f'  max    = {max(inst_vals):+.2f} dBm')

# --- 7) Stop PG1 -----------------------------------------
w('CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,10,1000,PRAN,TID0')
print(f'\nfinal err: {q("SYST:ERR?")}')
inst.close()
