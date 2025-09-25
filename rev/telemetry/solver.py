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