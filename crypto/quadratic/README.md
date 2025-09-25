## quadratic

**Difficulty:** Medium

**Author:** n4siKvn1ng

### Description

Kriptografi berbeda dengan Cryptocurrency/Blockchain, tetapi yang mendasari Cryptocurrency adalah kriptografi. Dasar chall untuk kripto memanglah matematika, ini adalah salah satu implementasinya dengan sedikit bumbu rsa dasar.

### Solution

```python
from Crypto.Util.number import getPrime, bytes_to_long

BITS_1 = 105
BITS_2 = 55
e = 65537
FLAG = b"NCLPS1{REDACTED}"

p = getPrime(BITS_1)
q = getPrime(BITS_1)
n = p * q
S = p + q
m = bytes_to_long(FLAG)
c = pow(m, e, n)

p2 = getPrime(BITS_2)
q2 = getPrime(BITS_2)
n2 = p2 * q2
phi2 = (p2 - 1) * (q2 - 1)
while phi2 % e == 0:
    p2 = getPrime(BITS_2)
    q2 = getPrime(BITS_2)
    n2 = p2 * q2
    phi2 = (p2 - 1) * (q2 - 1)

c_S = pow(S, e, n2)

print(f"n = {n}")
print(f"e = {e}")
print(f"c = {c}")
print(f"n2 = {n2}")
print(f"c_S = {c_S}")
```

Pada source code terlihat bahwa enkripsi menggunakan RSA dengan modulus `n = p * q` dan eksponen `e = 65537`. Ciphertext merupakan hasil enkripsi flag. Namun terdapat tambahan berupa nilai `S = p + q` yang kemudian juga dienkripsi menggunakan modulus kedua `n2 = p2 * q2` yang jauh lebih kecil. Ciphertext dari nilai ini disebut `cS`.

```python
n  = 482334770038158502104509019645301481449088150613131321272064999
e  = 65537
c  = 217030574813581748876560164628956728965229484123293220878296186
n2 = 568758980618471233824985353927557
cS = 194122074286685911567008750253330
```

Fokus awal adalah pada `n2` yang relatif kecil. Dengan ukuran modulus seperti ini, faktorisasinya dapat dilakukan dengan cepat menggunakan algoritma faktorisasi umum. Begitu `n2` terfaktorkan, didapatkan private key kedua dan mendekripsi `cS` untuk mendapatkan nilai `S`. Dengan mengetahui jumlah `p` dan `q`, kita dapat menyusun persamaan kuadrat:

$x^2 - Sx + n = 0$

Alur dekripsinya adalah:

1. Faktorisasi `n2` -> didapatkan `p2` dan `q2`.
2. Hitung totient `phi2 = (p2-1)(q2-1)` dan invers modular `d2 = e^{-1} mod phi2`.
3. Dekripsi `S = pow(cS, d2, n2)`.
4. Pecahkan persamaan kuadrat $x^2 - Sx + n = 0$ untuk menemukan `p` dan `q`.
5. Gunakan `p` dan `q` untuk menghitung `phi(n)`, lalu dapatkan `d = e^{-1} mod phi(n)`.
6. Dekripsi ciphertext utama menjadi flag.

Untuk implementasinya adalah solver berikut ini:

```python
from math import isqrt
from sympy import factorint, mod_inverse
from Crypto.Util.number import long_to_bytes

n  = 482334770038158502104509019645301481449088150613131321272064999
e  = 65537
c  = 217030574813581748876560164628956728965229484123293220878296186
n2 = 568758980618471233824985353927557
cS = 194122074286685911567008750253330

# Faktorisasi n2
f = factorint(n2)
p2, q2 = list(f.keys())
phi2 = (p2-1)*(q2-1)
d2 = mod_inverse(e, phi2)

# Dekripsi S
S = pow(cS, d2, n2)

# Pecahkan p, q
D = S*S - 4*n
r = isqrt(D); assert r*r == D
p = (S - r)//2
q = (S + r)//2

# Dekripsi flag
phi = (p-1)*(q-1)
d = mod_inverse(e, phi)
m = pow(c, d, n)
print(long_to_bytes(m))
```

### Flag

NCLPS1{p3r$4m44n_kv4dr4t_}
