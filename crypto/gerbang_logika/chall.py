import hashlib
import random

FLAG = "" # REDACTED FLAG
INITIAL_STATE = random.randint(0, 2**27)

# LCG?
A = 69069
M = 2**32

def update_state(current_state, plain_char_ord):
    return (A * current_state + plain_char_ord) % M

def encrypt_char(plain_char, current_state):
    xor_key = (current_state >> 8) & 0xFF 
    out = ord(plain_char) ^ xor_key
    swap_mode = current_state % 3
    
    if swap_mode == 0:
        var1 = (out & 0xAA) >> 1
        var2 = (2 * out) & 0xAA
        return var1 | var2
    elif swap_mode == 1:
        var1 = (out & 0xCC) >> 2
        var2 = (4 * out) & 0xCC
        return var1 | var2
    else:
        var1 = (out & 0xF0) >> 4
        var2 = (16 * out) & 0xF0
        return var1 | var2

if __name__ == "__main__":
    encrypted_result = []
    state = INITIAL_STATE

    for char in FLAG:
        encrypted_char_ord = encrypt_char(char, state)
        encrypted_result.append(chr(encrypted_char_ord))
        state = update_state(state, ord(char))
    
    encrypted_flag = "".join(encrypted_result)
    final_hash = hashlib.sha256(FLAG.encode()).hexdigest()

    print(f"Encrypted Flag  : {encrypted_flag.encode('latin-1').hex()}")
    print(f"SHA256 Checksum : {final_hash}")