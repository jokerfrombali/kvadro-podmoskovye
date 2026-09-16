# -*- coding: utf-8 -*-
import sys, os, importlib, re
sys.path.insert(0, 'build')
A = {}
for i in range(1, 8):
    for a in importlib.import_module('d_art_%02d' % i).ART: A[a[0]] = a
D = 'site/src/content/articles'
short, ok, miss = [], 0, []
for k in sorted(A):
    p = os.path.join(D, k + '.md')
    if not os.path.exists(p):
        miss.append(k); continue
    t = open(p, encoding='utf-8').read()
    t = re.sub(r'^---.*?---\n', '', t, flags=re.S)
    n = len(t)
    lo, hi = A[k][12], A[k][13]
    if n < lo: short.append((k, n, lo, hi, A[k][3][:40]))
    else: ok += 1
print(f'написано: {len(A)-len(miss)} | в норме: {ok} | короче нормы: {len(short)} | не написано: {len(miss)}')
if short:
    print('\nкороче нормы:')
    for k, n, lo, hi, h in short: print(f'  {k}  {n:>6} / {lo}-{hi}  (+{lo-n})  {h}')
print('\nсуммарный недобор:', sum(lo-n for _, n, lo, _, _ in short))
