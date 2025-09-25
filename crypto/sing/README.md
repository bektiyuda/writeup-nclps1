## sing

**Difficulty:** Insane

**Author:** n4siKvn1ng

### Description

Mencoba untuk implementasi sebuah cryptosystem dengan melanggar rule utama untuk mengamankan flag. Apakah itu sebuah kesalahan? i don't know... Let's just sing same song with Mr. Jamal Note: maybe this tool will help you https://sagemanifolds.obspm.fr/install_ubuntu.html

### Solution

```
p2 = 102360775616927576983385464260307534406913988994641083488371841417601237589487
 a = 102360775616927576983385464260307534406913988994641083488371841417601237589484
 b = 2
 Gx = 7644455972383009574954271307443164751748475778727501832213132925952300024545
 Gy = 101573852871707769271254138751474521352093292608677724066365511814632080362920
 Qx = 98305490898192258953356272513089255888160781777859467299225792236262120691981
 Qy = 80161053863379418628922186359615001382408924106146479422534497394984217418641

p1 = 75328539504512434959392248551334836255720426238723055979408399508379911242257
g1 = 26362179638343804554779964733040958878062098061770653773743089284369767183984
y1 = 14890360911719498303359880745673131252698277783522096003699766286065662181192
c1 = 36190580977708825355326737534548059444874621589153607092572356007292483493417
c2 = 52066014497039620520753136552806843298512257316676936511291473589116415755657
```

## Analisis Awal

Tantangan menggabungkan dua sisi. Di sisi pertama terdapat parameter ElGamal $p_1$: generator $g_1$, public key $y_1 = g_1^n \pmod{p_1}$, serta ciphertext $(c_1, c_2)$. Di sisi kedua terdapat parameter yang menyerupai kurva eliptik dengan modulus $p_2$, titik dasar $G$, dan hasil perkalian skalar $Q = nG$. Tujuannya memulihkan $n$ dari sisi kurva untuk kemudian digunakan dalam dekripsi ElGamal.

$$
 y^2 = x^3 - 3x + 2 = (x-1)^2(x+2).
$$

Dengan memeriksa koefisien, diketahui bahwa $a \equiv -3 \pmod{p_2}$ dan $b = 2$. Bentuk persamaan kurvanya adalah seperti daiatas. Bentuk faktorisasi ini mengindikasikan bahwa kurva tersebut singular dengan node di titik (1,0). Kondisi diskriminan $\Delta = 4a^3 + 27b^2 = 0$ menjelaskan bahwa ini bukan kurva eliptik valid, sehingga keamanan ECDLP tidak berlaku.

$$
  x = \lambda^2 - 2, \quad y = \lambda(\lambda^2 - 3).
$$

Kurva singular dapat diparameterisasi dengan kemiringan garis melalui node: $\lambda = y/(x-1)$. Dari sini diperoleh formula seperti diatas.

Dengan mendefinisikan transformasi Möbius $$ \varphi(P) = \frac{\lambda(P) - r}{\lambda(P) + r}, \quad r^2 \equiv 3 \pmod{p_2},$$ aturan penjumlahan pada kurva singular ini setara dengan perkalian pada $\mathbb{F}_{p_2}^*$. Akibatnya, $Q = nG$ dapat dikurangi menjadi logaritma diskrit biasa: $\varphi(Q) = \varphi(G)^n \pmod{p_2}$.

Begitu nilai $n$ diperoleh, langkah validasi dilakukan di sisi ElGamal dengan memeriksa $g_1^n \equiv y_1$. Setelah valid, dekripsi dilakukan dengan menghitung secret bersama $s = c_1^n$ dan plaintext $m = c_2 · s^{-1} \pmod{p_1}$. Karena ini adalah tantangan ECC, saya terbiasa memakai SageMath karena ada function discrete_log untuk mempermudah implementasi solver. Untuk implementasinya adalah solver berikut ini:

```python
p2 = 102360775616927576983385464260307534406913988994641083488371841417601237589487
Gx = 7644455972383009574954271307443164751748475778727501832213132925952300024545
Gy = 101573852871707769271254138751474521352093292608677724066365511814632080362920
Qx = 98305490898192258953356272513089255888160781777859467299225792236262120691981
Qy = 80161053863379418628922186359615001382408924106146479422534497394984217418641

p1 = 75328539504512434959392248551334836255720426238723055979408399508379911242257
g1 = 26362179638343804554779964733040958878062098061770653773743089284369767183984
y1 = 14890360911719498303359880745673131252698277783522096003699766286065662181192
c1 = 36190580977708825355326737534548059444874621589153607092572356007292483493417
c2 = 52066014497039620520753136552806843298512257316676936511291473589116415755657

Fp2, Fp1 = GF(p2), GF(p1)

def lam(x, y):
    return Fp2(y) / (Fp2(x) - 1)

def solve_with_r(r):
    phiG = (lam(Gx, Gy) - r) / (lam(Gx, Gy) + r)
    phiQ = (lam(Qx, Qy) - r) / (lam(Qx, Qy) + r)

    Nphi = Fp2(phiG).multiplicative_order()
    n_phi = discrete_log(Fp2(phiQ), Fp2(phiG), ord=Nphi)

    g1F, y1F = Fp1(g1), Fp1(y1)
    H = g1F ** Integer(Nphi)
    target = y1F / (g1F ** Integer(n_phi))
    t = 0 if H == 1 else discrete_log(target, H, ord=H.multiplicative_order())

    n = Integer(n_phi + t * Nphi)
    assert power_mod(g1, n, p1) == y1
    s = power_mod(c1, n, p1)
    m = (Integer(c2) * inverse_mod(s, p1)) % p1
    return m

r = sqrt(Fp2(3))
for rc in (r, -r):
    try:
        m = solve_with_r(rc)
        print(int(m).to_bytes((m.nbits()+7)//8, 'big'))
        break
    except Exception:
        continue
```

### Flag

NCLPS1{3cc_But_s!nGul4r}