import zlib, pathlib
c = pathlib.Path('packed.zlib').read_bytes()
stage2 = zlib.decompress(c)
print("decompressed size:", len(stage2))
pathlib.Path('stage2.elf').write_bytes(stage2)
print("validate header:", stage2[:4])