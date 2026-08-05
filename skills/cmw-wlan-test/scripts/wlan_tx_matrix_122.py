#!/usr/bin/env python3
"""CMW-500 .122 WLAN TX power MATRIX for Ai-Thinker 'aiio' WJAP module (COM9@921600).
Channels x rates; band auto-derived (ch>=36 -> 5GHz). CCK skipped on 5GHz (11b is 2.4GHz-only).
Writes incremental CSV so progress is monitorable / resumable.

Usage: python3 wlan_tx_matrix_122.py "1,6,13,36,64,149,165"
"""
import os, socket, time, base64, sys, csv
for k in ("http_proxy","https_proxy","HTTP_PROXY","HTTPS_PROXY","all_proxy","ALL_PROXY","PROXY"):
    os.environ.pop(k, None)
import winrm

HOST="192.0.2.10"; COM=os.environ.get("DUT_COM","COM9"); BAUD=int(os.environ.get("DUT_BAUD","921600"))
JOIN_CMD=os.environ.get("JOIN_CMD","AT+WJAP=CMW-AP,12345678")
JOIN_SETTLE=int(os.environ.get("JOIN_SETTLE_MS","3500"))
CSVP=os.environ.get("MATRIX_CSV","/home/zxf/keysight-test/wlan_tx_matrix_122.csv")
RATES=["CCK11","OFDM54","MCS7"]
# rate -> (meas ISIGnal:STANdard, fetch node, TX idx, want-rate substr, SCOunt, DFRControl code)
RI={'CCK11':('DSSS','DSSS',4,'CCK11',20,'C11M'),
    'OFDM54':('LOFDm','OFDM',3,'Q6M54',20,'Q6M34'),
    'MCS7':('HTOF','OFDM',3,'Q6R56',8,'MCS7')}
def is5g(ch): return ch>=36
def std_for(ch,rate):
    if is5g(ch): return {'CCK11':None,'OFDM54':'ASTD','MCS7':'ANST'}[rate]
    return {'CCK11':'BSTD','OFDM54':'GSTD','MCS7':'GNST'}[rate]
def freq_of(ch): return (5000000000+ch*5000000) if is5g(ch) else (2407000000+ch*5000000)
def band_of(ch): return "B5G" if is5g(ch) else "B24G"

def mk(): s=socket.create_connection((HOST,5025),timeout=20); s.settimeout(20); return s
class C:
    def __init__(self): self.s=mk()
    def _rl(self):
        b=b""
        while b"\n" not in b:
            ch=self.s.recv(65536)
            if not ch: break
            b+=ch
        return b.decode("latin1","replace").strip()
    def q(self,c):
        try:
            self.s.sendall((c+"\n").encode()); return self._rl()
        except Exception:
            try: self.s.close()
            except Exception: pass
            time.sleep(0.5); self.s=mk(); time.sleep(0.3)
            self.s.sendall((c+"\n").encode()); return self._rl()
    def w(self,c):
        try: self.s.sendall((c+"\n").encode()); time.sleep(0.1)
        except Exception:
            try: self.s.close()
            except Exception: pass
            time.sleep(0.5); self.s=mk(); time.sleep(0.3)
            self.s.sendall((c+"\n").encode()); time.sleep(0.1)
c=C()
sess=winrm.Session("http://%s:5985/wsman"%HOST, auth=("<CMW_WINRM_USER>","<CMW_WINRM_PASS>"), transport="ntlm",
                   read_timeout_sec=60, operation_timeout_sec=55)
