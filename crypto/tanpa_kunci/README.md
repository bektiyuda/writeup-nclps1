## tanpa kunci
**Difficulty:** Easy-Medium
**Author:** n4siKvn1ng

### Description
Bisakah recover flag tanpa diberikan key? sebelum eksekusi tela'ah dulu, apa sih yang bisa diexploitasi

### Solution
```python
FLAG = "NCLPS1{REDACTED}"
KEY = "" # REDACTED

def xor_cipher(data, key):
    data_bytes = data.encode('utf-8')
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)
    
    result = bytearray()
    
    for i, byte in enumerate(data_bytes):
        key_byte = key_bytes[i % key_len]
        
        xored_byte = byte ^ key_byte
        result.append(xored_byte)
        
    return bytes(result)

if __name__ == "__main__":
    encrypted_flag = xor_cipher(FLAG, KEY)
    encrypted_hex = encrypted_flag.hex()
    
    print(f"Encrypted: {encrypted_hex}")
```

Pada source codenya dapat diketahui bahwa fungsi `xor_cipher` melakukan XOR byte‑per‑byte antara `data_bytes` dan key. Selain itu, pada `key_bytes[i % key_len]`,  satu byte kunci digunakan berulang pada indeks yang kongruen modulo panjang kunci. 

Dengan format flag **NCLPS1{}**, *known plaintext* dapat diketahui. Jika sebagian plaintext diketahui, maka `key[i % L] = ct[i] XOR pt[i]`. Dengan mengumpulkan cukup banyak posisi i untuk tiap `i % L`, kita dapat menebak dan memverifikasi panjang kunci L.

Solusinya adalah konversi hex ke bytes lalu asumsikan panjang kunci L dalam rentang yang wajar (mis. 1–63).Gunakan `NCLPS1{` pada indeks 0 - 6, dan `}` pada indeks terakhir, untuk menghitung kandidat byte kunci pada posisi modulo L. Cek konsistensi, jika satu kelas kongruensi menghasilkan dua nilai berbeda, maka tolak L tersebut. Dekripsi penuh dan validasi, apakah output diawali `NCLPS1{`, berakhiran `}`, seluruh byte ASCII cetak. Untuk implementasinya adalah solver berikut ini:

```python
import string

HEX_CT = "3d700f2260655a07072d02070b4a404a1c10463f151d6c2e4640604d475b1c0100381514021c02073a4b475d242d43261215023b2d40604c476c27415d33151d6c33465d3e151d541c19002d5c"
ct = bytes.fromhex(HEX_CT)

known_prefix = b"NCLPS1{"
known = {i: known_prefix[i] for i in range(len(known_prefix))}
known[len(ct)-1] = ord("}")

def try_len(L):
    key = {}
    for i, pb in known.items():
        kb = ct[i] ^ pb
        j = i % L
        if j in key and key[j] != kb:
            return None, None
        key[j] = kb
    # plaintext (pakai '?' buat yg not found)
    pt = bytearray()
    for i, b in enumerate(ct):
        kpos = i % L
        pt.append(b ^ key[kpos] if kpos in key else ord("?"))
    return bytes(pt), bytes(key.get(i, 0) for i in range(L))

best = None
for L in range(1, 64):
    pt, key = try_len(L)
    if pt is None:
        continue
    if pt.startswith(known_prefix) and pt.endswith(b"}") and all(32 <= c <= 126 for c in pt):
        best = (L, pt, key)
        break

if not best:
    raise SystemExit("Gagal menemukan key")

L, pt, key = best
print("Key length:", L)
print("Key:", key.decode('utf-8', errors='ignore'))
print("Flag:", pt.decode())
```

### Flag 
NCLPS1{t4np4_k3y_buk4n_m4s4l4h_s3l4g1_p4nj4ng_pr3f1x_s4m4_d3ng4n_p4nj4ng_k3y}