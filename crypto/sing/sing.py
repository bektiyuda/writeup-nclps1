import random
from Crypto.Util.number import getPrime, bytes_to_long

def inverse_mod(k, p):
    if k == 0:
        raise ZeroDivisionError('division by zero')
    return pow(k, p - 2, p)

def add_points(P, Q, a, p):
    if P is None: 
        return Q
    if Q is None: 
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and y1 != y2: 
        return None
    if x1 == x2:
        m = (3 * x1 * x1 + a) * inverse_mod(2 * y1, p)
    else:
        m = (y2 - y1) * inverse_mod(x2 - x1, p)
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

def scalar_mult(n, P, a, p):
    result = None
    addend = P
    while n > 0:
        if n & 1: 
            result = add_points(result, addend, a, p)
        addend = add_points(addend, addend, a, p)
        n >>= 1
    return result

def encrypt(msg_int, p, g, y):
    k = random.randint(2, p - 2)
    c1 = pow(g, k, p)
    s = pow(y, k, p)
    c2 = (msg_int * s) % p
    return (c1, c2)

def generate_challenge():
    p1 = getPrime(256)
    g1 = random.randint(2, p1 - 2)

    n = random.randint(2, p1 - 2)
    y1 = pow(g1, n, p1)

    flag = b"NCLPS1{REDACTED}"
    flag_int = bytes_to_long(flag)
    encrypted_flag = encrypt(flag_int, p1, g1, y1)

    p2 = 0xE24E2559130DB6716584717A29F55EA54B88928E79856581E35AF3263F731DEF
    x0 = 1
    a = (-3 * pow(x0, 2, p2)) % p2
    b = (2 * pow(x0, 3, p2)) % p2
    assert (4 * pow(a, 3, p2) + 27 * pow(b, 2, p2)) % p2 == 0

    while True:
        Gx = random.randint(1, p2 - 1)
        y_sq = (pow(Gx, 3, p2) + a * Gx + b) % p2
        if pow(y_sq, (p2 - 1) // 2, p2) == 1:
            Gy = pow(y_sq, (p2 + 1) // 4, p2)
            G = (Gx, Gy)
            break

    Q = scalar_mult(n, G, a, p2)

    return {
        "p2": p2, "a": a, "b": b, "G": G, "Q": Q,
        "p1": p1, "g1": g1, "y1": y1,
        "encrypted_flag": encrypted_flag,
    }

def main():
    challenge = generate_challenge()
    print(f"p2 = {challenge['p2']}")
    print(f"a = {challenge['a']}")
    print(f"b = {challenge['b']}")
    print(f"Gx = {challenge['G'][0]}")
    print(f"Gy = {challenge['G'][1]}")
    print(f"Qx = {challenge['Q'][0]}")
    print(f"Qy = {challenge['Q'][1]}")
    print(f"p1 = {challenge['p1']}")
    print(f"g1 = {challenge['g1']}")
    print(f"y1 = {challenge['y1']}")
    print(f"c1 = {challenge['encrypted_flag'][0]}")
    print(f"c2 = {challenge['encrypted_flag'][1]}")

if __name__ == "__main__":
    main()