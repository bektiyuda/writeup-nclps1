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