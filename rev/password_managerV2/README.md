## Password Manager v2
**Difficulty:** Hard-Insane
**Author:** moonetics

### Deskripsi
VaultBox adalah aplikasi password manager Windows untuk menyimpan kredensial. Aplikasi berjalan offline, mendukung perubahan lokasi vault folder, dan menyediakan generator password.

TL;DR
Setel Master Password saat membuka aplikasi.
Item disimpan satu-file-per-entry di folder vault (.nclp).
Format file memiliki header + ciphertext + HMAC.
Urutan proteksi data: PBKDF2 → AES-256-CBC → Rotator (bit-rotate) → XOR keystream → HMAC.
Master dapat dipulihkan secara lokal (tidak butuh jaringan).

Hint
Magic bytes: NCLP
Kunci diturunkan dengan PBKDF2 bawaan .NET Framework (Rfc2898DeriveBytes) default = HMAC-SHA1.
Rounds yang ditulis di header bisa “lebih besar” daripada yang dipakai; implementasi melakukan clamp ke nilai tertentu untuk performa (perhatikan kode).
Verifikasi HMAC-SHA256 atas header||ciphertext.
XOR keystream: blok 32-byte dari HMAC-SHA256(K_xor, counter_le).
Gate UI melakukan XOR(0x5A) → SHA-256 → Base64 (di-obfuscate) untuk validasi.
Increment PCG32 hanya tersimpan 40-bit bawah; 24-bit atas disembunyikan → brute-force ruang 2^24.

### Solution
Setelah memuat `vaultbox.exe` dapat diketahui bahwa program melakukan parser header file `NclpHeader`, melakukan read/write file `NclpFile`, derive key `Kdf.DeriveKeys`, XOR keystream `XorKeystream.Apply`,  rotator `Rotator`, AES wrapper `AesCipher`, dan gate validasi `MasterGate`.

```csharp
// vaultbox, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null
// VaultBox.WinForms.Storage.NclpHeader
using System.IO;
using VaultBox.WinForms.Storage;

public class NclpHeader
{
	public static readonly byte[] Magic = new byte[4] { 78, 67, 76, 80 };

	public byte Version { get; set; } = 1;

	public byte[] Salt { get; set; } = new byte[16];

	public byte[] IV { get; set; } = new byte[16];

	public int KdfRoundsDeclared { get; set; } = 500000;

	public byte RotationSeed { get; set; } = 55;

	public byte[] SerializeMeta()
	{
		using MemoryStream memoryStream = new MemoryStream();
		using BinaryWriter binaryWriter = new BinaryWriter(memoryStream);
		binaryWriter.Write(Magic);
		binaryWriter.Write(Version);
		binaryWriter.Write((byte)Salt.Length);
		binaryWriter.Write((byte)IV.Length);
		binaryWriter.Write(Salt);
		binaryWriter.Write(IV);
		binaryWriter.Write(KdfRoundsDeclared);
		binaryWriter.Write(RotationSeed);
		return memoryStream.ToArray();
	}

	public static NclpHeader Parse(BinaryReader br)
	{
		byte[] array = br.ReadBytes(4);
		if (array.Length != 4 || array[0] != Magic[0] || array[1] != Magic[1] || array[2] != Magic[2] || array[3] != Magic[3])
		{
			throw new InvalidDataException("Invalid magic");
		}
		NclpHeader obj = new NclpHeader
		{
			Version = br.ReadByte()
		};
		byte count = br.ReadByte();
		byte count2 = br.ReadByte();
		obj.Salt = br.ReadBytes(count);
		obj.IV = br.ReadBytes(count2);
		obj.KdfRoundsDeclared = br.ReadInt32();
		obj.RotationSeed = br.ReadByte();
		return obj;
	}
}
```

Header `.nclp` mulai dengan magic `b"NCLP"` kemudian field variabel: versi (1 byte), salt length (1), iv length (1), salt (saltLen), iv (ivLen), `KdfRoundsDeclared` (Int32 LE), dan `RotationSeed` (1). `SerializeMeta()` menghasilkan barisan ini; `Parse()` membacanya kembali.

