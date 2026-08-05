"""Consolidate wlan_full_compliance_*.csv into a markdown deliverable.

Reads:
  wlan_full_compliance_tx.csv
  wlan_full_compliance_rx_summary.csv
  wlan_full_compliance_progress.csv

Writes:
  WLAN_FULL_COMPLIANCE_REPORT.md

Tables include:
  - DUT / setup header
  - TX summary per (mode, channel) with EVM/CF/SFL
  - RX 10% / 50% PER thresholds per (mode, channel, rate)
  - SKIP_REGDOMAIN gap section
  - Verification checklist (out of plan)
"""
import csv, os
from collections import defaultdict
from datetime import datetime

OUT_DIR = '/home/zxf/keysight-test'
TX_CSV         = f'{OUT_DIR}/wlan_full_compliance_tx.csv'
TX_RETRY_CSV   = f'{OUT_DIR}/wlan_full_compliance_tx_retry.csv'   # appended after retry
RX_SUMMARY_CSV = f'{OUT_DIR}/wlan_full_compliance_rx_summary.csv'
PROGRESS_CSV   = f'{OUT_DIR}/wlan_full_compliance_progress.csv'
REPORT_MD      = f'{OUT_DIR}/WLAN_FULL_COMPLIANCE_REPORT.md'

# ------------------------------------------------------------------
def load_csv(path):
    if not os.path.exists(path): return []
    with open(path) as f:
        return list(csv.DictReader(f))

def fmt(v, digits=2):
    if v in (None, '', 'NCAP', 'INV', 'TMO'): return '—'
    try:    return f'{float(v):.{digits}f}'
    except: return str(v)

def fmt_int(v):
    if v in (None, '', 'NCAP', 'INV'): return '—'
    try:    return str(int(float(v)))
    except: return str(v)

# ------------------------------------------------------------------
def section_header(title, lvl=2):
    return f'\n{"#"*lvl} {title}\n'

# ------------------------------------------------------------------
def build_tx_table(rows):
    """One markdown table per (band, mode) showing per-channel TX metrics."""
    by_mode = defaultdict(list)
    for r in rows:
        by_mode[r['mode']].append(r)

    out = []
    mode_order = ['BSTD','GSTD','GNST','ASTD','ANST']
    for mode in mode_order:
        if mode not in by_mode: continue
        out.append(f'\n### TX — {mode}\n')
        out.append('| CH | fdef_target | DRATe actual | TX dBm | EVM rms dB | EVM peak dB | CF err Hz | IQ imb dB | Phase imb deg | Sym clk ppm | SFL deviations dB |')
        out.append('|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|')
        rows_sorted = sorted(by_mode[mode], key=lambda r: (int(r['ch']), r['fdef_target']))
        for r in rows_sorted:
            sfl = ', '.join(fmt(r.get(f'sfl_d{i}',''), 2) for i in range(1,6))
            out.append(f'| {r["ch"]} | {r["fdef_target"]} | {r.get("drate_actual","")} | '
                       f'{fmt(r.get("tx_dbm",""))} | {fmt(r.get("evm_rms",""))} | {fmt(r.get("evm_pk",""))} | '
                       f'{fmt(r.get("cf_err",""), 1)} | {fmt(r.get("iq_imb",""))} | {fmt(r.get("phase_imb",""))} | '
                       f'{fmt(r.get("sclk_ppm",""), 3)} | {sfl} |')
    return '\n'.join(out)

