from math import isqrt
from sympy import factorint, mod_inverse
from Crypto.Util.number import long_to_bytes

n  = 482334770038158502104509019645301481449088150613131321272064999
e  = 65537
c  = 217030574813581748876560164628956728965229484123293220878296186
n2 = 568758980618471233824985353927557
cS = 194122074286685911567008750253330

# 1) faktorkan n2 lalu dapat d2
f = factorint(n2)
p2, q2 = list(f.keys())
phi2 = (p2-1)*(q2-1)
d2 = mod_inverse(e, phi2)

# 2) dekripsi S
S = pow(cS, d2, n2)

# 3) pecahkan p,q dari S dan n
D = S*S - 4*n
r = isqrt(D); assert r*r == D
p = (S - r)//2
q = (S + r)//2

# 4) dekripsi c
phi = (p-1)*(q-1)
d = mod_inverse(e, phi)
m = pow(c, d, n)
print(long_to_bytes(m))
