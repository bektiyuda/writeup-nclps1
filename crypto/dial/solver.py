import numpy as np
from scipy.io import wavfile
from Crypto.Util.number import long_to_bytes

LOWS  = [697,770,852,941]
HIGHS = [1209,1336,1477,1633]
MAP = {
    (697,1209):'1',(697,1336):'2',(697,1477):'3',(697,1633):'A',
    (770,1209):'4',(770,1336):'5',(770,1477):'6',(770,1633):'B',
    (852,1209):'7',(852,1336):'8',(852,1477):'9',(852,1633):'C',
    (941,1209):'*',(941,1336):'0',(941,1477):'#',(941,1633):'D',
}

def decode(path, tone=0.08, silence=0.10):
    sr, x = wavfile.read(path)
    if x.ndim>1: x = x[:,0]
    x = x.astype(np.float32)/32768.0
    L = int(sr*tone); B = int(sr*(tone+silence))
    nblk = len(x)//B
    out=[]
    freqs = np.fft.rfftfreq(2048, 1/sr)
    for i in range(nblk):
        seg = x[i*B:i*B+L]
        if len(seg)<L: continue
        X = np.abs(np.fft.rfft(seg*np.hamming(len(seg)), n=2048))
        def pick(targets):
            best=None; val=-1
            for f in targets:
                m = (freqs>=f-10)&(freqs<=f+10)
                s = X[m].sum()
                if s>val: val=s; best=f
            return best
        lo = pick(LOWS); hi = pick(HIGHS)
        out.append(MAP[(lo,hi)])
    return ''.join(out)

p = int(decode("p_dial.wav"))
q = int(decode("q_dial.wav"))
c = int(decode("message.wav"))
phi = (p-1)*(q-1); e=65537
d = pow(e, -1, phi)
m = pow(c, d, p*q)
print(long_to_bytes(m).decode("utf-8", errors="replace"))
