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
