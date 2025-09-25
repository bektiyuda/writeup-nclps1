import base64, hashlib

# Konstanta dari MasterGate
SEED = 10309554068971027553 # DeobfuscateSeed()
INC_LOWER40 = 0x00C59D2E7A3D # IncLower40 (40-bit bawah)
BLOB_B64 = "GU651+ldtMsYHW9JoL7KNAravLfQJg=="
GATE_KEY = 0x5A
REF_HASH = "sew3BktMXb8ZFsaO9eQrDsNlr/+aETGWaKmCoXkwwEc=" # (target gate-hash)

def gate_hash(s: str) -> str:
    b = s.encode("utf-8")
    b = bytes([x ^ GATE_KEY for x in b]) # XOR(0x5A)
    return base64.b64encode(hashlib.sha256(b).digest()).decode()

def pcg_keystream(seed: int, inc: int, nbytes: int) -> bytes:
    state = 0
    mul = 6364136223846793005
    incval = (inc << 1) | 1
    def step():
        nonlocal state
        state = (state * mul + incval) & ((1 << 64) - 1)
    step()
    state = (state + seed) & ((1 << 64) - 1)
    step()
    out = bytearray(nbytes); i = 0
    while i < nbytes:
        s = state; step()
        xorshifted = ((s >> 18) ^ s) >> 27
        rot = (s >> 59) & 0xFFFFFFFF
        r = ((xorshifted >> rot) | ((xorshifted << ((-rot) & 31)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        for shift in (0, 8, 16, 24):
            if i < nbytes:
                out[i] = (r >> shift) & 0xFF
                i += 1
    return bytes(out)

def try_recover_with_top24(top24: int) -> str:
    inc = ((top24 & 0xFFFFFF) << 40) | INC_LOWER40
    blob = base64.b64decode(BLOB_B64)
    ks = pcg_keystream(SEED, inc, len(blob))
    plain = bytes(a ^ b for a, b in zip(blob, ks))
    return plain.decode("utf-8", errors="ignore")

def main():
    for t in range(1 << 24):
        cand = try_recover_with_top24(t)
        if gate_hash(cand) == REF_HASH:
            print(f"Found top24=0x{t:06X}  master='{cand}'")
            print(f"Verify gate={gate_hash(cand)}")
            return
        if (t & 0xFFFF) == 0:
            print(f"\rscan 0x{t:06X}")
    print("\n[!] not found")

if __name__ == "__main__":
    main()
