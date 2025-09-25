import sys, json, argparse
import base64, zlib, re

def iter_rb64_for_campaign(paths, campaign):
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue
                    hdr = o.get("hdr") or {}
                    if hdr.get("x-campaign") != campaign:
                        continue
                    rb64 = o.get("rb64")
                    if rb64:
                        yield rb64
        except Exception as e:
            print(f"[!] Gagal membuka {p}: {e}", file=sys.stderr)

def b64_gunzip_decode(data):
    try:
        decoded = base64.b64decode(data)
        decompressed = zlib.decompress(decoded, wbits=zlib.MAX_WBITS | 16)
        return decompressed.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[!] Error decoding/decompressing data: {e}", file=sys.stderr)
        return None

def main():
    campaign = "koi-44291a1b"
    paths = ["rp-access-2025-08-23.log", "rp-access-2025-08-23.log.1", "rp-access-2025-08-24.log"]
    frags = {}
    patt = re.compile(r"FRAG\[(\d+)/\d+\]=([A-Za-z0-9+/=]+)")

    for rb64 in iter_rb64_for_campaign(paths, campaign):
        decoded = b64_gunzip_decode(rb64)
        if not decoded:
            continue
        for i, b64part in patt.findall(decoded):
            frags[int(i)] = b64part
    
    joined_b64 = ''.join(frags[i] for i in sorted(frags))
    try:
        print(base64.b64decode(joined_b64).decode('utf-8'))
    except Exception as e:
        print(f"[!] Gagal base64-decode gabungan: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()