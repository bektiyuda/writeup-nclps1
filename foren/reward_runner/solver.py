from Crypto.Cipher import AES

key = b"id-networkersnlc"
xor_key = b"notcra_lupra"

data = open("secret.txt.idn.enc","rb").read()
iv, ct = data[:16], data[16:]

# AES-CBC decrypt
pt_xored = AES.new(key, AES.MODE_CBC, iv=iv).decrypt(ct)

# PKCS7 unpad
pad = pt_xored[-1]
pt_xored = pt_xored[:-pad]

# reverse XOR
pt = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(pt_xored))

print(pt)