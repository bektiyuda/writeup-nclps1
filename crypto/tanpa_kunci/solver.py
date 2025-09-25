import string

HEX_CT = "3d700f2260655a07072d02070b4a404a1c10463f151d6c2e4640604d475b1c0100381514021c02073a4b475d242d43261215023b2d40604c476c27415d33151d6c33465d3e151d541c19002d5c"
ct = bytes.fromhex(HEX_CT)

known_prefix = b"NCLPS1{"
known = {i: known_prefix[i] for i in range(len(known_prefix))}
known[len(ct)-1] = ord("}")

def try_len(L):
    key = {}
    for i, pb in known.items():
        kb = ct[i] ^ pb
        j = i % L
        if j in key and key[j] != kb:
            return None, None
        key[j] = kb
    # plaintext (pakai '?' buat yg not found)
    pt = bytearray()
    for i, b in enumerate(ct):
        kpos = i % L
        pt.append(b ^ key[kpos] if kpos in key else ord("?"))
    return bytes(pt), bytes(key.get(i, 0) for i in range(L))

best = None
for L in range(1, 64):
    pt, key = try_len(L)
    if pt is None:
        continue
    if pt.startswith(known_prefix) and pt.endswith(b"}") and all(32 <= c <= 126 for c in pt):
        best = (L, pt, key)
        break

if not best:
    raise SystemExit("Gagal menemukan key")

L, pt, key = best
print("Key length:", L)
print("Key:", key.decode('utf-8', errors='ignore'))
print("Flag:", pt.decode())