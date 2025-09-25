import struct

SEED = 0xCAC7CF84
OBF_ADDR = 0x2080
OBF_LEN  = 0x3C

stage2 = open('stage2.elf','rb').read()

RO_VADDR = 0x2000
RO_FILEOFF = 0x2000
obf_off = OBF_ADDR - RO_VADDR + RO_FILEOFF
obf = stage2[obf_off:obf_off+OBF_LEN]

def xs32(x):
    x &= 0xffffffff
    x ^= (x << 13) & 0xffffffff
    x ^= (x >> 17) & 0xffffffff
    x ^= (x << 5) & 0xffffffff
    return x & 0xffffffff

x = SEED
out = bytearray()
for b in obf:
    x = xs32(x)
    out.append(b ^ (x & 0xff))

print(out.decode())