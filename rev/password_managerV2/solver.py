MASTER = "orbit_fluorescent#2025"
VAULT_DIR = "vaultbox/vault"

import glob, io, os, struct, gzip, hashlib, hmac, sys
from Crypto.Cipher import AES

# same helpers
def _pbkdf2(master: str, salt: bytes, rounds_declared: int):
    eff = min(rounds_declared, 100_000)
    m = master.encode("utf-8")
    kMain = hashlib.pbkdf2_hmac("sha1", m, salt, max(eff, 1), dklen=32)
    kMac  = hashlib.pbkdf2_hmac("sha1", m, salt, max(eff // 2, 1), dklen=32)
    kXor  = hashlib.pbkdf2_hmac("sha1", m, salt, max(eff // 4, 1), dklen=32)
    return kMain, kMac, kXor

def _xor_keystream(data: bytes, kxor: bytes) -> bytes:
    out = bytearray(len(data)); pos = 0; ctr = 0
    while pos < len(data):
        ctr_le = struct.pack("<I", ctr)
        ks = hmac.new(kxor, ctr_le, hashlib.sha256).digest()
        n = min(32, len(data) - pos)
        for i in range(n):
            out[pos + i] = data[pos + i] ^ ks[i]
        pos += n; ctr += 1
    return bytes(out)

def _unrotate(buf: bytes, seed: int) -> bytes:
    out = bytearray(len(buf))
    for i, b in enumerate(buf):
        r = ((seed + i) & 0xFF) % 8
        out[i] = ((b >> r) | ((b << (8 - r)) & 0xFF)) & 0xFF
    return bytes(out)

def _pkcs7_unpad(b: bytes) -> bytes:
    if not b: raise ValueError("empty")
    n = b[-1]
    if n < 1 or n > 16 or b[-n:] != bytes([n])*n: raise ValueError("bad PKCS7")
    return b[:-n]

def _parse_header(f: io.BytesIO):
    if f.read(4) != b"NCLP":
        raise ValueError("bad magic")
    version = f.read(1)[0]
    salt_len = f.read(1)[0]
    iv_len   = f.read(1)[0]
    salt = f.read(salt_len)
    iv   = f.read(iv_len)
    rounds_declared = struct.unpack("<i", f.read(4))[0]
    rotation_seed   = f.read(1)[0]
    meta_len = f.tell()
    return version, salt, iv, rounds_declared, rotation_seed, meta_len

def decrypt(path: str, master: str) -> str:
    data = open(path, "rb").read()
    f = io.BytesIO(data)
    ver, salt, iv, rounds, rot, meta_len = _parse_header(f)

    if len(data) < meta_len + 32:
        raise ValueError("truncated")
    tag = data[-32:]
    ct  = data[meta_len:-32]

    kMain, kMac, kXor = _pbkdf2(master, salt, rounds)

    want = hmac.new(kMac, data[:meta_len] + ct, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, want):
        raise ValueError("HMAC mismatch")

    x = _xor_keystream(ct, kXor)
    x = _unrotate(x, rot)
    pt = AES.new(kMain, AES.MODE_CBC, iv).decrypt(x)
    pt = _pkcs7_unpad(pt)
    
    return gzip.decompress(pt).decode("utf-8", "replace")

def main():
    files = sorted(glob.glob(os.path.join(VAULT_DIR, "*.nclp")))
    
    for p in files:
        print(f"===== FILE: {os.path.basename(p)} =====")
        try:
            s = decrypt(p, MASTER)
            print(s, end="" if s.endswith("\n") else "\n")
        except Exception as e:
            print(f"[ERROR] {e}")
        print()

if __name__ == "__main__":
    main()
