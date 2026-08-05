#!/usr/bin/env python3
"""CMW-500 .122 (FW 3.7.40) WLAN TX power for an Ai-Thinker 'aiio' WJAP module on COM9@921600.
Ports the .125 3-rate recipe (CCK11/OFDM54/MCS7) to .122: DFRControl + SRATes rate-set forcing
(NO MFRControl on this FW). Serial join via AT+WJAP=CMW-AP,12345678.

Usage: python3 wlan_tx_wjap_122.py <cells>   e.g. "1:CCK11"  or  "1:CCK11,1:OFDM54,1:MCS7"
"""
import os, socket, time, base64, sys
for k in ("http_proxy","https_proxy","HTTP_PROXY","HTTPS_PROXY","all_proxy","ALL_PROXY","PROXY"):
    os.environ.pop(k, None)
import winrm

HOST="192.0.2.10"; COM="COM9"; BAUD=921600
RELIAB={'0':'OK','3':'TrigTMO','6':'NoSignal','8':'Overdrive','26':'ResConflict'}

# rate-label -> (Sig STANdard, meas ISIGnal:STANdard, fetch node, TX-field idx, want-rate substr, SCOunt, [rate-force SCPI])
SPEC={
 'CCK11': ('BSTD','DSSS','DSSS',4,'CCK11',20,[
     'CONFigure:WLAN:SIGNaling1:CONNection:SRATes DIS',
     'CONFigure:WLAN:SIGNaling1:CONNection:DFRControl ENAB,C11M']),
 'OFDM54':('GSTD','LOFDm','OFDM',3,'Q6M54',20,[
     'CONFigure:WLAN:SIGNaling1:CONNection:SRATes DIS',
     'CONFigure:WLAN:SIGNaling1:CONNection:DFRControl ENAB,Q6M34']),
 'MCS7':  ('GNST','HTOF','OFDM',3,'Q6R56',8,[
     'CONFigure:WLAN:SIGNaling1:CONNection:SRATes DIS',
     'CONFigure:WLAN:SIGNaling1:CONNection:DFRControl ENAB,MCS7']),
}
def freq(ch): return 2407000000+ch*5000000

# ---------- SCPI ----------
def mk(): s=socket.create_connection((HOST,5025),timeout=20); s.settimeout(20); return s
class C:
    def __init__(self): self.s=mk()
    def q(self,c):
        self.s.sendall((c+"\n").encode())
        b=b""
        while b"\n" not in b:
            ch=self.s.recv(4096)
            if not ch: break
            b+=ch
        return b.decode("latin1","replace").strip()
    def w(self,c): self.s.sendall((c+"\n").encode()); time.sleep(0.1)
    def werr(self,c):
        self.w(c); e=self.q("SYSTem:ERRor?")
        if not e.startswith("0,"): print("      !SCPI %s -> %s"%(c.split(':')[-1][:24], e))
        return e
c=C()

# ---------- serial (WinRM ntlm, base64) ----------
sess=winrm.Session("http://%s:5985/wsman"%HOST, auth=("<CMW_WINRM_USER>","<CMW_WINRM_PASS>"), transport="ntlm",
                   read_timeout_sec=70, operation_timeout_sec=65)
