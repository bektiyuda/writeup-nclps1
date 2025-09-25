## Telemetry

**Difficulty:** Easy-Medium
**Author:** moonetics

### Description

CLI kecil untuk memvalidasi dan men-trace sebuah “session tag” yang digunakan modul telemetry internal. Mendukung mode verbose untuk membantu penelusuran jalur proses byte-per-byte. Dirancang untuk berjalan di Linux x86_64 (release build)

## Initial Analysis

```c
undefined8 main(int argc, char **argv) {
    // ... parsing -v/--verbose, --check <tag>, NCL_TRACE
    i64 meta[5] = {0};
    if (!parse_flag_format(tag, &meta[0], &meta[1])) { fprintf(stderr, "invalid format\n"); return 1; }

    size_t n = strlen(tag);
    void *buf = malloc(n);
    meta[2] = 0;
    transform_pipeline(tag, n, buf, &meta[2], verbose);
    if (meta[2] == 0x36 && constant_time_eq(buf, (void*)0x102080, 0x36)) {
        puts("session tag accepted");
        return 0;
    }
    puts("session tag rejected");
    return 1;
}
```

ELF membaca input "session tag" lewat `--check <tag>`. Variabel lingkungan `NCL_TRACE` atau opsi `-v/--verbose` menyalakan hexdump setiap tahap transformasi. Alur fungsi main:

1. Validasi format awal melalui `parse_flag_format(tag, ...)`.
2. Jalankan `transform_pipeline(tag, len, out, &out_len, verbose)` — transformasi **panjang tetap** (len-preserving).
3. Jika `out_len == 0x36 (54)` dan `constant_time_eq(out, kTarget@.rodata, 54)` valid, tag diterima.

```c
  iVar5 = constant_time_eq(__ptr,&kTarget,0x36);
  if (iVar5 != 0) {
    puts("session tag accepted");
    free(__ptr);
    uVar3 = 0;
    goto LAB_00101386;
```

**kTarget (54 byte, alamat mulai 0x102080):**

```
00 3c f0 9d f7 bc 3b ca 97 46 8d e4 e6 6f 64 fd ca 9d 13 c8 a2 91 02 b2 43 31 aa 00 18 c0 47 82 75 c6 fe 37 5c e6 e1 6f b1 d6 ac 67 f1 41 5b d8 dd 97 e6 f3 0f
```

Di `main`, bandingkan hasil transform dengan blob `kTarget` di `.rodata`.

```c
void transform_pipeline(void *in, size_t n, void *out, size_t *out_n, int verbose) {
    uint8_t *d = malloc(n); memcpy(d, in, n);
    // stage1_xor_key
    uint8_t b = 0xD8; for (size_t i=0;i<n;i++){ d[i]^=b; if(i+1<n) b = kKey[(i+1)&0xF]; }
    // stage2_addpos
    uint8_t acc=0; for (size_t i=0;i<n;i++){ acc+=7; d[i] = d[i] + acc + 3; }
    // stage3_rol (rotasi dihitung dari i menggunakan magic multiply /5)
    for (size_t i=0;i<n;i++){ uint8_t r = rot_count(i); d[i] = rol8(d[i], r); }
    // stage4_xor_idx
    for (size_t i=0;i<n;i++){ d[i] ^= (uint8_t)(i ^ 0xA5); }
    // stage5_swappairs
    for (size_t i=0;i+1<n;i+=2){ uint8_t t=d[i]; d[i]=d[i+1]; d[i+1]=t; }
    memcpy(out, d, n); *out_n = n; free(d);
}
```

**kKey (alamat mulai 0x102130):**

```
d8 0b 31 e2 e1 00 fc 46 71 1d 4e 24 37 0e 54 10
```

Kunci 16‑byte untuk tahap XOR berada pada `kKey` **`0x102130`**. Verifikasi merupakan rangkaian transformasi bytewise yang dapat dibalik. Tahap transformasinya seperti berikut:

1. stage1_xor_key: `dst[0] ^= 0xD8;` dan untuk `i≥1`: `dst[i] ^= kKey[i & 0xF]`.
2. stage2_addpos: `dst[i] = dst[i] + (3 + 7*i) (mod 256)`.
3. stage3_rol: `dst[i] = rol8(dst[i], b(i))`, dengan hitungan rotasi:
   `hi = ((i * 0xCCCCCCCCCCCCCCCD) >> 64) & 0xFF;`
   `b(i) = ( i - (( (hi & 0xFC) + (i/5) ) & 0xFF) ) & 7`
4. stage4_xor_idx: `dst[i] ^= (i ^ 0xA5)`.
5. stage5_swappairs: tukar `(0,1), (2,3), ...`.

Semua tahap tersebut dapat dilakukan inverse dengan, swap -> XOR -> ROR -> kurang -> XOR kunci. Saya mengeimplentasikannya dalam solver berikut:

```python
from typing import List

kTarget = bytes.fromhex(
    "00 3c f0 9d f7 bc 3b ca 97 46 8d e4 e6 6f 64 fd"
    " ca 9d 13 c8 a2 91 02 b2 43 31 aa 00 18 c0 47 82"
    " 75 c6 fe 37 5c e6 e1 6f b1 d6 ac 67 f1 41 5b d8"
    " dd 97 e6 f3 0f 5a".replace("\n", " ")
)

kKey = bytes.fromhex("d8 0b 31 e2 e1 00 fc 46 71 1d 4e 24 37 0e 54 10")

M = 0xCCCCCCCCCCCCCCCD

def ror8(x: int, r: int) -> int:
    r &= 7
    return ((x >> r) | ((x << (8 - r)) & 0xFF)) & 0xFF

def rot_count(i: int) -> int:
    hi = ((i * M) >> 64) & 0xFF
    return ((i & 0xFF) - (((hi & 0xFC) + ((i // 5) & 0xFF)) & 0xFF)) & 7

def invert(target: bytes) -> bytes:
    n = len(target)
    buf = bytearray(target)
    # inv stage5: swap
    for i in range(0, n - 1, 2):
        buf[i], buf[i+1] = buf[i+1], buf[i]
    # inv stage4: XOR (i ^ 0xA5)
    for i in range(n):
        buf[i] ^= (i ^ 0xA5) & 0xFF
    # inv stage3: ROR by rot_count(i)
    for i in range(n):
        buf[i] = ror8(buf[i], rot_count(i))
    # inv stage2: subtract (3 + 7*i)
    for i in range(n):
        buf[i] = (buf[i] - (3 + 7*i)) & 0xFF
    # inv stage1: XOR keystream
    for i in range(n):
        k = 0xD8 if i == 0 else kKey[i & 0xF]
        buf[i] ^= k
    return bytes(buf)

flag = invert(kTarget)
print(flag.decode('utf-8', errors='replace'))
```

### Flag

NCLPS1{t3lLemeTry._0ps_4lPha_2025_+bU1ld1a_0b5085122b}