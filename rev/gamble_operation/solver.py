import struct

CORE = "coredmp"
enc  = "encrypted_flag.idn"

with open(CORE, "rb") as f:
    core = f.read()
assert core[:4] == b"\x7fELF" and core[4] == 2
endi = "<"  # little endian

# ELF header
(e_type, e_machine, e_version, e_entry, e_phoff, e_shoff,
 e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = struct.unpack(
    endi+"HHIQQQIHHHHHH", core[16:64])

phdrs = []
for i in range(e_phnum):
    off = e_phoff + i*e_phentsize
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack(
        endi+"IIQQQQQQ", core[off:off+56])
    phdrs.append(dict(type=p_type, flags=p_flags, offset=p_offset, vaddr=p_vaddr, filesz=p_filesz, memsz=p_memsz))

def read_va(va, size):
    for ph in phdrs:
        if ph["type"] == 1:  # PT_LOAD
            start, end = ph["vaddr"], ph["vaddr"] + ph["memsz"]
            if start <= va < end:
                file_off = ph["offset"] + (va - start)
                return core[file_off:file_off+size]
    raise RuntimeError("VA di luar segmen PT_LOAD")

# parse NT_AUXV for BASE (AT_ENTRY - entrypoint_offset)
AT_ENTRY=None
for ph in phdrs:
    if ph["type"] != 4:  # PT_NOTE
        continue
    data = core[ph["offset"]:ph["offset"]+ph["filesz"]]
    off=0
    while off+12 <= len(data):
        namesz, descsz, ntype = struct.unpack(endi+"III", data[off:off+12])
        off += 12
        off += (namesz + 3) & ~3
        desc = data[off:off+descsz]
        off += (descsz + 3) & ~3
        if ntype == 6:  # NT_AUXV
            for i in range(0, len(desc), 16):
                a_type, a_val = struct.unpack(endi+"QQ", desc[i:i+16])
                if a_type == 9:  # AT_ENTRY
                    AT_ENTRY = a_val
                    break

if AT_ENTRY is None:
    raise RuntimeError("AT_ENTRY tidak ditemukan di NT_AUXV")

ENTRY_OFFSET = 0x1200
BASE = AT_ENTRY - ENTRY_OFFSET

# ambil pointer array g_key_store
G_KEY_STORE_OFF = 0x4030
ptr_tbl = read_va(BASE + G_KEY_STORE_OFF, 8)
g_key_store, = struct.unpack(endi+"Q", ptr_tbl)

ptrs = []
for i in range(0, 8*60, 8):
    p_bytes = read_va(g_key_store + i, 8)
    p, = struct.unpack(endi+"Q", p_bytes)
    if p == 0:
        break
    ptrs.append(p)

NUM_KEYS = 50
KEYLEN   = 128
assert len(ptrs) >= NUM_KEYS, f"Hanya {len(ptrs)} pointer, ekspektasi {NUM_KEYS}"
ptrs = ptrs[:NUM_KEYS]

keystream = bytearray(KEYLEN)
for p in ptrs:
    key = read_va(p, KEYLEN)
    for i, b in enumerate(key):
        keystream[i] ^= b

with open(enc, "rb") as f:
    ct = f.read()
pt = bytes(c ^ keystream[i % KEYLEN] for i, c in enumerate(ct))

try:
    print(pt.decode("utf-8"))
except UnicodeDecodeError:
    with open("decrypted.bin", "wb") as f:
        f.write(pt)
    print("[+] Plaintext biner tersimpan di decrypted.bin")