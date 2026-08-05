"""Bring CMW WLAN signaling back up from clean state: Sig STATe ON + wait PEND→ON."""
import pyvisa, time, os, sys
for k in ('http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)

rm = pyvisa.ResourceManager('@py')
inst = rm.open_resource('TCPIP0::192.0.2.10::5025::SOCKET')
inst.read_termination='\n'; inst.write_termination='\n'; inst.timeout=15000
inst.write('*CLS')

def q(s): return inst.query(s).strip()

print(f'IDN: {q("*IDN?")}')
print(f'Pre Sig STATe: {q("SOURce:WLAN:SIGNaling1:STATe?")}')

# Bring Sig1 up
inst.write('SOURce:WLAN:SIGNaling1:STATe ON')
t0 = time.time()
last = None
while time.time() - t0 < 90:
    s = q('SOURce:WLAN:SIGNaling1:STATe?')
    if s != last:
        print(f'  t={time.time()-t0:5.1f}s  STATe={s}')
        last = s
    if s == 'ON': break
    time.sleep(2)

# Verify config preserved
print(f'\nFinal STATe: {q("SOURce:WLAN:SIGNaling1:STATe?")}')
print(f'  SSID    : {q("CONFigure:WLAN:SIGNaling1:CONNection:SSID?")}')
print(f'  CH      : {q("CONFigure:WLAN:SIGNaling1:RFSettings:CHANnel?")}')
print(f'  BOPower : {q("CONFigure:WLAN:SIGNaling1:RFSettings:BOPower?")}')
print(f'  EATT IN : {q("CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:INPut?")}')
print(f'  EATT OUT: {q("CONFigure:WLAN:SIGNaling1:RFSettings:EATTenuation:OUTPut?")}')
print(f'  err     : {q("SYST:ERR?")}')
inst.close()
