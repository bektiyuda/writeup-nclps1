## Spikey 

**Difficulty:** Medium-Hard
**Author:** moonetics

### Description

You are hired as a security consultant to audit “Spikey”, the control module on a prototype research drone. It's discovered that there's a logic bomb in its firmware: the drone will only unlock if given eight passwords at precise time intervals - and it will detect the debugger. Your mission: reverse-engineer and disable the logic bomb to get the mission access code without triggering the “explosion”.

### Solution

```c
__time64_t t = _time64(NULL);
srand((uint)t);
if (!IsDebuggerPresent()) {
    double tol[8]  = {0.05,0.02,0.05,0.02,0.1,0.02,0.05,0.02};
    double goal[8] = {0.5,0.1,0.9,0.2,1.0,0.15,0.85,0.3}; // disimpan pada indeks 8..15
    double t0 = nowSec();
    char codes[8][16];
    for (int i=0;i<8;i++) {
        printf("Code %d: ", i+1); fflush(stdout);
        if (scanf("%15s", codes[i]) != 1) return 1;
        double t1 = nowSec();
        double dt = t1 - t0;
        if (dt < goal[i]-tol[i] || dt > goal[i]+tol[i]) { puts("Miscalibrated"); return 1; }
        t0 = t1; jitter();
    }
    if (isRabbitHole((long long)codes) == 0) {
        for (int i=0;i<8;i++) {
            char *p = (char*)recoverPart(i);
            if (strcmp(codes[i], p) != 0) { puts("Integrity breach"); free(p); return 1; }
            free(p);
        }
        void *flag = recoverFlag();
        printf("Flag: %s\n", flag);
        free(flag);
    } else {
        void *boom = recoverBoom();
        printf("Flag: %s\n", boom);
        free(boom);
    }
}
```

Fungsi main menunjukkan tiga lapis kontrol: anti‑debug, timing gate untuk delapan input, dan pemilihan jalur pemulihan flag. Program memanggil `IsDebuggerPresent()`, jika terdeteksi debugger, proses berhenti. Program melakukan delapan kali prompt `Code 1..8`, memeriksa selisih waktu antar input dibanding target dan toleransi per‑indeks. Jika di luar rentang, muncul `Miscalibrated` dan program berhenti. Setelah seluruh input diterima, jalur bercabang berdasarkan `isRabbitHole()`. Jika `isRabbitHole(...) == 0`, setiap input diverifikasi terhadap nilai `recoverPart(i)`. Jika seluruhnya cocok, program memanggil `recoverFlag()` dan mencetak `Flag: ...`. Jika tidak, ia mencetak hasil dari `recoverBoom()` (decoy).

```c
void* recoverFlag(void) {
    void *buf = malloc(0x4F);
    if (!buf) exit(1);
    for (unsigned long i=0; i<0x4E; i++) { // 78 byte
        ((unsigned char*)buf)[i] = revOp(((unsigned char*)&mystBlockF)[i], (int)i);
    }
    ((unsigned char*)buf)[0x4E] = 0; // NUL
    return buf;
}
```

**mystBlockF (78 byte, alamat mulai 0x1400050A0):**

```
46 83 15 56 df 99 e4 b5 2f 26 da 6b 03 d7 8e 75 b5 f0 b3 bb a0 21 b4 c0 9f 86 17 4a 56 51 9b 8f b2 6a 86 d2 1e 97 31 78 13 b7 c3 98 48 79 6e f5 af 34 1a b4 4e 43 8c 49 bc 2b c9 83 2f 1d bf e1 e1 33 6d de fa 3d 4e 44 ee f6 86 27 28 37
```

Dari hasil decompile, dapat diketahui bahwa `recoverFlag()` tidak tergantung pada input maupun waktu. Fungsi ini membaca blob global `mystBlockF` sepanjang **78 byte** dan men-decode setiap byte dengan transformasi terbalik `revOp(b, idx)`, lalu menambahkan terminator NUL.

```c
byte revOp(byte b, int idx) {
    int k = (idx * 3 + 5) % 8; if (k == 0) k = 1; // k ∈ {1..7}
    unsigned int r = ror8(~b, (byte)k);
    return ( (char)r + 0xA6U ) ^ ((unsigned char*)&helperKey)[idx % 5];
}

unsigned int ror8(byte x, byte s) {
    return ((unsigned int)x << ((8 - s) & 0x1F)) | (((unsigned int)x) >> (s & 0x1F));
}
```

**helperKey (5 byte, alamat mulai 0x140005120):**

```
3d a7 4f 1c e5
```

Transformasi berada pada `revOp`. Di sini byte obfuscated dibalik (NOT), diputar (ROR) dalam 8 bit dengan jumlah rotasi yang diturunkan dari indeks, di‑offset dengan `+0xA6`, kemudian di‑XOR dengan kunci berulang 5‑byte `helperKey`.

Karena `revOp` hanya bergantung pada argumen `(b, idx)` dan tabel `helperKey`, maka flag dapat dipulihkan **statis** tanpa perlu memenuhi timing gate atau melewati `isRabbitHole()`. Implimentasinya cukup terapkan `revOp` pada setiap byte `mystBlockF[i]` dengan indeks `i` dari 0 sampai 77 untuk memperoleh flag. Berikut adalah implementasinya di solver.

```python
mystBlockF = bytes([
    0x46,0x83,0x15,0x56,0xDF,0x99,0xE4,0xB5,0x2F,0x26,0xDA,0x6B,0x03,0xD7,0x8E,0x75,
    0xB5,0xF0,0xB3,0xBB,0xA0,0x21,0xB4,0xC0,0x9F,0x86,0x17,0x4A,0x56,0x51,0x9B,0x8F,
    0xB2,0x6A,0x86,0xD2,0x1E,0x97,0x31,0x78,0x13,0xB7,0xC3,0x98,0x48,0x79,0x6E,0xF5,
    0xAF,0x34,0x1A,0xB4,0x4E,0x43,0x8C,0x49,0xBC,0x2B,0xC9,0x83,0x2F,0x1D,0xBF,0xE1,
    0xE1,0x33,0x6D,0xDE,0xFA,0x3D,0x4E,0x44,0xEE,0xF6,0x86,0x27,0x28,0x37
])

helperKey = bytes([0x3D, 0xA7, 0x4F, 0x1C, 0xE5])

def ror8(x, s):
    s &= 7
    return ((x >> s) | ((x << (8 - s)) & 0xFF)) & 0xFF

def revOp(b, idx):
    k = (idx * 3 + 5) % 8
    if k == 0:
        k = 1
    r = ror8((~b) & 0xFF, k)
    return ((r + 0xA6) & 0xFF) ^ helperKey[idx % 5]

out = bytearray()
for i, bb in enumerate(mystBlockF[:78]):
    out.append(revOp(bb, i))

flag = out.decode('utf-8', errors='strict')
print(flag)
```

### Flag

NCLPS1{w0ww_k4mu_b3Rh4siL_d3fuSe_l0g1c_b0mb_d3ng4n_t1ming_pr3si1s1_e4743a6046}