# ------------------------------------------------------------------
def build_rx_table(rows):
    by_mode = defaultdict(list)
    for r in rows:
        by_mode[r['mode']].append(r)
    out = []
    for mode in ['BSTD','GSTD','GNST','ASTD','ANST']:
        if mode not in by_mode: continue
        out.append(f'\n### RX sensitivity — {mode}\n')
        out.append('| CH | FDEF | 10% PER dBm | 50% PER dBm | coarse pts | fine pts |')
        out.append('|---:|---|---:|---:|---:|---:|')
        rs = sorted(by_mode[mode], key=lambda r: (int(r['ch']), r['fdef']))
        for r in rs:
            out.append(f'| {r["ch"]} | {r["fdef"]} | {r["sens_10pct_dBm"] or "—"} | {r["sens_50pct_dBm"] or "—"} | '
                       f'{r.get("coarse_n_points","")} | {r.get("fine_n_points","")} |')
    return '\n'.join(out)

# ------------------------------------------------------------------
def build_progress_summary(rows, recovered_keys):
    """recovered_keys: set of (ch,mode,extra) that retry CSV proves succeeded."""
    by_status = defaultdict(int)
    skipped = []
    failed = []
    recovered = 0
    for r in rows:
        if r['status'] == 'fail':
            key = (str(r.get('ch','')), r.get('mode',''), r.get('extra',''))
            if key in recovered_keys:
                recovered += 1
                by_status['recovered'] += 1
                continue
        by_status[r['status']] += 1
        if r['status'] == 'skip':
            skipped.append(r)
        elif r['status'] == 'fail':
            failed.append(r)

    out = [f'\n**Total**: {sum(by_status.values())} measurements\n']
    for s,c in sorted(by_status.items()):
        out.append(f'- {s}: **{c}**')
    if recovered:
        out.append(f'\n*Note*: **{recovered}** cells originally marked `fail` were recovered '
                   f'via `wlan_tx_retry.py` (fresh PyVISA session + 5 s PG1 settle). '
                   f'Their data is included in the TX table above.')
    if skipped:
        out.append('\n**Skipped cells (DFS regdomain or DUT-unreachable):**\n')
        out.append('| CH | mode | extra | note |')
        out.append('|---:|---|---|---|')
        for r in skipped:
            out.append(f'| {r["ch"]} | {r["mode"]} | {r.get("extra","")} | {r.get("note","")} |')
    if failed:
        out.append('\n**Failed cells (still unresolved — need manual investigation):**\n')
        out.append('| CH | mode | extra | note |')
        out.append('|---:|---|---|---|')
        for r in failed:
            out.append(f'| {r["ch"]} | {r["mode"]} | {r.get("extra","")} | {r.get("note","")} |')
    return '\n'.join(out)

