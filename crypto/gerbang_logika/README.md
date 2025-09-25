## gerbang logika

**Difficulty:** Medium-Hard

**Author:** n4siKvn1ng

### Description

Chall ini dasarnya ialah seperti chall crypto di Incognito CTF 4.0 Saya coba modifikasi dengan menambahkan beberapa hal.

### Solution

Dari source code, dapat diketahui bahwa alur enkripsi yang terdiri dari operasi XOR dengan output linear congruential generator (LCG) dan transformasi bit berdasarkan swap. Ciphertext yang diberikan dalam bentuk heksadesimal, sementara plaintext yang valid dapat diverifikasi dengan hash SHA-256 yang disediakan.

```python
def encrypt_byte(p, state):
    out = p ^ ((state >> 8) & 0xFF)
    mode = state % 3
    if mode == 0:
        out = ((out >> 1) & 0x55) | ((out & 0x55) << 1)
    elif mode == 1:
        out = ((out >> 2) & 0x33) | ((out & 0x33) << 2)
    else:
        out = ((out >> 4) & 0x0F) | ((out & 0x0F) << 4)
    return out
```

Alur enkripsinya adalah :
1. Setiap byte plaintext `p` dienkripsi dengan XOR terhadap `(state >> 8) & 0xFF`. 
2. Hasil XOR ini kemudian dimodifikasi oleh bit swap sesuai dengan mode `(state % 3)`. 
3. Mode `0` melakukan pertukaran bit per pasangan (mask 0xAA). 
4. Mode `1` melakukan pertukaran blok 2-bit (mask 0xCC). 
5. Mode `2` menukar nibbles tinggi dan rendah (mask 0xF0). 

Operasi swap ini bersifat, apabila dilakukan dua kali hasilnya kembali ke nilai semula.

```python
INITIAL_STATE = random.randint(0, 2**27)

def update_state(current_state, plain_char_ord):
    return (A * current_state + plain_char_ord) % M
```

State diperbarui mengikuti formula LCG: `state_{i+1} = (69069 * state_i + ord(p_i)) mod 2^32`. Initial state dibatasi hanya sampai `2^27`, sehingga ruang pencarian bisa disaring.

Dengan menggunakan format flag `NCLPS1{`, maka byte-byte awal dapat digunakan untuk memfilter kandidat initial state. Setiap kandidat diverifikasi dengan membandingkan hasil dekripsi ciphertext dengan prefix flag yang diketahui. Strategi dekripsi dimulai dengan menebak prefix flag. Pada setiap byte, ciphertext di-*unswap* sesuai mode, kemudian di-XOR dengan `((state >> 8) & 0xFF)`. State diperbarui dengan rumus LCG, dan proses ini diulang hingga seluruh ciphertext diproses. Akhirnya plaintext diverifikasi dengan hash SHA-256 yang sesuai. Untuk implementasinya adalah solver berikut ini:

```python
from hashlib import sha256

def unswap(b, mode):
    if mode == 0:
        return ((b >> 1) & 0x55) | ((b & 0x55) << 1)
    elif mode == 1:
        return ((b >> 2) & 0x33) | ((b & 0x33) << 2)
    else:
        return ((b >> 4) & 0x0F) | ((b & 0x0F) << 4)

def decrypt(ct, state):
    pt = b''
    for c in ct:
        mode = state % 3
        c = unswap(c, mode)
        p = c ^ ((state >> 8) & 0xFF)
        pt += bytes([p])
        state = (69069 * state + p) % (1 << 32)
    return pt

ciphertext = bytes.fromhex("d0e3094ebed1f12ac681efe295f3b16d8047b9d51f0dd1a322f0d0a8df9c68f62778987611e9cade7b76946a994c44db")
TARGET_HASH = "781ea8ef7526f9e0abf2362a30ebf1e46ada7ed0dfd4dd55321d4a6baef4cd49"

for s in range(1 << 27):
    pt = decrypt(ciphertext, s)
    if pt.startswith(b'NCLPS1{'):
        if sha256(pt).hexdigest() == TARGET_HASH:
            print("FLAG:", pt.decode(errors="ignore"))
            print("state0 =", s)
            break
```

Dari solver diatas, karena proses pencariannya cukup lama saya minta GPT buat optimasi agar pencariannya lebih cepat dan kode solvernya jadi seperti berikut :

```python
CT = bytes.fromhex("d0e3094ebed1f12ac681efe295f3b16d8047b9d51f0dd1a322f0d0a8df9c68f62778987611e9cade7b76946a994c44db")
PREFIX = b"NCLPS1{"

def unswap(b, m):
    return ((b>>1)&0x55)|((b&0x55)<<1) if m==0 else ((b>>2)&0x33)|((b&0x33)<<2) if m==1 else ((b>>4)&0x0F)|((b&0x0F)<<4)

def decrypt(ct, s):
    out=[]
    for c in ct:
        m=s%3; p=unswap(c,m)^((s>>8)&0xFF)
        out.append(p); s=(69069*s+p)&0xFFFFFFFF
    return bytes(out)

for m in (0,1,2):
    xor0 = PREFIX[0]^unswap(CT[0],m)
    for hi in range(1<<11):
        base=(hi<<16)|(xor0<<8)
        for lo in range(256):
            s0=base|lo
            if s0%3==m and decrypt(CT[:len(PREFIX)],s0)==PREFIX:
                flag=decrypt(CT,s0).decode()
                print(flag); exit()
```

### Flag

NCLPS1{gerbang_logika_dengan_sedikit_bumbu_lcg_}

