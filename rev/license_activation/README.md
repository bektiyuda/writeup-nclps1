## License Activation

**Difficulty:** Easy
**Author:** moonetics

### Description

Utilitas baris-perintah untuk memverifikasi kunci lisensi secara offline. Masukkan kunci dengan format NCLPS1{...} Jika valid, aplikasi menampilkan Activation successful. Jika tidak, akan menampilkan Activation failed.

### Solution

```python
def _rol8(x, r):
    r &= 7
    x &= 0xFF
    return ((x << r) | (x >> (8 - r))) & 0xFF

class _VM:
    def __init__(self, bytecode, user_input):
        self.bc = bytearray(bytecode)
        self.ip = 0
        self.st = []
        self.s  = [ord(c) & 0xFF for c in user_input]

    def run(self):
        ip = self.ip
        bc = self.bc
        st = self.st
        s  = self.s
        while True:
            op = bc[ip]; ip += 1
            if op == 0x00:
                pass
            elif op == 0x01:
                st.append(bc[ip]); ip += 1
            elif op == 0x02:
                idx = bc[ip]; ip += 1
                st.append(s[idx] if 0 <= idx < len(s) else 0)
            elif op == 0x03:
                b = st.pop(); a = st.pop(); st.append((a ^ b) & 0xFF)
            elif op == 0x04:
                b = st.pop(); a = st.pop(); st.append((a + b) & 0xFF)
            elif op == 0x05:
                r = bc[ip]; ip += 1
                a = st.pop(); st.append(_rol8(a, r))
            elif op == 0x06:
                b = st.pop(); a = st.pop(); st.append(1 if a == b else 0)
            elif op == 0x07:
                b = st.pop(); a = st.pop(); st.append(1 if (a and b) else 0)
            elif op == 0x08:
                return bool(st.pop() if st else 0)
            elif op == 0x09:
                b = st.pop(); a = st.pop(); st.append((a - b) & 0xFF)
            elif op == 0x0A:
                m = bc[ip]; ip += 1
                a = st.pop(); st.append(a % m if m else 0)
            elif op == 0x0B:
                a = st[-1]; st.append(a)
            elif op == 0x0C:
                if st: st.pop()
            else:
                return False
```

Dari code python yang diberikan, ternyata tidak menjalankan verifikasi langsung atas string, melainkan memuat sebuah blok bytecode biner yang disimpan dalam bentuk Base85 kemudian di-XOR dengan sebuah konstanta (228). Setelah decode, ditemukan sebuah VM yang mengeksekusi, PUSH_CONST, PUSH_INPUT, XOR, ADD, ROL, MOD, EQ, AND, RET untuk setiap posisi karakter input. Ada serangkaian 72 cek per-karakter yang masing‑masing melakukan manipulasi aritmetik/bitwise pada `s[i]` lalu membandingkannya dengan sebuah konstanta, semua hasil di-`AND` untuk menentukan validitas keseluruhan.

Berikut implementasi solver yang saya gunakan. Kode ini mendekode payload Base85, melakukan XOR kunci, mem-parse aliran instruksi, lalu menyelesaikan setiap cek karakter satu per satu dengan mencoba semua nilai byte (0..255).

```python
import base64

B85 = "..."
KEY = 228

raw = base64.b85decode(B85.encode('ascii'))
bc  = bytes((b ^ KEY) & 0xFF for b in raw)

# 0x01 = PUSH_CONST <imm>
# 0x02 = PUSH_INPUT <idx>
# 0x03 = XOR
# 0x04 = ADD
# 0x05 = ROL <imm>
# 0x06 = EQ
# 0x07 = AND
# 0x08 = RET
# 0x09 = SUB
# 0x0A = MOD <imm>
# 0x0B = DUP
# 0x0C = POP

def solve_seq(seq):
    sols=[]
    for x in range(256):
        st=[x]
        ip=0
        try:
            while ip < len(seq):
                op, imm = seq[ip]; ip+=1
                if op==0x01: st.append(imm)
                elif op==0x02: st.append(0)
                elif op==0x03:
                    b = st.pop(); a = st.pop(); st.append((a ^ b) & 0xFF)
                elif op==0x04:
                    b = st.pop(); a = st.pop(); st.append((a + b) & 0xFF)
                elif op==0x05:
                    r = imm & 7; a = st.pop(); st.append(((a << r) | (a >> (8-r))) & 0xFF)
                elif op==0x06:
                    b = st.pop(); a = st.pop(); st.append(1 if a==b else 0)
                elif op==0x07:
                    b = st.pop(); a = st.pop(); st.append(1 if (a and b) else 0)
                elif op==0x09:
                    b = st.pop(); a = st.pop(); st.append((a - b) & 0xFF)
                elif op==0x0A:
                    m = imm; a = st.pop(); st.append(a % m if m else 0)
                elif op==0x0B:
                    st.append(st[-1])
                elif op==0x0C:
                    if st: st.pop()
                else:
                    raise RuntimeError(f"unknown op {op}")
        except IndexError:
            continue
        if st and st[-1]==1:
            sols.append(x)
    if len(sols)!=1:
        raise RuntimeError(f"solusi tidak unik/ada untuk seq: {sols}")
    return sols[0]

flag = [0]*72
ip = 0
found = 0
while ip < len(bc) and found < 72:
    op = bc[ip]; ip+=1
    if op==0x02:
        idx = bc[ip]; ip+=1
        seq = []
        while True:
            o = bc[ip]; ip+=1
            if o in (0x01, 0x02, 0x05, 0x0A):
                imm = bc[ip]; ip+=1
                seq.append((o, imm))
            else:
                seq.append((o, None))
            if o==0x06:
                break
        flag[idx] = solve_seq(seq)
        found += 1
    elif op==0x08:
        break
    else:
        pass

print(bytes(flag).decode())
```

### Flag

NCLPS1{he1i_KamU_ter1m4k4siH_y4_uD4h_akt1v4si_l1SeNnns1_k4m1_b4c7599f3b}