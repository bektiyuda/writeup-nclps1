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