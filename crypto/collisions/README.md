## collisions

**Difficulty:** Medium-Hard

**Author:** n4siKvn1ng

### Description

Hash adalah fungsi satu arah, apakah ada attack untuk hash? Yaps ada berupa collisions atau dictionary attack, tapi untuk chall ini tidak menggunakan dictionary attack Bentuk collisions bisa tabrakan dari input yang berbeda atau juga nilai akhir kembali ke awal.

### Solution

```python
import functools; print(functools.reduce(lambda flag, i: flag ^ (flag >> 2**i), range(9), int.from_bytes(b"NCLPS1{redacted}", "big")))
```

Dari source code ditemukan kalau program menggunakan `functools.reduce` untuk melakukan transformasi berulang terhadap integer hasil `int.from_bytes`. Nilai awal adalah representasi biner dari string flag.

```python
flag = flag ^ (flag >> (2**i))
```

Operasi `x ^ (x >> k)` merupakan fungsi linear representasi bit. Transformasi ini dapat dibalik karena bit paling signifikan tidak bergantung pada bit yang lebih tinggi lagi, sehingga dapat dihitung balik ke nilai asal. 

Strateginya membalik transformasi dengan urutan terbalik. Dimulai dari integer output, kita menerapkan inverse dari operasi shift terbesar ke yang terkecil. Inverse dari operasi `y = x ^ (x >> k)` dapat dilakukan dengan loop iteratif, kemudian integer hasil dapat diubah kembali ke bytes dan dibaca sebagai string ASCII, yang akan memunculkan flag. Untuk implementasinya adalah adalah solver berikut ini:

```python
T = 6708225246577317268201359870589947128321270453156893234886662491398921333524854484228506876784333764380835907785971649995603806504942718660141508646410278513251598900

def invert_xor_shift(y, k, bitlen):
    x = y
    s = k
    while s < bitlen:
        x ^= (x >> s)
        s <<= 1
    return x

bitlen = T.bit_length() + 256
cur = T
for i in reversed(range(9)):
    cur = invert_xor_shift(cur, 1 << i, bitlen)

flag = cur.to_bytes((cur.bit_length() + 7) // 8, "big")
print(flag.decode())
```

### Flag

NCLPS1{h4sh_t1d4k_s3cur3_k3t1k4_t3rj4d1_c0ll1s10ns_p4d4_r3sult_v4lu3}
