T = int("""6708225246577317268201359870589947128321270453156893234886662491398921333524854484228506876784333764380835907785971649995603806504942718660141508646410278513251598900""")

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
    k = 1 << i   # 2**i
    cur = invert_xor_shift(cur, k, bitlen)

b = cur.to_bytes((cur.bit_length() + 7) // 8, "big")
print(b.decode(errors="replace"))
