## byte code
**Difficulty:** Easy-Medium
**Author:** n4siKvn1ng

### Description
This code is something another, can you see what the code is todo?

### Solution
```txt
[101, 154, 101, 21, 26, 170, 80, 171, 76, 19, 44, 233, 88, 234, 118, 32, 39, 252, 26, 183, 76, 32, 97, 53, 81, 88, 99, 85, 50, 125, 74, 76, 87, 94, 33, 121, 124, 86, 48, 63, 48, 68, 85, 49, 108, 122, 52, 87, 53, 82, 35]
```

File output.txt berisi **daftar integer Python**. Bagian **akhir** merupakan karakter ASCII yang sepertinya Base85, sedangkan bagian **awal** tampak biner.

File chall.dism menampilkan bytecode Python 3.11 (terlihat dari opcode seperti `RESUME`, `BINARY_SLICE`, `WITH_EXCEPT_START`, dll). Potongan fungsi berikut menjadi kunci:

- **Flag read**: membuka `flag.txt`, lalu `read().strip()`.
- **Flag split**: `mid = len(flag)//2` dan mengembalikan `(flag[:mid], flag[mid:])`.
- **Fungsi pergeseran byte**:
  - `left(char, amount) => chr((ord(char) - amount) % 256)`
  - `r_t(char, amount) => chr((ord(char) + amount) % 256)`
- **Transform A (XOR)**: generator `''.join(chr(ord(a) ^ b) for (a,b) in zip(s1, repeated_key))` dengan **kunci pendek berulang** yang dibentuk dari tuple konstanta `(43, 217, 41, 69, 73, 155)`.
- **Transform B (Shift → Base85)**: untuk `enumerate(s)` digunakan pola, indeks genap `left(c, 2)` (−2), indeks ganjil `r_t(c, 3)` (+3), hasilnya **di-UTF‑8‑kan (`.encode()`)** dan **di‑Base85** (`b85encode`), lalu `.decode()` kembali menjadi teks.
- **Writer**: menyusun `qw(aer, ot()) + cd(abu)` kemudian menulis `str([ord(c) for c in ...])` ke `output.txt`. Dari pemanggilan: `qw` menerima **2 argumen** (cocok untuk XOR+key), `cd` menerima **1 argumen** (cocok untuk Shift→Base85). Artinya **phase pertama** diproses XOR, **phase kedua** diproses Shift→Base85.

Di bawah ini skrip solver dari daftar integer. Skrip akan:
1. Mengubah daftar integer menjadi string,
2. Mencari batas di mana sufiks valid untuk **Base85** dan setelah di‑UTF‑8‑kan serta dibalik pergeseran berakhir dengan `}` (format flag),
3. Membalik XOR menggunakan kunci berulang,
4. Menggabungkan kedua phase.

```python
import base64
from typing import Optional

INTS = [
    101, 154, 101, 21, 26, 170, 80, 171, 76, 19, 44, 233, 88, 234, 118, 32,
    39, 252, 26, 183, 76, 32, 97, 53, 81, 88, 99, 85, 50, 125, 74, 76, 87, 94,
    33, 121, 124, 86, 48, 63, 48, 68, 85, 49, 108, 122, 52, 87, 53, 82, 35,
]

KEY = [43, 217, 41, 69, 73, 155]

s = ''.join(map(chr, INTS))

def try_decode_halfB(base85_text: str) -> Optional[str]:
    try:
        raw = base64.b85decode(base85_text)
        shifted = raw.decode('utf-8')
        out = []
        for i, ch in enumerate(shifted):
            c = ord(ch)
            out.append(chr((c + 2) % 256) if i % 2 == 0 else chr((c - 3) % 256))
        candidate = ''.join(out)
        return candidate
    except Exception:
        return None

best_split = None
halfB_plain = None
for i in range(1, len(s)):
    suf = s[i:]
    rec = try_decode_halfB(suf)
    if not rec:
        continue
    if rec.endswith('}') and all(0 <= ord(c) <= 255 for c in rec):
        best_split = i
        halfB_plain = rec
        break

if best_split is None:
    raise SystemExit('Split Base85 tidak ditemukan — periksa input.')

pref = s[:best_split].encode('latin-1', 'ignore')
plainA = bytes([b ^ KEY[i % len(KEY)] for i, b in enumerate(pref)]).decode('latin-1')

flag = plainA + halfB_plain
print(flag)
```

### Flag
NCLPS1{reVers3_eng1neer1ng_python_byte_c0de}
