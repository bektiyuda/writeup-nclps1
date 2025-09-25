## License

**Difficulty:** Medium
**Author:** moonetics

### Description

A local software company has just released their digital product. This product can only be used after activation using an encrypted license file that will be generated if you can enter a valid “authorization code”. Their internal security team is quite confident that this protection system is safe enough from piracy because there is no flag directly in the binary

### Solution

```c
undefined8 main(void)

{
  int iVar1;
  undefined8 uVar2;
  size_t sVar3;
  long lVar4;
  void *__ptr;
  FILE *__s;
  long in_FS_OFFSET;
  int local_e4;
  char local_b8 [32];
  char local_98 [136];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  printf("Enter your 8-digit serial key: ");
  iVar1 = __isoc99_scanf(&DAT_00102038,local_b8);
  if (iVar1 == 1) {
    sVar3 = strlen(local_b8);
    if (sVar3 == 8) {
      for (local_e4 = 0; local_e4 < 8; local_e4 = local_e4 + 1) {
        if ((local_b8[local_e4] < '0') || ('9' < local_b8[local_e4])) {
          puts("Serial key hanya boleh angka.");
          uVar2 = 1;
          goto LAB_001017f2;
        }
      }
      lVar4 = custom_hash(local_b8);
      printf("custom_hash(\"%s\") = 0x%016llxULL\n",local_b8,lVar4);
      if (lVar4 == 0x5ad4f40b2b0a4f09) {
        iVar1 = read_flag(local_98,0x80);
        if (iVar1 == 0) {
          puts("Gagal membaca flag dari .env.");
          uVar2 = 1;
        }
        else {
          sVar3 = strlen(local_98);
          __ptr = malloc(sVar3);
          encrypt_flag(local_98,local_b8,__ptr,sVar3);
          __s = fopen("license.key","wb");
          if (__s == (FILE *)0x0) {
            puts("Gagal membuat license.key.");
            free(__ptr);
            uVar2 = 1;
          }
          else {
            fwrite(__ptr,1,sVar3,__s);
            fclose(__s);
            free(__ptr);
            puts("Serial valid. license.key berhasil dibuat!");
            uVar2 = 0;
          }
        }
      }
      else {
        puts("Serial key salah.");
        uVar2 = 1;
      }
    }
    else {
      puts("Serial key harus 8 digit angka.");
      uVar2 = 1;
    }
  }
  else {
    puts("Input error.");
    uVar2 = 1;
  }
LAB_001017f2:
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return uVar2;
}
```

Di Ghidra, membuka `license` menampilkan fungsi `main` yang mengambil input dari stdin, mengecek panjang/karakter (delapan digit sering kali menjadi pola umum), lalu dilakukan sebuah **custom hash** atas serial dan dibandingkan terhadap sebuah **konstanta 64‑bit yang di-hard‑code**. Jika sama, eksekusi berlanjut ke penulisan `license.key` dengan cara mengenkripsi plaintext internal menggunakan **XOR berulang (8‑byte key repeated)**. Pola ini terdeteksi dari loop sederhana yang meng‑XOR setiap byte plaintext dengan byte ke‑`i mod 8` dari nilai 64‑bit hasil hash/konstanta.

Dengan hadirnya **ciphertext** (`license.key`) yang dihasilkan dari key tersebut, dapat dilakukan dekripsi hanya dengan XOR ulang memakai **keystream yang sama**. Begitu keystream diketahui, dekripsi : `plaintext = ciphertext XOR keystream`. Karena keystream diulang per 8 byte, implementasi loop berukuran 8 juga memudahkan.

Tahapannya adalah mengambil **konstanta 64‑bit** dari biner (hasil reverse/Ghidra), konversi ke **8 byte little‑endian**, ulangi sepanjang panjang ciphertext, lalu **XOR** dengan `license.key` untuk memperoleh flag. Solver berikut adalah implementasinya :

```python
from pathlib import Path

KEY64 = 0x5ad4f40b2b0a4f09
KEY_BYTES = KEY64.to_bytes(8, 'little')

ct = Path('license.key').read_bytes()

pt = bytes(c ^ KEY_BYTES[i % 8] for i, c in enumerate(ct))

print(pt.decode())
```

### Flag

NCLPS1{i1'mM_s0rRy_m4ke_y0u_fe3lba4d_bBut_c0Ngr4ts_047d9db348}
