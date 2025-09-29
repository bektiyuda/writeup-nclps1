## Dial & Decode
**Difficulty:** Easy-Medium
**Author:** moonetics

### Description
“Mereka” menelepon, tapi tidak dengan cara yang kamu kira. Tugasmu: dengarkan, pahami, bongkar.

### Solution
```python
dtmf_freqs = {
    '1': (697, 1209), '2': (697, 1336), '3': (697, 1477), 'A': (697, 1633),
    '4': (770, 1209), '5': (770, 1336), '6': (770, 1477), 'B': (770, 1633),
    '7': (852, 1209), '8': (852, 1336), '9': (852, 1477), 'C': (852, 1633),
    '*': (941, 1209), '0': (941, 1336), '#': (941, 1477), 'D': (941, 1633),
}

def text_to_tone(text, filename, fs=8000, tone_time=0.08, silence_time=0.10):
    for char in text:
        f1, f2 = dtmf_freqs[char]
        t = np.linspace(0, tone_time, int(fs * tone_time), endpoint=False)
        tone = 0.5*np.sin(2*np.pi*f1*t) + 0.5*np.sin(2*np.pi*f2*t)
        # disimpan ke file WAV
```

Pada source code ditemukan bahwa program menggunakan **DTMF (Dual-Tone Multi-Frequency)** untuk mengubah digit teks menjadi nada telepon. Tiap digit direpresentasikan oleh kombinasi dua frekuensi, satu dari kelompok low (697, 770, 852, 941 Hz) dan satu dari kelompok high (1209, 1336, 1477, 1633 Hz). 

File audio yang dihasilkan menyimpan tiga bilangan, bilangan prima `p`, bilangan prima `q`, dan ciphertext `c`. Dengan mengetahui kedua faktor prima tersebut, dapat dihitung nilai `φ(n) = (p−1)(q−1)` dan memperoleh private key `d = e⁻¹ mod φ(n)`. Untuk tahapannya 

1. Tulis fungsi untuk membaca WAV, 
2. Memotongnya ke dalam blok 0.08 detik, 
3. Menjalankan FFT berukuran kecil (misal 2048) untuk mendeteksi dua frekuensi dominan. 
4. Mapping kombinasi frekuensi ke digit menggunakan tabel standar. Hasil decoding tiga file WAV menghasilkan string numerik panjang yang dapat langsung dikonversi menjadi integer `p`, `q`, dan `c`. 
5. Lakukan dekripsi RSA menggunakan Python.

Untuk implementasinya adalah solver berikut ini:

```python
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
```

### Flag
NCLPS1{hai1_BOl3H_aku_m1nta_nom0r_t3lepOn_k4mu?_0dcd60dab2}
