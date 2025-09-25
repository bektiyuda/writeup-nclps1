blob_hex = "c29d180f717b171f71be38983d16400cdeded64ad495a4e98f498a37202a51857e79c427b32dc0f233e5999b56c67219beddb32d1150f095e11018d1399f10c4049f2c44db0e3037a46a316dc3d01f6c8108ccc623b70e466930db58285d4f188cf13cb3c563935d33122900"
blob = bytes.fromhex(blob_hex)
assert len(blob) == 108

def recover(blob):
    out = []
    eax = 0x0c0ffee5
    for i in range(0x6b):
        esi = (0xffffffc2 & 0xffffffff) if i == 0 else blob[i]
        ecx = eax
        ecx = ((ecx << 13) & 0xffffffff) ^ ecx
        ecx = (ecx ^ (ecx >> 17)) & 0xffffffff
        eax = ((ecx << 5) & 0xffffffff) ^ ecx
        byte = (eax ^ i ^ esi) & 0xff
        out.append(byte)
    return bytes(out)

print(recover(blob).decode())