```csharp
// vaultbox, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null
// VaultBox.WinForms.Crypto.Kdf
using System.Security.Cryptography;

public static class Kdf
{
	private const int ClampRounds = 100000;

	public static void DeriveKeys(string master, byte[] salt, int roundsDeclared, out byte[] kMain, out byte[] kMac, out byte[] kXor)
	{
		int num = roundsDeclared;
		if (num > 100000)
		{
			num = 100000;
		}
		using (Rfc2898DeriveBytes rfc2898DeriveBytes = new Rfc2898DeriveBytes(master, salt, num))
		{
			kMain = rfc2898DeriveBytes.GetBytes(32);
		}
		using (Rfc2898DeriveBytes rfc2898DeriveBytes2 = new Rfc2898DeriveBytes(master, salt, num / 2))
		{
			kMac = rfc2898DeriveBytes2.GetBytes(32);
		}
		using Rfc2898DeriveBytes rfc2898DeriveBytes3 = new Rfc2898DeriveBytes(master, salt, num / 4);
		kXor = rfc2898DeriveBytes3.GetBytes(32);
	}
}
```

KDF mengimplementasi tiga derivasi PBKDF2‑HMAC‑SHA1: `kMain = PBKDF2(master, salt, rounds')` (32 B), `kMac = PBKDF2(master, salt, rounds'/2)` (32 B), `kXor = PBKDF2(master, salt, rounds'/4)` (32 B) dengan `rounds' = min(declared, 100000)`.

Urutan proteksi file yang diambil dari `NclpFile.Write` dan `NclpFile.Read` adalah:

```
Plaintext -> gzip -> AES-256-CBC/PKCS7 (kMain, IV) -> per-byte LEFT rotate (seed + index) % 8 -> XOR keystream (HMAC-SHA256(kXor, LE32 counter)) -> write header || cipher || HMAC-SHA256(kMac, header||cipher)
```

```csharp
// vaultbox, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null
// VaultBox.WinForms.Crypto.XorKeystream
using System;
using System.Security.Cryptography;

public static class XorKeystream
{
	public static byte[] Apply(byte[] input, byte[] kXor)
	{
		byte[] array = new byte[input.Length];
		int num = 0;
		int num2 = 0;
		using HMACSHA256 hMACSHA = new HMACSHA256(kXor);
		while (num2 < input.Length)
		{
			byte[] bytes = BitConverter.GetBytes(num);
			byte[] array2 = hMACSHA.ComputeHash(bytes);
			int num3 = Math.Min(array2.Length, input.Length - num2);
			for (int i = 0; i < num3; i++)
			{
				array[num2 + i] = (byte)(input[num2 + i] ^ array2[i]);
			}
			num2 += num3;
			num++;
		}
		return array;
	}
}
```

XOR keystream dibuat oleh `HMACSHA256(kXor)` terhadap counter 32‑bit little-endian yang mulai dari 0; setiap blok HMAC memberi 32 byte keystream yang kemudian dipotong jika akhir data.

```csharp
// vaultbox, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null
// VaultBox.WinForms.Crypto.Rotator
public static class Rotator
{
	public static byte[] Rotate(byte[] input, byte seed)
	{
		byte[] array = new byte[input.Length];
		for (int i = 0; i < input.Length; i++)
		{
			int num = ((seed + i) & 0xFF) % 8;
			byte b = input[i];
			array[i] = (byte)((b << num) | (b >> 8 - num));
		}
		return array;
	}

	public static byte[] Unrotate(byte[] input, byte seed)
	{
		byte[] array = new byte[input.Length];
		for (int i = 0; i < input.Length; i++)
		{
			int num = ((seed + i) & 0xFF) % 8;
			byte b = input[i];
			array[i] = (byte)((b >> num) | (b << 8 - num));
		}
		return array;
	}
}
```

Rotator memutar bit tiap byte: `r = ((seed + i) & 0xFF) % 8` lalu `out[i] = (in[i] << r) | (in[i] >> (8-r))`.

