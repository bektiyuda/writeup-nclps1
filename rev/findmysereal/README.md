## findmysereal

### Description
ayo cari aku cari aku, blob blob blob

### Solution

```c
  std::getline<>((istream *)&std::cin,(string *)&local_68,cVar4);
  piVar6 = __errno_location();
  *piVar6 = 0;
  lVar7 = ptrace(PTRACE_TRACEME,0,0,0);
  if (((int)lVar7 == -1) && (*piVar6 == 1)) {
    FUN_001015d0(std::cout,"Debugger detected - aborting.\n");
  }
```

* Timing Gate
```cpp
    lVar7 = std::chrono::_V2::system_clock::now();
    lVar8 = 0;
    do {
      lVar8 = lVar8 + 1;
    } while (lVar8 != 1200000);
    lVar8 = std::chrono::_V2::system_clock::now();
    if (lVar8 - lVar7 < 800000000) {
      if (local_68 == local_68 + local_60) {
LAB_00101309:
        FUN_001015d0(std::cout,"Invalid serial.\n");
      }
      else {
        uVar5 = 0x811c9dc5;
        pbVar10 = local_68;
        do {
          bVar1 = *pbVar10;
          pbVar10 = pbVar10 + 1;
          uVar3 = (uVar5 ^ bVar1) * 0x20003260;
          uVar5 = (uVar3 | (uVar5 ^ bVar1) * 0x1000193 >> 0x1b) ^ uVar3 >> 0xd;
        } while (pbVar10 != local_68 + local_60);
        if (uVar5 != 0x14530451) goto LAB_00101309;
        FUN_001015d0(std::cout,"Serial OK. Decrypting flag...\n");
        local_48 = local_38;
        local_38[0] = '\0';
        local_40 = 0;
                    /* try { // try from 001013c6 to 001013f6 has its CatchHandler @ 00101442 */
        std::string::reserve((ulong)&local_48);
        lVar8 = DAT_00104308;
        for (lVar7 = DAT_00104300; lVar7 != lVar8; lVar7 = lVar7 + 1) {
          std::string::push_back((char)&local_48);
        }
                    /* try { // try from 0010140d to 00101420 has its CatchHandler @ 0010144f */
        poVar9 = std::__ostream_insert<>((ostream *)std::cout,local_48,local_40);
        FUN_001015d0(poVar9,"\n");
        std::string::_M_dispose();
      }
      uVar11 = 0;
      goto LAB_0010131a;
    }
                    /* try { // try from 00101438 to 0010143c has its CatchHandler @ 0010144a */
    FUN_001015d0(std::cout,"Timing check failed - try again.\n");
```

Program meminta satu baris *serial*, menjalankan anti‑debug `ptrace(PTRACE_TRACEME)`, kemudian melakukan *timing gate* memakai `std::chrono::system_clock::now()` sebelum dan sesudah *busy loop* iterasi 1.200.000 kali; jika durasi melebihi ~0,8 detik, program menghentikan eksekusi. Setelah lolos, input di-*hash* memakai skema yang menyerupai FNV‑1a dan dibandingkan terhadap konstanta target.

* Custom Hash atas Serial

```c
      else {
        uVar5 = 0x811c9dc5;
        pbVar10 = local_68;
        do {
          bVar1 = *pbVar10;
          pbVar10 = pbVar10 + 1;
          uVar3 = (uVar5 ^ bVar1) * 0x20003260;
          uVar5 = (uVar3 | (uVar5 ^ bVar1) * 0x1000193 >> 0x1b) ^ uVar3 >> 0xd;
        } while (pbVar10 != local_68 + local_60);
        if (uVar5 != 0x14530451) goto LAB_00101309;
        FUN_001015d0(std::cout,"Serial OK. Decrypting flag...\n");
        local_48 = local_38;
        local_38[0] = '\0';
        local_40 = 0;
                    /* try { // try from 001013c6 to 001013f6 has its CatchHandler @ 00101442 */
        std::string::reserve((ulong)&local_48);
        lVar8 = DAT_00104308;
        for (lVar7 = DAT_00104300; lVar7 != lVar8; lVar7 = lVar7 + 1) {
          std::string::push_back((char)&local_48);
        }
                    /* try { // try from 0010140d to 00101420 has its CatchHandler @ 0010144f */
        poVar9 = std::__ostream_insert<>((ostream *)std::cout,local_48,local_40);
        FUN_001015d0(poVar9,"\n");
        std::string::_M_dispose();
      }
```

Inisialisasi memakai **offset basis FNV‑1a** `0x811c9dc5`, kemudian dikombinasi dua perkalian dan operasi bit. Jika *hash* cocok, program menampilkan pesan "Serial OK. Decrypting flag..." lalu membentuk string keluaran dari sebuah rentang data global di heap.

```c
void _INIT_1(void)

{
  DAT_00104310 = 0;
  _DAT_00104300 = (undefined1  [16])0x0;
                    /* try { // try from 0010147c to 00101480 has its CatchHandler @ 001014cb */
  DAT_00104300 = (undefined8 *)operator.new(0x17);
  DAT_00104310 = (long)DAT_00104300 + 0x17;
  *DAT_00104300 = 0xf7dcd63550d33293;
  DAT_00104300[1] = 0x5c92b1f4b7bcb193;
  *(undefined8 *)((long)DAT_00104300 + 0xf) = 0xf53cf7b1d693f45c;
  DAT_00104308 = (long)DAT_00104300 + 0x17;
  __cxa_atexit(FUN_00101630,&DAT_00104300,&PTR_LOOP_00104088);
  return;
}
```

Pada *initializer* program mengisi buffer cipher di heap dengan 0x17 byte (23 byte) dan melakukan tiga penyimpanan 64‑bit yang saling tumpang tindih sehingga menghasilkan urutan byte bukan‑ASCII (ciphertext).  *loop* yang melakukan transformasi per‑byte sebelum *push_back*.

Setelah diproyeksikan dalam *little‑endian*, 23 byte yang terbentuk adalah: 93 32 d3 50 35 d6 dc f7 93 b1 bc b7 f4 b1 92 5c f4 93 d6 b1 f7 3c f5. Byte‑byte ini tidak bisa dibaca sebagai ASCII sehingga mustahil dicetak langsung sebagai flag.

```asm
001013e0  MOVZX ESI, byte ptr [R14]   ; load src byte
001013e4  MOV   RDI, R12              ; this = &std::string
001013e7  XOR   ESI, 0x5a             ; src ^= 0x5A
001013ea  ROL   SIL, 0x3              ; src = rotl8(src, 3)
001013ee  MOVSX ESI, SIL              ; sign-extend 8→32
001013f2  CALL  std::string::push_back(char)
```

Disasembly di body loop menunjukkan transformasi per‑byte sebelum dimasukkan ke `std::string`:.
Artinya, setiap output dihitung sebagai **`ROL8((cipher[i] ^ 0x5A), 3)`**. Dengan begitu, dapat dilakukan ekstraksi flagnya dengan solver berikut ini:

```python
cipher = bytes.fromhex(
    "93 32 d3 50 35 d6 dc f7 93 b1 bc b7 f4 b1 92 5c f4 93 d6 b1 f7 3c f5".replace(" ", "")
)
rol8 = lambda v, r: ((v << r) & 0xff) | (v >> (8 - r))
flag = bytes(rol8(b ^ 0x5A, 3) for b in cipher).decode()
print(flag)
```

### Flag
NCLP{d4mN_7ou_F0uNd_m3}
