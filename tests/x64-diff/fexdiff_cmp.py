import sys,collections
ref=open(sys.argv[1]).read().splitlines(); got=open(sys.argv[2]).read().splitlines()
val=collections.OrderedDict(); flg=collections.Counter()
modes=['default','rc-down','rc-up','rc-zero','ftz','daz','ftz+daz']
for a,b in zip(ref,got):
    if a==b: continue
    ra=a.split(); rb=b.split()
    if ra[3]!=rb[3]: val.setdefault(ra[0],[]).append((ra,rb))
    else: flg[ra[0]]+=1
print(f'{len(ref)} cases; value differs in {sum(len(v) for v in val.values())} cases over {len(val)} instructions; flags-only differences in {sum(flg.values())} cases over {len(flg)} instructions')
for op,l in val.items():
    ra,rb=l[0]; ms=sorted(set(modes[int(x[1][1:])] for x,_ in l))
    print(f'  {op:16s} {len(l):5d}  modes {",".join(ms)}\n      ref {ra[3]}\n      got {rb[3]}')
