"""WLAN full compliance test driver for RTL8711DAN AmebaDplus on CMW-500.

Mode-outer / channel-inner iteration over verified DUT capability set:
- 2.4 GHz: BSTD / GSTD / GNST on ch 1, 3, 6, 9, 11
- 5 GHz:   ASTD / ANST       on ch 36, 40, 52, 64, 100, 132, 149, 165

Per cell:
- TX: PG1 ICMP flood, Multi-Eval 40 bursts → MODulation (OFDM or DSSS) + SFLatness
- TX HT: also forces DFRControl+DFDef to specific MCS{1,4,7}
- RX: PG1 keep-alive @ 50 TU/200 B, coarse PER (5 dB step -30..-85), fine PER (1 dB
  around cliff), 10% / 50% threshold interpolation

Outputs:
  wlan_full_compliance_tx.csv         — TX per (ch,mode[,mcs])
  wlan_full_compliance_rx_coarse.csv  — RX coarse raw
  wlan_full_compliance_rx_fine.csv    — RX fine raw
  wlan_full_compliance_rx_summary.csv — RX 10% / 50% threshold per cell
  wlan_full_compliance_progress.csv   — checkpoint log (done/skip/fail/recovered)

Usage:
  python wlan_full_compliance.py --phase A [--resume]   # TX all + RX 2 sample ch/mode
  python wlan_full_compliance.py --phase B [--resume]   # full RX matrix
  python wlan_full_compliance.py --phase all [--resume]
"""
import pyvisa, time, os, sys, csv, subprocess, argparse, socket
from datetime import datetime

