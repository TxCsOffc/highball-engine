import collections,sys
ref=open('ref.txt').read().splitlines(); got=open('fex.txt').read().splitlines()
val=collections.OrderedDict(); flg=collections.Counter()
seg=[('flags',0,16),('rcx',16,32),('rax',32,48),('M',48,240),('ymm1',240,304),('ymm0',304,368)]
for a,b in zip(ref,got):
    if a==b: continue
    ra=a.split(); rb=b.split(); ha,hb=ra[3],rb[3]
    if ha[16:]!=hb[16:]: val.setdefault(ra[0],[]).append((ha,hb,ra[1]))
    else: flg[ra[0]]+=1
print(len(ref),'cases; value diffs in',len(val),'tests; flag/mxcsr-only in',len(flg))
for op,l in val.items():
    a,b,m=l[0]; where=[n for n,s,e in seg if a[s:e]!=b[s:e]]
    print(f'{op:22s} {len(l):4d} in {",".join(where)} modes {sorted(set(x[2] for x in l))}')
    for n,s,e in seg:
        if n!='flags' and a[s:e]!=b[s:e]: print(f'      {n} ref {a[s:e][-64:]}\n      {n} got {b[s:e][-64:]}'); break
print('flag-only:', dict(flg.most_common(40)))