# ------------------------------------------------------------------
def main():
    # Load TX rows from main file + retry file (retry rows take precedence)
    tx_rows = load_csv(TX_CSV)
    retry_rows = load_csv(TX_RETRY_CSV)
    # Build (ch, mode, fdef_target) → row map. Retry wins.
    by_key = {}
    for r in tx_rows:
        # Skip rows that are clearly invalid (empty tx_dbm)
        if r.get('tx_dbm','').strip() in ('',):
            continue
        by_key[(r.get('ch',''), r.get('mode',''), r.get('fdef_target',''))] = r
    for r in retry_rows:
        if r.get('tx_dbm','').strip() in ('',):
            continue
        by_key[(r.get('ch',''), r.get('mode',''), r.get('fdef_target',''))] = r
    tx_rows = list(by_key.values())

    rx_rows = load_csv(RX_SUMMARY_CSV)
    prog_rows = load_csv(PROGRESS_CSV)

    # Build set of (ch,mode,extra) successfully recovered by retry. retry CSV
    # uses fdef_target → translate back to the 'extra' field used in progress.
    # extra is the MCSn suffix for GNST/ANST MCS cells, empty otherwise.
    recovered_keys = set()
    for r in retry_rows:
        if r.get('tx_dbm','').strip() == '':
            continue
        ch = r.get('ch','')
        mode = r.get('mode','')
        ft = r.get('fdef_target','')
        if 'MCS' in ft:
            # e.g. HTM,BW20,MCS4,LONG → extra = MCS4
            extra = ft.split(',')[2] if ',' in ft else ''
        else:
            extra = ''
        recovered_keys.add((ch, mode, extra))

    md = []
    md.append('# RTL8711DAN (AmebaDplus) WLAN Full Compliance Report\n')
    md.append(f'Generated: {datetime.now().isoformat(timespec="seconds")}\n')
    md.append('CMW-500 FW 3.7.40, WLAN Sig/Meas V3.7.32.\n')

    md.append(section_header('Setup', 2))
    md.append('| Item | Value |')
    md.append('|---|---|')
    md.append('| DUT | Realtek RTL8711DAN (AmebaDplus), MAC `AA:BB:CC:DD:EE:FF` |')
    md.append('| CMW-AP SSID | CMW-AP (open security) |')
    md.append('| RF path | CMW RF2 COM ↔ DUT antenna, direct coax ~1 dB |')
    md.append('| EATT (2.4 / 5 GHz) | 1 dB / 1 dB |')
    md.append('| BOPower default | −30 dBm |')
    md.append('| EPEPower | +30 dBm |')
    md.append('| Multi-Eval SCount | 40 bursts |')
    md.append('| PER packets | 100 (coarse) / 200 (fine) |')
    md.append('| PER PG1 keep-alive | 50 TU / 200 B |')
    md.append('')
    md.append('Channel × Standard pairing rule (enforced):')
    md.append('- 2.4 GHz {1, 3, 6, 9, 11}: BSTD / GSTD / GNST')
    md.append('- 5 GHz {36, 40, 52, 64, 100, 132, 149, 165}: ASTD / ANST')

    md.append(section_header('TX Measurements', 2))
    md.append(f'Total TX runs: **{len(tx_rows)}**')
    md.append(build_tx_table(tx_rows))

    md.append(section_header('RX Sensitivity', 2))
    md.append(f'Total RX cells with thresholds: **{len(rx_rows)}**')
    md.append(build_rx_table(rx_rows))

    md.append(section_header('Coverage / Status', 2))
    md.append(build_progress_summary(prog_rows, recovered_keys))

    md.append(section_header('Known Gaps (route to N9020A)', 2))
    md.append('| Test | Reason | Alternative |')
    md.append('|---|---|---|')
    md.append('| Spectral Emission Mask (TSMask) | CMW FW 3.7.40 CSP NCAP | N9020A `:HCOPY:SDUMP` or `:CALC:MARK1:MAX` |')
    md.append('| Power vs Time edges (PVTime) | CMW FW bug | N9020A `:CALC:MARK:T1/T2` |')
    md.append('| Spectrum density (SPECtrum) | Same as TSMask | N9020A noise marker |')
    md.append('| BW40 / BW80 / BW160 | CMW license `-203` + DUT NSS1/BW20 | n/a (DUT does not support) |')
    md.append('| HE/VHT modes | DUT does not support (NCAP) | n/a |')

    md.append(section_header('Verification (manual)', 2))
    md.append('- [ ] All 70 TX runs have non-empty `tx_dbm` and reliab=0')
    md.append('- [ ] EVM RMS ≤ −25 dB for 11g/n 54M; CCK EVM ≤ 17%')
    md.append('- [ ] CF Error |·| ≤ 25 ppm')
    md.append('- [ ] 5 GHz TX 2-3 dB below 2.4 GHz (known DUT trait)')
    md.append('- [ ] 6 Mbps RX 10-15 dB better sensitivity than 54 Mbps (per channel)')
    md.append('- [ ] CCK rates RX 10 dB better than OFDM 54M (per channel)')
    md.append('- [ ] DFS channels (52/64/100/132) status: SKIP_REGDOMAIN if assoc fails')

    out = '\n'.join(md) + '\n'
    with open(REPORT_MD, 'w') as f: f.write(out)
    print(f'Wrote {REPORT_MD} ({len(out)} chars)')

if __name__ == '__main__':
    main()