for k in ('http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)

# ============================================================================
# Configuration
# ============================================================================
CMW_HOST       = '192.0.2.10'
CMW_RESOURCE   = f'TCPIP0::{CMW_HOST}::5025::SOCKET'
EATT_24G_dB    = 1.0      # direct coax, 2.4 GHz cable loss
EATT_5G_dB     = 1.0      # direct coax, 5 GHz cable loss (TODO refine via VNA)
BOPOWER_DEFAULT = -30     # baseline TX power for non-RX tests
EPEPOWER_dBm   = 30       # required ≥30 to avoid Sig1 RX AGC saturation

# Channels per band
CHANNELS_24G = [1, 3, 6, 9, 11]
CHANNELS_5G  = [36, 40, 52, 64, 100, 132, 149, 165]
DFS_CHANNELS = {52, 64, 100, 132}    # may fail to associate (regulatory)

# Phase A: which channels get RX sampled (band edges + center)
PHASE_A_RX_24G = {1, 6, 11}
PHASE_A_RX_5G  = {36, 100, 165}

# Mode definitions: (STANdard, band, ordered list of NHT rate codes, HT MCS list or [])
MODES = [
    ('BSTD', '2.4G', ['D1MB','D2MB','C55M','C11M'], []),       # 11b CCK
    ('GSTD', '2.4G', ['Q1M12','Q1M34','Q6M23','Q6M34'], []),    # 11g OFDM
    ('GNST', '2.4G', ['Q1M12','Q1M34','Q6M23','Q6M34'], [1,4,7]),  # 11g/n + HT
    ('ASTD', '5G',   ['Q1M12','Q1M34','Q6M23','Q6M34'], []),    # 11a OFDM
    ('ANST', '5G',   ['Q1M12','Q1M34','Q6M23','Q6M34'], [1,4,7]),  # 11a/n + HT
]

# Files
OUT_DIR = '/home/zxf/keysight-test'
TX_CSV          = f'{OUT_DIR}/wlan_full_compliance_tx.csv'
RX_COARSE_CSV   = f'{OUT_DIR}/wlan_full_compliance_rx_coarse.csv'
RX_FINE_CSV     = f'{OUT_DIR}/wlan_full_compliance_rx_fine.csv'
RX_SUMMARY_CSV  = f'{OUT_DIR}/wlan_full_compliance_rx_summary.csv'
PROGRESS_CSV    = f'{OUT_DIR}/wlan_full_compliance_progress.csv'

# Multi-Eval / PER configuration
MEV_SCOUNT      = 40        # bursts to average for TX measurement
PER_PACKETS_COARSE = 100
PER_PACKETS_FINE   = 200
PER_TIMEOUT_S      = 30     # per INITiate

# PG1 ICMP flood (for TX measurement)
PG1_TX_INTERVAL = 10        # TU
PG1_TX_SIZE     = 1000      # bytes
# PG1 keep-alive (background during RX sweep, lowers baseline PER)
PG1_KA_INTERVAL = 50        # TU (slower → DUT stays awake without saturating)
PG1_KA_SIZE     = 200

# ============================================================================
# SCPI session wrapper
# ============================================================================
class CMW:
    def __init__(self):
        self.inst = None
        self.cmd_count = 0
        self._connect()

    def _connect(self):
        rm = pyvisa.ResourceManager('@py')
        self.inst = rm.open_resource(CMW_RESOURCE)
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'
        self.inst.timeout = 15000
        self.inst.write('*CLS')
        self.cmd_count = 0

    def _maybe_recycle(self):
        """Every 30 commands, close + reconnect to clear any accumulated session state."""
        self.cmd_count += 1
        if self.cmd_count >= 30:
            try: self.inst.close()
            except: pass
            time.sleep(0.5)
            self._connect()

    def w(self, scpi):
        self.inst.write(scpi)
        time.sleep(0.12)
        self._maybe_recycle()

    def q(self, scpi):
        try:
            r = self.inst.query(scpi).strip()
            self._maybe_recycle()
            return r
        except Exception:
            return 'TMO'

    def health(self):
        return self.q('SOURce:WLAN:SIGNaling1:STATe?') in ('ON','OFF','PEND','RDY')

    def reboot_recover(self):
        """Reboot CMW via WinRM helper, wait for SCPI back, then reconnect."""
        print('  >> CMW deadlock detected — initiating reboot recovery', flush=True)
        try: self.inst.close()
        except: pass
        subprocess.run(['python','/tmp/cmw_reboot.py'], capture_output=True, timeout=480)
        # Wait for SCPI port
        t0 = time.time()
        while time.time() - t0 < 500:
            try:
                s = socket.socket(); s.settimeout(2); s.connect((CMW_HOST, 5025))
                s.sendall(b'*IDN?\n'); d = s.recv(256); s.close()
                if d and b'CMW' in d:
                    self._connect()
                    print(f'  >> SCPI back after {time.time()-t0:.0f}s', flush=True)
                    return True
            except: pass
            time.sleep(3)
        return False

# ============================================================================
# DUT serial control (via WinRM PowerShell)
# ============================================================================
def dut_reconnect(channel, retries=3):
    """Force DUT disconnect+connect on given channel. Return DUT IP or None."""
    ps = f'''$p = New-Object System.IO.Ports.SerialPort 'COM28', 115200, 'None', 8, 'One'
$p.ReadTimeout = 1500; $p.DtrEnable = $true; $p.RtsEnable = $true
$p.Open(); Start-Sleep -Milliseconds 200
$p.Write("AT+WLDISCONN`r`n"); Start-Sleep -Milliseconds 500
$p.DiscardInBuffer() | Out-Null
$p.Write("AT+WLCONN=ssid,CMW-AP,ch,{channel}`r`n")
Start-Sleep -Milliseconds 500
$p.Close()
'''
    with open('/tmp/_reconnect.ps1','w') as f: f.write(ps)
    for attempt in range(retries):
        subprocess.run(['python','/tmp/winrm_run_ps_file.py','/tmp/_reconnect.ps1',
                        'C:\\Users\\<CMW_WINRM_USER>\\Documents\\_reconnect.ps1'],
                       capture_output=True, timeout=30)
        time.sleep(8)
        return None  # caller will check via CMW SENSe


# ============================================================================
# Helpers
# ============================================================================
def band_of(channel):
    return '2.4G' if channel <= 13 else '5G'

def freq_of(channel):
    if channel <= 13:
        return 2407_000_000 + channel * 5_000_000   # 2.4 GHz: 2412 + (ch-1)*5 MHz
    # 5 GHz: ch * 5 MHz + 5000 MHz (simplified)
    return 5000_000_000 + channel * 5_000_000

def eatt_of(channel):
    return EATT_24G_dB if channel <= 13 else EATT_5G_dB

def fdef_for(mode, rate_code):
    """Build full PER:FDEF string from rate code."""
    if rate_code.startswith('MCS'):
        return f'HTM,BW20,{rate_code},LONG'
    return f'NHT,BW20,{rate_code},LONG'

def dfrcontrol_for_rate(rate_code):
    """DFRControl value (NHT rate code or MCS{n})."""
    return rate_code   # accepts the same codes (Q6M34, MCS7, etc.)


# ============================================================================
# Test execution
# ============================================================================
def setup_mode_and_channel(cmw, std, channel, dfrcontrol_rate='Q6M34'):
    """Switch CMW to given STANdard + channel + DFRControl, restart Sig1."""
    cmw.w('SOURce:WLAN:SIGNaling1:STATe OFF')
    t0 = time.time()
    while time.time() - t0 < 25:
        if cmw.q('SOURce:WLAN:SIGNaling1:STATe?') == 'OFF': break
        time.sleep(0.5)

    cmw.w(f'CONFigure:WLAN:SIGNaling1:CONNection:STANdard {std}')
    cmw.w(f'CONFigure:WLAN:SIGNaling1:RFSettings:CHANnel {channel}')
    cmw.w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower {BOPOWER_DEFAULT}')
    cmw.w(f'CONFigure:WLAN:SIGNaling1:RFSettings:EPEPower {EPEPOWER_dBm}')
    eatt = eatt_of(channel)
    cmw.w(f'CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:OUTPut {eatt}')
    cmw.w(f'CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:INPut {eatt}')
    cmw.w(f'CONFigure:WLAN:SIGNaling1:CONNection:DFRControl ENAB,{dfrcontrol_rate}')

    cmw.w('SOURce:WLAN:SIGNaling1:STATe ON')
    t0 = time.time()
    while time.time() - t0 < 90:
        if cmw.q('SOURce:WLAN:SIGNaling1:STATe?') == 'ON': break
        time.sleep(2)

    # Trigger source persists across reboots — re-assert for safety
    cmw.w('TRIGger:WLAN:MEAS1:MEValuation:SOURce "WLAN Sig1: RXFrameTrigger"')


def setup_meas1(cmw, channel, mode):
    """Configure MEAS1 for the current mode/channel for Multi-Eval."""
    cmw.w('ABORt:WLAN:MEAS1:MEValuation')
    cmw.w('ROUTe:WLAN:MEAS1:SCENario:CSPath "WLAN Sig1"')
    cmw.w(f'CONFigure:WLAN:MEAS1:RFSettings:FREQuency {freq_of(channel)}')
    cmw.w(f'CONFigure:WLAN:MEAS1:RFSettings:ENPower1 {EPEPOWER_dBm}')
    cmw.w(f'CONFigure:WLAN:MEAS1:RFSettings:EATTenuation1 {eatt_of(channel)}')
    if mode == 'BSTD':
        cmw.w('CONFigure:WLAN:MEAS1:ISIGnal:STANdard DSSS')
    else:
        cmw.w('CONFigure:WLAN:MEAS1:ISIGnal:STANdard LOFDm')
    cmw.w('CONFigure:WLAN:MEAS1:ISIGnal:BWIDth BW20')
    cmw.w('CONFigure:WLAN:MEAS1:MEValuation:RESult:EVM ON')
    cmw.w('CONFigure:WLAN:MEAS1:MEValuation:RESult:SFLatness ON')
    cmw.w(f'CONFigure:WLAN:MEAS1:MEValuation:SCOunt:MODulation {MEV_SCOUNT}')
    cmw.w(f'CONFigure:WLAN:MEAS1:MEValuation:SCOunt:SFLatness {MEV_SCOUNT}')
    cmw.w('CONFigure:WLAN:MEAS1:MEValuation:REPetition SING')
    cmw.w('CONFigure:WLAN:MEAS1:MEValuation:TOUT 45')


def pg1_on(cmw, dut_ip, interval=PG1_TX_INTERVAL, size=PG1_TX_SIZE):
    cmw.w(f'CONFigure:WLAN:SIGNaling1:IPVFour:STATic:IPADdress:DESTination {dut_ip.replace(".",",")}')
    cmw.w('CONFigure:WLAN:SIGNaling1:PGEN1:PROTocol ICMP')
    cmw.w(f'CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,{interval},{size},PRAN,TID0')

def pg1_off(cmw):
    cmw.w(f'CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,{PG1_TX_INTERVAL},{PG1_TX_SIZE},PRAN,TID0')


def get_dut_ip(cmw):
    ip = cmw.q('SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?').strip('"')
    return None if ip in ('','0.0.0.0','NAV','TMO') else ip


def parse_mev_ofdm(fields):
    """Parse FETCh:...:MODulation:OFDM:AVERage? — 15 fields."""
    try:
        return {
            'reliab': fields[0],
            'rate':   fields[1],
            'nb':     int(float(fields[2])),
            'tx_dbm': float(fields[3]),
            'evm_rms':  float(fields[4]),
            'evm_pk':   float(fields[5]),
            'evm_data': float(fields[6]),
            'cf_err':   float(fields[7]),
            'iq_imb':   float(fields[8]),
            'phase_imb':float(fields[9]),
            'sclk_ppm': float(fields[11]) if fields[11] not in ('NCAP','INV') else None,
        }
    except Exception:
        return None

def parse_mev_dssss(fields):
    """Parse FETCh:...:MODulation:DSSS:AVERage? — different layout (extra format field)."""
    try:
        # 0:reliab, 1:rate, 2:format(LONG/SHORt), 3:Nb, 4:tx_pwr_avg, 5:tx_pwr_pk,
        # 6:evm_rms (positive dB), 7:cf_err, 8:iq, 9:phase, ...
        return {
            'reliab': fields[0],
            'rate':   fields[1],
            'nb':     int(float(fields[3])),
            'tx_dbm': float(fields[4]),
            'evm_rms':  float(fields[6]),
            'evm_pk':   float(fields[5]),       # peak power doubles as 'peak EVM' placeholder for DSSS
            'evm_data': None,
            'cf_err':   float(fields[7]),
            'iq_imb':   float(fields[8]),
            'phase_imb':float(fields[9]),
            'sclk_ppm': None,
        }
    except Exception:
        return None


def run_tx_cell(cmw, channel, mode, mcs=None):
    """One TX measurement: PG1 + Multi-Eval. Returns dict or None on fail."""
    setup_meas1(cmw, channel, mode)
    if mcs is not None:
        # Force HT MCS via DFDef for HT TX measurement
        cmw.w(f'CONFigure:WLAN:SIGNaling1:CONNection:DFRControl ENAB,MCS{mcs}')
        cmw.w(f'CONFigure:WLAN:SIGNaling1:CONNection:DFDef ENAB,HTM,BW20,MCS{mcs},LONG')
        fdef_label = f'HTM,BW20,MCS{mcs},LONG'
    else:
        fdef_label = 'auto'

    ip = get_dut_ip(cmw)
    if not ip:
        return None
    pg1_on(cmw, ip, interval=PG1_TX_INTERVAL, size=PG1_TX_SIZE)
    time.sleep(2)
    cmw.w('INITiate:WLAN:MEAS1:MEValuation')
    t0 = time.time()
    while time.time() - t0 < 35:
        time.sleep(0.5)
        if cmw.q('FETCh:WLAN:MEAS1:MEValuation:STATe?') == 'RDY': break

    # Fetch (DSSS vs OFDM path)
    if mode == 'BSTD':
        raw = cmw.q('FETCh:WLAN:MEAS1:MEValuation:MODulation:DSSS:AVERage?')
        parsed = parse_mev_dssss(raw.split(','))
    else:
        raw = cmw.q('FETCh:WLAN:MEAS1:MEValuation:MODulation:OFDM:AVERage?')
        parsed = parse_mev_ofdm(raw.split(','))

    sfl_raw = cmw.q('FETCh:WLAN:MEAS1:MEValuation:SFLatness:AVERage?').split(',')
    sfl_devs = []
    if sfl_raw and sfl_raw[0] == '0':
        for v in sfl_raw[1:6]:
            try: sfl_devs.append(float(v))
            except: sfl_devs.append(None)
    while len(sfl_devs) < 5: sfl_devs.append(None)

    drate = cmw.q('SENSe:WLAN:SIGNaling1:UESinfo:DRATe?')
    pg1_off(cmw)

    if not parsed:
        return {'ch': channel, 'mode': mode, 'fdef_target': fdef_label, 'reliab': raw.split(',')[0] if raw else '?',
                'drate_actual': drate}

    return {
        'ch': channel, 'mode': mode, 'fdef_target': fdef_label,
        'drate_actual': drate,
        **parsed,
        'sfl_d1': sfl_devs[0], 'sfl_d2': sfl_devs[1], 'sfl_d3': sfl_devs[2],
        'sfl_d4': sfl_devs[3], 'sfl_d5': sfl_devs[4],
    }


def per_at_level(cmw, bop_dbm, packets):
    """One PER measurement at a given BOPower. Returns (sent, missing, per_pct, reliab)."""
    cmw.w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower {bop_dbm}')
    time.sleep(0.6)
    cmw.w(f'CONFigure:WLAN:SIGNaling1:PER:PACKets {packets}')
    cmw.w('CONFigure:WLAN:SIGNaling1:PER:LIMit 100')
    cmw.w('INITiate:WLAN:SIGNaling1:PER')
    t0 = time.time()
    while time.time() - t0 < PER_TIMEOUT_S:
        time.sleep(0.4)
        st = cmw.q('FETCh:WLAN:SIGNaling1:PER:STATe?')
        if st == 'RDY': break
        if st == 'TMO' and (time.time() - t0) > 5: pass   # may be deadlock
    f = cmw.q('FETCh:WLAN:SIGNaling1:PER?').split(',')
    reliab = f[0] if f else '?'
    try:
        per = float(f[1]) if f[1] != 'INV' else None
        sent = int(float(f[2])) if f[2] != 'INV' else 0
        missing = int(float(f[3])) if f[3] != 'INV' else 0
    except Exception:
        return (0, 0, None, reliab)
    return (sent, missing, per, reliab)


def find_10pct_crossing(coarse_results):
    """Find BOPower range where PER crosses 10%. Return (low_dbm, high_dbm) or None."""
    # coarse_results = [(bop_dbm, per_pct), ...] sorted descending BOPower
    crossing = None
    for i in range(len(coarse_results)-1):
        b_hi, p_hi = coarse_results[i]
        b_lo, p_lo = coarse_results[i+1]
        if p_hi is None or p_lo is None: continue
        if p_hi < 10 and p_lo >= 10:
            return (b_lo, b_hi)        # 10% sits between b_lo (worse) and b_hi (better)
    return None


def interpolate_threshold(points, target_pct):
    """Linear interp BOPower at target PER% from sorted-descending (bop, per) list."""
    for i in range(len(points)-1):
        b1, p1 = points[i]
        b2, p2 = points[i+1]
        if p1 is None or p2 is None: continue
        if (p1 < target_pct <= p2) or (p1 >= target_pct > p2):
            if p1 == p2: return b1
            return b1 + (target_pct - p1) * (b2 - b1) / (p2 - p1)
    return None


def run_rx_cell(cmw, channel, mode, fdef, rx_coarse_writer, rx_fine_writer):
    """Full RX sweep for one cell. Coarse → fine → 10%/50% thresholds. Return summary dict."""
    cmw.w(f'CONFigure:WLAN:SIGNaling1:PER:FDEF {fdef}')

    # PG1 keep-alive in background (lowers PER baseline)
    ip = get_dut_ip(cmw)
    if not ip: return None
    pg1_on(cmw, ip, interval=PG1_KA_INTERVAL, size=PG1_KA_SIZE)
    time.sleep(2)

    # Coarse pass: -30 to -85 in 5 dB
    coarse = []
    for bop in range(-30, -86, -5):
        sent, missing, per, reliab = per_at_level(cmw, bop, PER_PACKETS_COARSE)
        rx_coarse_writer.writerow({'ch':channel,'mode':mode,'fdef':fdef,'phase':'coarse',
                                   'bop':bop,'sent':sent,'missing':missing,'per_pct':per,'reliab':reliab})
        coarse.append((bop, per))
        if per is not None and per >= 99: break

    # Determine 10% crossing window from coarse
    window = find_10pct_crossing(coarse)
    fine = []
    if window:
        b_lo, b_hi = window
        # extend ±2 dB
        lo = int(b_lo) - 2
        hi = int(b_hi) + 2
        for bop in range(hi, lo-1, -1):
            sent, missing, per, reliab = per_at_level(cmw, bop, PER_PACKETS_FINE)
            rx_fine_writer.writerow({'ch':channel,'mode':mode,'fdef':fdef,'phase':'fine',
                                     'bop':bop,'sent':sent,'missing':missing,'per_pct':per,'reliab':reliab})
            fine.append((bop, per))

    # Restore BOPower
    cmw.w(f'CONFigure:WLAN:SIGNaling1:RFSettings:BOPower {BOPOWER_DEFAULT}')
    pg1_off(cmw)

    sens_10 = interpolate_threshold(fine if fine else coarse, 10.0)
    sens_50 = interpolate_threshold(fine if fine else coarse, 50.0)

    return {
        'ch': channel, 'mode': mode, 'fdef': fdef,
        'sens_10pct_dBm': f'{sens_10:.2f}' if sens_10 is not None else '',
        'sens_50pct_dBm': f'{sens_50:.2f}' if sens_50 is not None else '',
        'coarse_n_points': len(coarse),
        'fine_n_points': len(fine),
    }


# ============================================================================
# Progress / checkpoint
# ============================================================================
class Progress:
    def __init__(self, path):
        self.path = path
        self.done = set()
        if os.path.exists(path):
            with open(path) as f:
                rd = csv.DictReader(f)
                for r in rd:
                    if r.get('status') == 'done':
                        key = f"{r.get('test_type')}|{r.get('ch')}|{r.get('mode')}|{r.get('extra','')}"
                        self.done.add(key)
        self.fp = open(path, 'a', newline='')
        self.writer = csv.DictWriter(self.fp,
            fieldnames=['ts','test_type','ch','mode','extra','status','note'])
        if os.stat(path).st_size == 0:
            self.writer.writeheader(); self.fp.flush()

    def is_done(self, test_type, ch, mode, extra=''):
        return f'{test_type}|{ch}|{mode}|{extra}' in self.done

    def log(self, test_type, ch, mode, extra='', status='done', note=''):
        self.writer.writerow({'ts': datetime.now().isoformat(timespec='seconds'),
                              'test_type': test_type, 'ch': ch, 'mode': mode,
                              'extra': extra, 'status': status, 'note': note})
        self.fp.flush()
        if status == 'done':
            self.done.add(f'{test_type}|{ch}|{mode}|{extra}')

    def close(self):
        self.fp.close()


# ============================================================================
# Main
# ============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase', choices=['A','B','all'], default='A')
    ap.add_argument('--resume', action='store_true')
    args = ap.parse_args()

    # Wipe TX CSV header if not resuming
    tx_fields = ['ch','mode','fdef_target','drate_actual','reliab','rate','nb',
                 'tx_dbm','evm_rms','evm_pk','evm_data','cf_err','iq_imb','phase_imb',
                 'sclk_ppm','sfl_d1','sfl_d2','sfl_d3','sfl_d4','sfl_d5']
    rx_coarse_fields = ['ch','mode','fdef','phase','bop','sent','missing','per_pct','reliab']
    rx_fine_fields   = rx_coarse_fields
    rx_summary_fields = ['ch','mode','fdef','sens_10pct_dBm','sens_50pct_dBm',
                         'coarse_n_points','fine_n_points']

    if not args.resume:
        # Wipe + write headers
        for path, fields in [(TX_CSV, tx_fields),
                             (RX_COARSE_CSV, rx_coarse_fields),
                             (RX_FINE_CSV, rx_fine_fields),
                             (RX_SUMMARY_CSV, rx_summary_fields)]:
            with open(path,'w',newline='') as f:
                csv.DictWriter(f, fieldnames=fields).writeheader()
        if os.path.exists(PROGRESS_CSV):
            os.remove(PROGRESS_CSV)
    else:
        # Resume: ensure headers exist even if a prior run truncated them
        for path, fields in [(TX_CSV, tx_fields),
                             (RX_COARSE_CSV, rx_coarse_fields),
                             (RX_FINE_CSV, rx_fine_fields),
                             (RX_SUMMARY_CSV, rx_summary_fields)]:
            if not os.path.exists(path):
                with open(path,'w',newline='') as f:
                    csv.DictWriter(f, fieldnames=fields).writeheader()
            else:
                with open(path) as f: first = f.readline().strip()
                expected = ','.join(fields)
                if first != expected:
                    body = open(path).read()
                    with open(path,'w',newline='') as f:
                        f.write(expected + '\n')
                        f.write(body)

    # Always append (header is already in file)
    tx_fp        = open(TX_CSV,        'a', newline='')
    rx_coarse_fp = open(RX_COARSE_CSV, 'a', newline='')
    rx_fine_fp   = open(RX_FINE_CSV,   'a', newline='')
    rx_summary_fp= open(RX_SUMMARY_CSV,'a', newline='')
    tx_w   = csv.DictWriter(tx_fp,        fieldnames=tx_fields,         extrasaction='ignore')
    rxc_w  = csv.DictWriter(rx_coarse_fp, fieldnames=rx_coarse_fields,  extrasaction='ignore')
    rxf_w  = csv.DictWriter(rx_fine_fp,   fieldnames=rx_fine_fields,    extrasaction='ignore')
    rxs_w  = csv.DictWriter(rx_summary_fp,fieldnames=rx_summary_fields, extrasaction='ignore')

    progress = Progress(PROGRESS_CSV)

    cmw = CMW()

    def with_recovery(test_fn, *args, **kw):
        """Wrap a test step; if SCPI deadlocks, reboot CMW and retry once."""
        try:
            return test_fn(*args, **kw)
        except pyvisa.errors.VisaIOError:
            pass
        if not cmw.health():
            if not cmw.reboot_recover():
                return None
            try:
                return test_fn(*args, **kw)
            except Exception:
                return None
        return None

    do_tx = args.phase in ('A','all')
    do_rx_sample = args.phase == 'A'
    do_rx_full   = args.phase in ('B','all')

    for std, band, nht_rates, mcs_list in MODES:
        channels = CHANNELS_24G if band == '2.4G' else CHANNELS_5G
        if not channels: continue

        print(f'\n========== STANdard {std} ({band}) ==========', flush=True)

        for ch_idx, ch in enumerate(channels):
            print(f'\n  -- ch{ch} --', flush=True)
            # Setup once per channel
            try:
                if ch_idx == 0:
                    # First channel of this mode: full STANdard switch
                    setup_mode_and_channel(cmw, std, ch)
                else:
                    # Same mode: just change channel + DFRControl reset
                    cmw.w(f'CONFigure:WLAN:SIGNaling1:RFSettings:CHANnel {ch}')
                    cmw.w(f'CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:OUTPut {eatt_of(ch)}')
                    cmw.w(f'CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:INPut {eatt_of(ch)}')
            except Exception as e:
                print(f'    setup err: {e}', flush=True)
                if not cmw.health():
                    if not cmw.reboot_recover():
                        print('    reboot failed, abort'); break
                    setup_mode_and_channel(cmw, std, ch)

            # DUT reconnect (with retry for DFS handling)
            ip = None
            for attempt in range(3):
                dut_reconnect(ch)
                time.sleep(2)
                ip = get_dut_ip(cmw)
                if ip: break
            if not ip:
                tag = 'SKIP_REGDOMAIN' if ch in DFS_CHANNELS else 'NO_DUT'
                print(f'    {tag} — skip all tests on ch{ch}', flush=True)
                progress.log('TX', ch, std, status='skip', note=tag)
                # Also log RX skip for each rate
                for r in nht_rates: progress.log('RX', ch, std, extra=r, status='skip', note=tag)
                for m in mcs_list:  progress.log('RX', ch, std, extra=f'MCS{m}', status='skip', note=tag)
                continue
            print(f'    DUT IP={ip}', flush=True)

            # ---------- TX cell ----------
            if do_tx and not progress.is_done('TX', ch, std):
                print(f'    TX (NHT auto-rate) ...', end='', flush=True)
                row = run_tx_cell(cmw, ch, std, mcs=None)
                if row and row.get('tx_dbm') is not None:
                    tx_w.writerow(row); tx_fp.flush()
                    print(f' TX={row.get("tx_dbm","?")!s} EVM={row.get("evm_rms","?")!s} '
                          f'DRATe={row.get("drate_actual","?")}', flush=True)
                    progress.log('TX', ch, std, status='done')
                else:
                    reliab = row.get('reliab','?') if row else '?'
                    print(f' FAIL (reliab={reliab})', flush=True)
                    progress.log('TX', ch, std, status='fail', note=f'reliab={reliab}')

            # HT MCS TX (forced rate)
            if do_tx:
                for mcs in mcs_list:
                    if progress.is_done('TX', ch, std, extra=f'MCS{mcs}'): continue
                    print(f'    TX MCS{mcs} (forced) ...', end='', flush=True)
                    row = run_tx_cell(cmw, ch, std, mcs=mcs)
                    if row and row.get('tx_dbm') is not None:
                        tx_w.writerow(row); tx_fp.flush()
                        print(f' TX={row.get("tx_dbm","?")!s} EVM={row.get("evm_rms","?")!s} '
                              f'DRATe={row.get("drate_actual","?")}', flush=True)
                        progress.log('TX', ch, std, extra=f'MCS{mcs}', status='done')
                    else:
                        reliab = row.get('reliab','?') if row else '?'
                        print(f' FAIL (reliab={reliab})', flush=True)
                        progress.log('TX', ch, std, extra=f'MCS{mcs}', status='fail',
                                     note=f'reliab={reliab}')

            # ---------- RX cells ----------
            run_rx_this_ch = (do_rx_full or
                              (do_rx_sample and
                               ((band == '2.4G' and ch in PHASE_A_RX_24G) or
                                (band == '5G' and ch in PHASE_A_RX_5G))))
            if not run_rx_this_ch:
                continue

            # Reset DFRControl to NHT (HT TX may have left it on MCSn — restore for RX sweep)
            cmw.w('CONFigure:WLAN:SIGNaling1:CONNection:DFRControl ENAB,Q6M34')
            cmw.w('CONFigure:WLAN:SIGNaling1:CONNection:DFDef ENAB,NHT,BW20,Q6M34,LONG')

            all_rates = list(nht_rates) + [f'MCS{m}' for m in mcs_list]
            for rate in all_rates:
                if progress.is_done('RX', ch, std, extra=rate): continue
                fdef = fdef_for(std, rate)
                print(f'    RX {rate} ({fdef}) sweep ...', flush=True)
                t0 = time.time()
                summary = run_rx_cell(cmw, ch, std, fdef, rxc_w, rxf_w)
                rx_coarse_fp.flush(); rx_fine_fp.flush()
                if summary:
                    rxs_w.writerow(summary); rx_summary_fp.flush()
                    print(f'      → 10%={summary["sens_10pct_dBm"]} dBm  50%={summary["sens_50pct_dBm"]} dBm '
                          f'({time.time()-t0:.0f}s)', flush=True)
                    progress.log('RX', ch, std, extra=rate, status='done')
                else:
                    print(f'      FAIL', flush=True)
                    progress.log('RX', ch, std, extra=rate, status='fail')

    # Final restore
    print('\n========== Restore safe state (GSTD ch1) ==========', flush=True)
    setup_mode_and_channel(cmw, 'GSTD', 1)

    tx_fp.close(); rx_coarse_fp.close(); rx_fine_fp.close(); rx_summary_fp.close()
    progress.close()

    print(f'\nOutput files in {OUT_DIR}:', flush=True)
    print(f'  {TX_CSV}')
    print(f'  {RX_COARSE_CSV}')
    print(f'  {RX_FINE_CSV}')
    print(f'  {RX_SUMMARY_CSV}')
    print(f'  {PROGRESS_CSV}')

if __name__ == '__main__':
    main()
