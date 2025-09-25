import re

src = open('tilde.js','r',encoding='utf-8').read()
re_cmp = re.compile(r"flag\.charCodeAt\(([^)]*)\)\s*==\s*([^)&|;]+)[)&|;]")

def count_pairs(expr: str) -> int:
    return len(re.findall(r"-~", re.sub(r"\s+","", expr)))

pairs = []
for idx_expr, val_expr in re_cmp.findall(src):
    idx = count_pairs(idx_expr)
    val = count_pairs(val_expr)
    pairs.append((idx, val))

pairs.sort()
maxi = pairs[-1][0]
arr = [0]*(maxi+1)
for i,v in pairs:
    arr[i]=v
print('Flag:', ''.join(map(chr, arr)))