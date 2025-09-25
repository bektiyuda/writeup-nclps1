import os, time, random
from Crypto.Cipher import AES

enc_path = "flag.png.enc"
ct = open(enc_path, "rb").read()
c0 = ct[:16]
PNG = b"\x89PNG\r\n\x1a\n"

center_t1 = int(os.path.getmtime(enc_path)) // 10

def find_seed(center, radius_days=14):
    start = center - radius_days*8640
    end = center + radius_days*8640
    for t1 in range(start, end + 1):
        random.seed(t1)
        key = random.randbytes(16)
        iv  = random.randbytes(16)
        p0 = AES.new(key, AES.MODE_ECB).decrypt(c0)
        p0 = bytes(x ^ y for x, y in zip(p0, iv))
        if p0.startswith(PNG):
            return t1, key, iv
    return None, None, None

seed, key, iv = find_seed(center_t1, radius_days=120)
if seed is None:
    raise SystemExit("Seed tidak ditemukan")

from Crypto.Util.Padding import unpad
pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
pt = unpad(pt, 16)
open('flag.png', 'wb').write(pt)
print('Seed:', seed, 'UTC:', time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(seed*10)))