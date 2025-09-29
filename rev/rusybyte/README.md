## rusybyte
**Difficulty:** Hard-Insane
**Author:** n4siKvn1ng

### Description
Apakah kalian pikir reverse chall hanya berupa c code? Bagaimana dengan chall sederhana ini, hope you find how the code is work :D

### Solution
Ketika menelusuri `chall.ll`, alur fungsi main adalah seperti berikut: 

```llvm
@alloc_27e20ab4610c44e7cd1ed777571a5eaa = private unnamed_addr constant [4 x i8] c"flag", align 1
```

1. Program membuka file literal berlabel `"flag"`, 

```llvm
; call std::fs::File::open
  %1 = call { i64, ptr } @_ZN3std2fs4File4open17hd6ef4275f7c3f694E(ptr align 1 @alloc_27e20ab4610c44e7cd1ed777571a5eaa, i64 4)
; invoke <std::fs::File as std::io::Read>::read_to_string
  %16 = invoke { i64, ptr } @...Read$GT$14read_to_string...
```

2. Membaca isi sebagai `String`, 

```llvm
; invoke hex::encode
  invoke void @_ZN3hex6encode17h04af9b7614623139E(...)
; invoke core::iter::traits::iterator::Iterator::step_by
  invoke void @_ZN4core4iter6traits8iterator8Iterator7step_by17h643e416d973a3425E(..., i64 2)
```

3. Memproses pasangan heks dari string tersebut menjadi vektor byte, 

```llvm
; invoke <alloc::string::String as core::ops::index::Index<I>>::index
  %67 = invoke { i1, i8 } @core::num::<impl u8>::from_str_radix(..., i32 16)
; invoke alloc::vec::Vec<T,A>::push
  invoke void @_ZN5alloc3vec16Vec$LT$T$C$A$GT$4push17h442119782527e08dE(ptr align 8 %bytes_as_number, i8 %number,...)
```

4. Menggabungkan byte tersebut menjadi sebuah bilangan besar (BigUint, big‑endian), 

```llvm
; invoke num_bigint::biguint::BigUint::from_bytes_be
  invoke void @_ZN10num_bigint7biguint7BigUint13from_bytes_be17h46da48b7b7a716f9E(...)
; invoke num_bigint::biguint::shift::<impl core::ops::bit::Shr<i32> ...>::shr
  invoke void ...Shr$LT$i32$GT... (ptr align 8 %big_int, i32 1)
; invoke num_bigint::biguint::...BitXor...
  invoke void ...bitxor...(ptr align 8 %gray, ptr align 8 %big_int, ptr align 8 %_52)
```

5. Lalu menghitung `g = n ^ (n >> 1)` dan mencetak `g` dalam format desimal. Outputnya adalah nilai dalam `output.txt` :

```
14752413339507261788089274160981710388034751813474093911954931340700920522403115209264370445883623831619
```

Dengan solver berikut prosesnya dapat dibalik dan didapatkan flagnya :

```python
def gray_to_binary(g: int) -> int:
    b = 0
    while g:
        b ^= g
        g >>= 1
    return b

def int_to_bytes_be(x: int) -> bytes:
    length = (x.bit_length() + 7) // 8
    return x.to_bytes(length, 'big') if length else b"\x00"

val = 14752413339507261788089274160981710388034751813474093911954931340700920522403115209264370445883623831619
n = gray_to_binary(val)
data = int_to_bytes_be(n)
print(data.decode())
```

### Flag
NCLPS1{rust_code_is_faster_than_go_code_:P}
