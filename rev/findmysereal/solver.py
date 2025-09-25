cipher = bytes.fromhex(
    "93 32 d3 50 35 d6 dc f7 93 b1 bc b7 f4 b1 92 5c f4 93 d6 b1 f7 3c f5".replace(" ", "")
)
rol8 = lambda v, r: ((v << r) & 0xff) | (v >> (8 - r))
flag = bytes(rol8(b ^ 0x5A, 3) for b in cipher).decode()
print(flag)