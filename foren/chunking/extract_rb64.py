import sys, json, argparse

def iter_rb64(paths):
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
                    rb64 = o.get("rb64")
                    if rb64:
                        yield rb64
        except Exception as e:
            print(f"[!] Gagal membuka {p}: {e}", file=sys.stderr)

def main():
    path_1 = "rp-access-2025-08-23.log"
    path_2 = "rp-access-2025-08-23.log.1"
    path_3 = "rp-access-2025-08-24.log"
    count_in, count_out = 0, 0
    with open("rb64_all.txt", "w", encoding="utf-8") as out:
        for rb64 in iter_rb64([path_1, path_2, path_3]):
            count_in += 1
            out.write(rb64.rstrip() + "\n")
            count_out += 1

    print(f"Saved: rb64_all.txt")

if __name__ == "__main__":
    main()
