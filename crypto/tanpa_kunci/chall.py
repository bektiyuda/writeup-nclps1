FLAG = "NCLPS1{REDACTED}"
KEY = "" # REDACTED

def xor_cipher(data, key):
    data_bytes = data.encode('utf-8')
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)
    
    result = bytearray()
    
    for i, byte in enumerate(data_bytes):
        key_byte = key_bytes[i % key_len]
        
        xored_byte = byte ^ key_byte
        result.append(xored_byte)
        
    return bytes(result)

if __name__ == "__main__":
    encrypted_flag = xor_cipher(FLAG, KEY)
    encrypted_hex = encrypted_flag.hex()
    
    print(f"Encrypted: {encrypted_hex}")