```csharp
// vaultbox, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null
// VaultBox.WinForms.Crypto.AesCipher
using System.IO;
using System.Security.Cryptography;

public static class AesCipher
{
	public static byte[] Encrypt(byte[] plaintext, byte[] key, byte[] iv)
	{
		using Aes aes = Aes.Create();
		aes.KeySize = 256;
		aes.BlockSize = 128;
		aes.Mode = CipherMode.CBC;
		aes.Padding = PaddingMode.PKCS7;
		aes.Key = key;
		aes.IV = iv;
		using MemoryStream memoryStream = new MemoryStream();
		using CryptoStream cryptoStream = new CryptoStream(memoryStream, aes.CreateEncryptor(), CryptoStreamMode.Write);
		cryptoStream.Write(plaintext, 0, plaintext.Length);
		cryptoStream.FlushFinalBlock();
		return memoryStream.ToArray();
	}

	public static byte[] Decrypt(byte[] ciphertext, byte[] key, byte[] iv)
	{
		using Aes aes = Aes.Create();
		aes.KeySize = 256;
		aes.BlockSize = 128;
		aes.Mode = CipherMode.CBC;
		aes.Padding = PaddingMode.PKCS7;
		aes.Key = key;
		aes.IV = iv;
		using MemoryStream memoryStream = new MemoryStream();
		using CryptoStream cryptoStream = new CryptoStream(memoryStream, aes.CreateDecryptor(), CryptoStreamMode.Write);
		cryptoStream.Write(ciphertext, 0, ciphertext.Length);
		cryptoStream.FlushFinalBlock();
		return memoryStream.ToArray();
	}
}
```

AES adalah `KeySize=256, Mode=CBC, Padding=PKCS7`.

