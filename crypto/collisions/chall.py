import functools; print(functools.reduce(lambda flag, i: flag ^ (flag >> 2**i), range(9), int.from_bytes(b"NCLPS1{redacted}", "big")))
