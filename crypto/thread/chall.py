import time
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

INPUT_IMAGE = 'flag.png'
ENCRYPTED_OUTPUT = 'flag.png.enc'

def encrypt_file():
    with open(INPUT_IMAGE, 'rb') as f:
        plaintext = f.read()

    t1 = int(time.time()) // 10
    
    # print(f"Enkripsi diproses di sekitar timestamp: {t1}")
    random.seed(t1)

    key = random.randbytes(16)
    iv = random.randbytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    encrypted_data = cipher.encrypt(pad(plaintext, AES.block_size))

    with open(ENCRYPTED_OUTPUT, 'wb') as f:
        f.write(encrypted_data)
        
    print(f"File '{INPUT_IMAGE}' berhasil dienkripsi menjadi '{ENCRYPTED_OUTPUT}'.")

if __name__ == "__main__":
    encrypt_file()