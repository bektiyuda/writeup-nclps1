import os, re, sys, fcntl, signal, subprocess, time

PATTERN = re.compile(rb'NCLPS1\{[^}]+\}')
HANDSHAKE_HINT = b'handshake'

def nonblock(fd):
    import fcntl as F
    fl = F.fcntl(fd, F.F_GETFL)
    F.fcntl(fd, F.F_SETFL, fl | os.O_NONBLOCK)

def scan_mem(pid):
    hits = []
    with open(f'/proc/{pid}/maps') as mp, open(f'/proc/{pid}/mem','rb',0) as mem:
        for line in mp:
            rng, perms, *_ = line.split()
            if 'r' not in perms:
                continue
            start, end = (int(x,16) for x in rng.split('-'))
            try:
                mem.seek(start)
                data = mem.read(min(end-start, 8_000_000))
            except Exception:
                continue
            for m in PATTERN.finditer(data):
                hits.append((start + m.start(), m.group(0)))
    return hits

def main():
    p = subprocess.Popen(['./diag'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    nonblock(p.stdout.fileno())
    buf=b''; t0=time.time(); carved=False
    while p.poll() is None:
        try:
            chunk = os.read(p.stdout.fileno(), 65536)
            if chunk:
                buf += chunk
                if b'handshake' in buf and not carved:
                    os.kill(p.pid, signal.SIGSTOP)
                    for addr, tok in scan_mem(p.pid):
                        print(f'[+] token @0x{addr:x}: {tok.decode()}')
                    os.kill(p.pid, signal.SIGCONT)
                    carved=True
        except BlockingIOError:
            pass
        if not carved and time.time()-t0 > 1.5: # fallback
            os.kill(p.pid, signal.SIGSTOP)
            for addr, tok in scan_mem(p.pid):
                print(f'[+] token (fallback) @0x{addr:x}: {tok.decode()}')
            os.kill(p.pid, signal.SIGCONT)
            carved=True
        time.sleep(0.01)

if __name__ == '__main__':
    main()