def wjap_join():
    ps=r'''
$ErrorActionPreference="Stop"
try {{
 $r=New-Object System.IO.Ports.SerialPort '{com}',{baud},'None',8,'One'
 $r.DtrEnable=$true;$r.RtsEnable=$true;$r.Open();Start-Sleep -Milliseconds 500;$r.Close();Start-Sleep -Milliseconds 400
 $sp=New-Object System.IO.Ports.SerialPort '{com}',{baud},'None',8,'One'
 $sp.ReadTimeout=600;$sp.WriteTimeout=600;$sp.NewLine=[char]13+[char]10
 $sp.DtrEnable=$false;$sp.RtsEnable=$false;$sp.Open();Start-Sleep -Milliseconds {settle};$sp.DiscardInBuffer()
 $sp.WriteLine([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{w}')))
 $t=[Diagnostics.Stopwatch]::StartNew();$b=New-Object Text.StringBuilder
 while($t.ElapsedMilliseconds -lt 18000){{ if($sp.BytesToRead -gt 0){{[void]$b.Append($sp.ReadExisting())}}; if($b.ToString() -match 'got ip|GOT IP|WJAP:1'){{break}}; Start-Sleep -Milliseconds 100 }}
 $sp.Close();$b.ToString()
}} catch {{ "ERR="+$_.Exception.Message; try{{$sp.Close()}}catch{{}} }}
'''.format(com=COM,baud=BAUD,settle=JOIN_SETTLE,w=base64.b64encode(JOIN_CMD.encode()).decode())
    return (sess.run_ps(ps).std_out or b"").decode("cp936","replace")

def setup(ch, std, dfr):
    c.w("SOURce:WLAN:SIGNaling1:STATe OFF")
    t0=time.time()
    while time.time()-t0<20:
        if c.q("SOURce:WLAN:SIGNaling1:STATe?")=="OFF": break
        time.sleep(1.5)
    c.w("*CLS")
    c.w("ROUTe:WLAN:SIGNaling1:SCENario:SCELl RF2C,RX1,RF2C,TX1")
    c.w("CONFigure:WLAN:SIGNaling1:CONNection:OMODe AP")
    c.w("CONFigure:WLAN:SIGNaling1:CONNection:SSID 'CMW-AP'")
    c.w('CONFigure:WLAN:SIGNaling1:CONNection:SECurity:PASSphrase W2P,"12345678"')
    c.w("CONFigure:WLAN:SIGNaling1:CONNection:STANdard %s"%std)
    c.w("CONFigure:WLAN:SIGNaling1:RFSettings:CHANnel %d"%ch)
    if dfr.startswith("MCS"):
        # force HT MCS7: advertise only MCS7 (+ OFDM basics for association)
        c.w("CONFigure:WLAN:SIGNaling1:CONNection:SRATes ENAB")
        c.w("CONFigure:WLAN:SIGNaling1:CONNection:SRATes:OFDMconf MAND,OPT,MAND,OPT,MAND,OPT,OPT,OPT")
        c.w("CONFigure:WLAN:SIGNaling1:CONNection:SRATes:OMCSconf NOTS,NOTS,NOTS,NOTS,NOTS,NOTS,NOTS,SUPP")
    else:
        c.w("CONFigure:WLAN:SIGNaling1:CONNection:SRATes DIS")
    c.w("CONFigure:WLAN:SIGNaling1:CONNection:DFRControl ENAB,%s"%dfr)
    c.w("CONFigure:WLAN:SIGNaling1:RFSettings:BOPower -30")   # clamps to band max if -222
    c.w("CONFigure:WLAN:SIGNaling1:RFSettings:EPEPower 30")
    c.w("CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:OUTPut 1")
    c.w("CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:INPut 1")
    c.w("SOURce:WLAN:SIGNaling1:STATe ON")
    t0=time.time()
    while time.time()-t0<25:
        if c.q("SOURce:WLAN:SIGNaling1:STATe?")=="ON": break
        time.sleep(1.5)

def pg1_on(dut):
    c.w("CONFigure:WLAN:SIGNaling1:IPVFour:STATic:IPADdress:DESTination %s"%dut.replace(".",","))
    c.w("CONFigure:WLAN:SIGNaling1:PGEN1:PROTocol ICMP")
    c.w("CONFigure:WLAN:SIGNaling1:PGEN1:IPVersion IV4")
    c.w("CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,4,1472,PRAN,TID0")