```csharp
// vaultbox, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null
// VaultBox.WinForms.Core.Security.MasterGate
using System;
using System.Security.Cryptography;
using System.Text;

public static class MasterGate
{
	private static readonly string ObfuscatedRef = "=cEv0idwwkv0idXoCv0idmKav0idWGTv0idEa+v0id/rlv0idNsDv0idrQev0id9Oav0idsFZv0id8bXv0idMtkv0idB3wv0ides";

	private const byte GateKey = 90;

	private const ulong SeedObf = 6602474991779635733uL;

	private const ulong SeedMask = 11936128518282651045uL;

	private const ulong IncLower40 = 848745626173uL;

	private static readonly string RecoveryBlobB64 = "GU651+ldtMsYHW9JoL7KNAravLfQJg==";

	public static bool Validate(string input)
	{
		try
		{
			string a = Reverse(Deinterleave(ObfuscatedRef, "v0id"));
			string b = Sha256Base64(XorUtf8(input, 90));
			return SlowEquals(a, b);
		}
		catch
		{
			return false;
		}
	}

	public static string TryRecoverWithTop24(uint top24)
	{
		ulong seed = DeobfuscateSeed();
		ulong inc = ((ulong)(top24 & 0xFFFFFF) << 40) | 0xC59D2E7A3DL;
		byte[] array = Convert.FromBase64String(RecoveryBlobB64);
		byte[] array2 = PcgKeystream(seed, inc, array.Length);
		byte[] array3 = new byte[array.Length];
		for (int i = 0; i < array.Length; i++)
		{
			array3[i] = (byte)(array[i] ^ array2[i]);
		}
		return Encoding.UTF8.GetString(array3);
	}

	private static byte[] PcgKeystream(ulong seed, ulong inc, int nbytes)
	{
		ulong state = 0uL;
		ulong mul = 6364136223846793005uL;
		ulong incval = (inc << 1) | 1;
		Step();
		state += seed;
		Step();
		byte[] array = new byte[nbytes];
		int num = 0;
		while (num < nbytes)
		{
			ulong num2 = state;
			Step();
			uint num3 = (uint)(((num2 >> 18) ^ num2) >> 27);
			uint num4 = (uint)(num2 >> 59);
			uint num5 = (num3 >> (int)num4) | (num3 << (int)((0L - (long)num4) & 0x1F));
			if (num < nbytes)
			{
				array[num++] = (byte)(num5 & 0xFF);
			}
			if (num < nbytes)
			{
				array[num++] = (byte)((num5 >> 8) & 0xFF);
			}
			if (num < nbytes)
			{
				array[num++] = (byte)((num5 >> 16) & 0xFF);
			}
			if (num < nbytes)
			{
				array[num++] = (byte)((num5 >> 24) & 0xFF);
			}
		}
		return array;
		void Step()
		{
			state = state * mul + incval;
		}
	}

	private static ulong DeobfuscateSeed()
	{
		return 10309554068971027553uL;
	}

	public static string GenerateReferenceHash(string master)
	{
		return Interleave(Reverse(Sha256Base64(XorUtf8(master, 90))), "v0id");
	}

	private static byte[] XorUtf8(string s, byte key)
	{
		byte[] bytes = Encoding.UTF8.GetBytes(s);
		for (int i = 0; i < bytes.Length; i++)
		{
			bytes[i] ^= key;
		}
		return bytes;
	}

	private static string Sha256Base64(byte[] data)
	{
		using SHA256 sHA = SHA256.Create();
		return Convert.ToBase64String(sHA.ComputeHash(data));
	}

	private static string Reverse(string s)
	{
		char[] array = s.ToCharArray();
		Array.Reverse(array);
		return new string(array);
	}

	private static string Interleave(string s, string salt)
	{
		StringBuilder stringBuilder = new StringBuilder();
		for (int i = 0; i < s.Length; i++)
		{
			stringBuilder.Append(s[i]);
			if (i % 3 == 2)
			{
				stringBuilder.Append(salt);
			}
		}
		return stringBuilder.ToString();
	}

	private static string Deinterleave(string s, string salt)
	{
		return s.Replace(salt, string.Empty);
	}

	private static bool SlowEquals(string a, string b)
	{
		if (a == null || b == null || a.Length != b.Length)
		{
			return false;
		}
		int num = 0;
		for (int i = 0; i < a.Length; i++)
		{
			num |= a[i] ^ b[i];
		}
		return num == 0;
	}
}
```

MasterGate menghitung `candidate_hash = Base64(SHA256(XOR_UTF8(master, 0x5A)))` dan membandingkan dengan konstanta yang di‑obfuscate. Ada juga fungsi tersembunyi `TryRecoverWithTop24(uint)` yang menggunakan PCG32 untuk mendekripsi `RecoveryBlobB64` dengan increment yang menggabungkan 24‑bit teratas. Karena lower 40 bit increment tetap, hanya 24‑bit yang perlu di‑brute force.

Setelah master diketahui, dekripsi `.nclp` dapat dilakukan dengan: turunkan tiga kunci PBKDF2 (sesuai clamp), verifikasi `HMAC-SHA256(kMac, header||cipher)` byte‑per‑byte, lalu urutkan balikan: XOR‑keystream -> unrotate -> AES‑CBC decrypt -> gunzip.

Pertama, brute‑force recovery dengan skrip berikut yang berhenti ketika master ditemukan dan memverifikasinya dengan fungsi gate yang identik dengan aplikasi:

```python
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
```

Master ditemukan pada `0x370000` dan nilainya adalah `master='orbit_fluorescent#2025'`.

Setelah master diperoleh, langkah dekripsinya: masukkan `MASTER` & `VAULT_DIR` di bagian atas skrip, lalu jalankan. Skrip membaca setiap `.nclp`, memparsing header, memverifikasi HMAC, membalik transformasi, lalu melakukan gunzip decompress dan menampilkan plaintext. Untuk implementasinya adalah solver berikut ini:

```python
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
```

### Flag
NCLPS1{PBKDF2_&&_pCg32_40_b1t_1ncR3m3Nt_t0p24_h1d3_r3COv3r3d_thEn_VauLt_decrYpt3d_a21d1d6a82}
