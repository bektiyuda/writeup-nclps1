## Gamble Operation
**Difficulty:** Medium
**Author:** moonetics

### Description
A secret agent has just completed a crucial mission, successfully infiltrating an enemy lair and obtaining vital intelligence data. To ensure the confidentiality of the data, he uses a special encryption program designed to be highly secure. The program claims to use a multi-layered encryption technique with a randomly generated key for each session, ensuring no two encryptions are the same.

However, in the middle of writing the encrypted data to disk, an unexpected incident occurred that caused the agent's system to crash. Fortunately, he was able to recover some artifacts from the crashed system.

Your task is that of a reverse engineering expert. Using the available artifacts, you must recover the original hidden intelligence data.

### Solution
```c
void initialize_keys(int num_keys,int key_len)

{
  char **ppcVar1;
  char *pcVar2;
  ssize_t sVar3;
  int key_len_local;
  int num_keys_local;
  int i;
  int j;
  int j_1;
  
  g_key_store = (char **)malloc((long)num_keys << 3);
  if (g_key_store == (char **)0x0) {
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  i = 0;
  while( true ) {
    if (num_keys <= i) {
      return;
    }
    ppcVar1 = g_key_store + i;
    pcVar2 = (char *)malloc((long)key_len);
    *ppcVar1 = pcVar2;
    if (g_key_store[i] == (char *)0x0) break;
    sVar3 = read(g_random_fd,g_key_store[i],(long)key_len);
    if (sVar3 != key_len) {
      for (j_1 = 0; j_1 <= i; j_1 = j_1 + 1) {
        free(g_key_store[j_1]);
      }
      free(g_key_store);
      g_key_store = (char **)0x0;
                    /* WARNING: Subroutine does not return */
      exit(1);
    }
    i = i + 1;
  }
  for (j = 0; j < i; j = j + 1) {
    free(g_key_store[j]);
  }
  free(g_key_store);
  g_key_store = (char **)0x0;
                    /* WARNING: Subroutine does not return */
  exit(1);
}
```

Decompile di Ghidra menampilkan fungsi `initialize_keys(num_keys, key_len)` mengalokasikan array pointer kunci di heap, lalu mengisi setiap kunci dari `/dev/urandom`. Dari konstanta pada call‑site terlihat `num_keys = 0x32` (50) dan `key_len = 0x80` (128). 

```c
void encrypt_data(uchar *data,int data_len,int num_keys,int key_len)

{
  int key_len_local;
  int num_keys_local;
  int data_len_local;
  uchar *data_local;
  int k;
  int i;
  
  if (g_key_store != (char **)0x0) {
    for (k = 0; k < num_keys; k = k + 1) {
      for (i = 0; i < data_len; i = i + 1) {
        data[i] = data[i] ^ g_key_store[k][i % key_len];
      }
    }
    puts("[-] Data encrypted.");
  }
  return;
}
```

Fungsi `encrypt_data(buf, len, num_layers, key_len)` melakukan XOR bertingkat: untuk setiap lapisan `i`, setiap byte `buf[j]` di‑XOR dengan `key[i][j % key_len]`. Karena XOR bersifat komutatif dan inversnya sendiri, seluruh lapisan ini ekuivalen dengan men‑XOR plaintext dengan **satu keystream gabungan** sepanjang 128 byte, yaitu XOR posisi‑per‑posisi dari 50 kunci. 

```c
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void create_memory_dump(void)

{
  long lVar1;
  uint uVar2;
  int iVar3;
  long in_FS_OFFSET;
  pid_t pid;
  char cmd [256];
  
  lVar1 = *(long *)(in_FS_OFFSET + 0x28);
  uVar2 = getpid();
  snprintf(cmd,0x100,"gcore -o temp_dump %d > /dev/null 2>&1 && mv temp_dump.%d coredmp",
           (ulong)uVar2,(ulong)uVar2);
  iVar3 = system(cmd);
  if (iVar3 == -1) {
    perror("[-] Failed to run gcore.");
  }
  if (lVar1 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}
```

Setelah menulis ciphertext, program memanggil pembuatan core dump (`create_memory_dump` -> `gcore`) sebelum proses benar‑benar mati.

Inti kelemahannya adalah **leakage kunci melalui core dump**. Semua lapisan hanyalah XOR dengan key chunk 128‑byte yang berbeda, keseluruhan lapisan collapse menjadi satu keystream gabungan sepanjang 128 byte: `KS[j] = key0[j] ^ key1[j] ^ … ^ key49[j]` untuk `j ∈ [0..127]`. Begitu core dump mengungkap seluruh konten heap yang menyimpan 50 kunci mentah, kita cukup menghitung XOR per posisi untuk membentuk keystream gabungan. Dekripsi ciphertext tinggal `PT[i] = CT[i] ^ KS[i % 128]`. Program sengaja memicu pembuatan core sehingga seluruh material rahasia tetap tertinggal.

Solver di bawah ini mem‑parsing ELF core, membaca program headers (PT\_LOAD/PT\_NOTE), mengekstrak `AT_ENTRY` dari `NT_AUXV`, menghitung BASE, membaca pointer `g_key_store` (offset global 0x4030), menelusuri 50 pointer kunci, melakukan XOR per posisi (128B), lalu mendekripsi `encrypted_flag.idn`.

```python
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
```

### Flag

NCLPS1{ay00_m3nujJu_t4akk_t3rbba4t4s_d4an_Mel4mp4uwii_e64b364595}