def meas_setup(ch, mstd, scount):
    c.w("ABORt:WLAN:MEAS1:MEValuation"); time.sleep(0.3)
    c.w('ROUTe:WLAN:MEAS1:SCENario:CSPath "WLAN Sig1"')
    c.w("CONFigure:WLAN:MEAS1:RFSettings:FREQuency %d"%freq_of(ch))
    c.w("CONFigure:WLAN:MEAS1:RFSettings:FREQuency:BAND %s"%band_of(ch))
    c.w("CONFigure:WLAN:MEAS1:RFSettings:ENPower1 30")
    c.w("CONFigure:WLAN:MEAS1:ISIGnal:STANdard %s"%mstd)
    c.w("CONFigure:WLAN:MEAS1:ISIGnal:BWIDth BW20")
    c.w("CONFigure:WLAN:MEAS1:MEValuation:REPetition SING")
    c.w("CONFigure:WLAN:MEAS1:MEValuation:SCOunt:MODulation %d"%scount)
    c.w("CONFigure:WLAN:MEAS1:MEValuation:TOUT 15")
    c.w('TRIGger:WLAN:MEAS1:MEValuation:SOURce "WLAN Sig1: RXFrameTrigger"')

def shot(fetch):
    c.w("ABORt:WLAN:MEAS1:MEValuation"); c.w("INITiate:WLAN:MEAS1:MEValuation")
    t0=time.time()
    while time.time()-t0<16:
        if c.q("FETCh:WLAN:MEAS1:MEValuation:STATe?").startswith("RDY"): break
        time.sleep(0.4)
    return c.q("FETCh:WLAN:MEAS1:MEValuation:MODulation:%s:AVERage?"%fetch).split(",")

def measure(ch, rate):
    std=std_for(ch,rate)
    if std is None: return None,"N/A(5GHz-no-CCK)"
    mstd,fetch,idx,want,scount,dfr=RI[rate]
    seen=set()
    for rnd in range(3):
        print("  [ch%d %s] round%d..."%(ch,rate,rnd+1),flush=True)
        setup(ch,std,dfr)
        log=wjap_join()
        joined=any(x in log.lower() for x in ("got ip","wifi connected","wjap:1"))
        print("    joined=%s DRATe=%s"%(joined,c.q("SENSe:WLAN:SIGNaling1:UESinfo:DRATe?")),flush=True)
        if not joined: continue
        dut=(c.q("SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?") or "").strip('"')
        if dut in ("","0.0.0.0","NAV"): dut="192.168.48.129"
        pg1_on(dut); time.sleep(3)
        meas_setup(ch,mstd,scount)
        vals=[]; seen=set(); nshot=16 if scount<=1 else 12
        for i in range(nshot):
            f=shot(fetch); rr=f[0] if f else "?"; rate_c=f[1] if len(f)>1 else "?"
            ok=rr=="0" and len(f)>idx and f[idx] not in ("NCAP","INV","NAV")
            if ok: seen.add(rate_c)
            if ok and want in rate_c:
                vals.append(float(f[idx]))
                if len(vals)>=3: break
            time.sleep(0.25)
        print("    seen=%s vals=%s"%(sorted(seen),[round(v,2) for v in vals]),flush=True)
        if len(vals)>=3:
            return sum(vals)/len(vals),"OK"
    return None,"FAIL(seen=%s)"%sorted(seen)

def main():
    chans=[int(x) for x in (sys.argv[1] if len(sys.argv)>1 else "1,6,13,36,64,149,165").split(",")]
    # fresh CSV
    with open(CSVP,"w",newline="") as fp:
        csv.writer(fp).writerow(["channel","band","rate","tx_dbm","status"])
    print("IDN:",c.q("*IDN?"),flush=True)
    for ch in chans:
        for rate in RATES:
            print("\n===== ch%d %s ====="%(ch,rate),flush=True)
            tx,st=measure(ch,rate)
            with open(CSVP,"a",newline="") as fp:
                csv.writer(fp).writerow([ch,band_of(ch),rate,("%.2f"%tx if tx is not None else ""),st])
            print(">>> ch%d %s: %s %s"%(ch,rate,("%.2f dBm"%tx if tx is not None else "-"),st),flush=True)
    c.w("CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,4,1472,PRAN,TID0")
    print("\nDONE. CSV:",CSVP,flush=True)

if __name__=="__main__": main()