def b64(x): return base64.b64encode(x.encode()).decode()
def wjap_join():
    """DTR/RTS hard reset, AT+WJAP, wait for connect; return module log tail."""
    ps=r'''
$ErrorActionPreference="Stop"
try {{
 $r=New-Object System.IO.Ports.SerialPort '{com}',{baud},'None',8,'One'
 $r.DtrEnable=$true;$r.RtsEnable=$true;$r.Open();Start-Sleep -Milliseconds 500;$r.Close();Start-Sleep -Milliseconds 400
 $sp=New-Object System.IO.Ports.SerialPort '{com}',{baud},'None',8,'One'
 $sp.ReadTimeout=600;$sp.WriteTimeout=600;$sp.NewLine=[char]13+[char]10
 $sp.DtrEnable=$false;$sp.RtsEnable=$false;$sp.Open();Start-Sleep -Milliseconds 3500;$sp.DiscardInBuffer()
 $sp.WriteLine([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{wjap}')))
 $t=[Diagnostics.Stopwatch]::StartNew();$b=New-Object Text.StringBuilder
 while($t.ElapsedMilliseconds -lt 15000){{ if($sp.BytesToRead -gt 0){{[void]$b.Append($sp.ReadExisting())}}; if($b.ToString() -match 'GOT IP|got ip|WJAP:1'){{break}}; Start-Sleep -Milliseconds 100 }}
 $sp.Close();$b.ToString()
}} catch {{ "ERR="+$_.Exception.Message; try{{$sp.Close()}}catch{{}} }}
'''.format(com=COM,baud=BAUD,wjap=b64("AT+WJAP=CMW-AP,12345678"))
    return (sess.run_ps(ps).std_out or b"").decode("cp936","replace")

# ---------- per-rate ----------
def setup(ch, sig, ratecmds):
    c.w("SOURce:WLAN:SIGNaling1:STATe OFF")
    t0=time.time()
    while time.time()-t0<20:
        if c.q("SOURce:WLAN:SIGNaling1:STATe?")=="OFF": break
        time.sleep(1.5)
    c.w("*CLS")
    c.w("ROUTe:WLAN:SIGNaling1:SCENario:SCELl RF2C,RX1,RF2C,TX1")
    c.w("CONFigure:WLAN:SIGNaling1:CONNection:OMODe AP")
    c.w("CONFigure:WLAN:SIGNaling1:CONNection:SSID 'CMW-AP'")
    c.w('CONFigure:WLAN:SIGNaling1:CONNection:SECurity:PASSphrase W2P,"12345678"')  # sets W2P + passphrase in one cmd
    c.werr("CONFigure:WLAN:SIGNaling1:CONNection:STANdard %s"%sig)
    c.w("CONFigure:WLAN:SIGNaling1:RFSettings:CHANnel %d"%ch)
    for rc in ratecmds: c.werr(rc)
    c.w("CONFigure:WLAN:SIGNaling1:RFSettings:BOPower -40")
    c.w("CONFigure:WLAN:SIGNaling1:RFSettings:EPEPower 30")
    c.w("CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:OUTPut 1")
    c.w("CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:INPut 1")
    c.w("SOURce:WLAN:SIGNaling1:STATe ON")
    t0=time.time()
    while time.time()-t0<25:
        if c.q("SOURce:WLAN:SIGNaling1:STATe?")=="ON": break
        time.sleep(1.5)
    print("    STANdard=%s CH=%s DFR=%s"%(
        c.q("CONFigure:WLAN:SIGNaling1:CONNection:STANdard?"),
        c.q("CONFigure:WLAN:SIGNaling1:RFSettings:CHANnel?"),
        c.q("CONFigure:WLAN:SIGNaling1:CONNection:DFRControl?")))

def pg1_on(dut):
    c.w("CONFigure:WLAN:SIGNaling1:IPVFour:STATic:IPADdress:DESTination %s"%dut.replace(".",","))
    c.w("CONFigure:WLAN:SIGNaling1:PGEN1:PROTocol ICMP")
    c.w("CONFigure:WLAN:SIGNaling1:PGEN1:IPVersion IV4")
    c.w("CONFigure:WLAN:SIGNaling1:PGEN1:CONFig ON,4,1472,PRAN,TID0")

def meas_setup(ch, mstd, scount):
    c.w("ABORt:WLAN:MEAS1:MEValuation"); time.sleep(0.3)
    c.w('ROUTe:WLAN:MEAS1:SCENario:CSPath "WLAN Sig1"')
    c.w("CONFigure:WLAN:MEAS1:RFSettings:FREQuency %d"%freq(ch))
    c.w("CONFigure:WLAN:MEAS1:RFSettings:ENPower1 30")
    c.werr("CONFigure:WLAN:MEAS1:ISIGnal:STANdard %s"%mstd)
    c.w("CONFigure:WLAN:MEAS1:ISIGnal:BWIDth BW20")
    c.w("CONFigure:WLAN:MEAS1:MEValuation:REPetition SING")
    c.w("CONFigure:WLAN:MEAS1:MEValuation:SCOunt:MODulation %d"%scount)
    c.w("CONFigure:WLAN:MEAS1:MEValuation:TOUT 15")
    c.w('TRIGger:WLAN:MEAS1:MEValuation:SOURce "WLAN Sig1: RXFrameTrigger"')
    c.w("TRIGger:WLAN:MEAS1:MEValuation:TOUT 15")

def shot(fetch):
    c.w("ABORt:WLAN:MEAS1:MEValuation"); c.w("INITiate:WLAN:MEAS1:MEValuation")
    t0=time.time()
    while time.time()-t0<16:
        if c.q("FETCh:WLAN:MEAS1:MEValuation:STATe?").startswith("RDY"): break
        time.sleep(0.4)
    return c.q("FETCh:WLAN:MEAS1:MEValuation:MODulation:%s:AVERage?"%fetch).split(",")

def measure(ch, lbl):
    sig,mstd,fetch,idx,want,scount,ratecmds=SPEC[lbl]
    for rnd in range(3):
        print("  [ch%d %s] round%d setup..."%(ch,lbl,rnd+1))
        setup(ch, sig, ratecmds)
        log=wjap_join()
        joined = any(k in log.lower() for k in ("got ip","wifi connected","wjap:1"))
        tail=" ".join(l.strip() for l in log.splitlines() if l.strip())[-160:]
        print("    join: ...%s | joined=%s"%(tail, joined))
        if not joined:
            print("    module did not connect, retry"); continue
        dut=(c.q("SENSe:WLAN:SIGNaling1:UESinfo:UEADdress:IPV4?") or "").strip('"')
        if dut in ("","0.0.0.0","NAV"): dut="192.168.48.129"
        pg1_on(dut); time.sleep(3)
        print("    DRATe=%s RXBP=%s"%(c.q("SENSe:WLAN:SIGNaling1:UESinfo:DRATe?"),
                                      c.q("SENSe:WLAN:SIGNaling1:UESinfo:RXBPower?")))
        meas_setup(ch, mstd, scount)
        vals=[]; seen=set()
        nshot=16 if scount<=1 else 10
        for i in range(nshot):
            f=shot(fetch); rr=f[0] if f else "?"; rate=f[1] if len(f)>1 else "?"
            ok = rr=="0" and len(f)>idx and f[idx] not in ("NCAP","INV","NAV")
            print("    shot%2d reliab=%s(%s) rate=%s TX=%s"%(i+1,rr,RELIAB.get(rr,rr),rate,f[idx] if ok else "-"))
            if ok: seen.add(rate)
            if ok and want in rate:
                vals.append(float(f[idx]))
                if len(vals)>=3: break
            time.sleep(0.3)
        if len(vals)>=3:
            return sum(vals)/len(vals), vals, "OK"
        print("    target rate '%s' not captured (seen=%s), retry"%(want,sorted(seen)))
    return None, [], "FAIL(seen=%s)"%sorted(seen)

def main():
    cells=sys.argv[1] if len(sys.argv)>1 else "1:CCK11"
    print("IDN:", c.q("*IDN?"))
    rows=[]
    for cell in cells.split(","):
        chs,lbl=cell.split(":"); ch=int(chs)
        print("\n===== ch%d %s ====="%(ch,lbl))
        avg,vals,st=measure(ch,lbl)
        txt="TXavg=%.2f dBm (n=%d: %s)"%(avg,len(vals),[round(v,2) for v in vals]) if avg is not None else st
        print(">>> ch%d %s: %s"%(ch,lbl,txt)); rows.append(("ch%d %s"%(ch,lbl),txt))
    print("\n===== SUMMARY =====")
    for l,t in rows: print("  %s: %s"%(l,t))
    c.w("CONFigure:WLAN:SIGNaling1:PGEN1:CONFig OFF,4,1472,PRAN,TID0")

if __name__=="__main__": main()
