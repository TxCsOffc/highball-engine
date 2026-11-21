# Pull every MSL source out of a Mesa disk cache (KosmicKrisp entries), keyed by the build id at the head of each entry.
import os, sys, zlib, hashlib, collections, json
root = sys.argv[1]; out = sys.argv[2]; want_build = sys.argv[3] if len(sys.argv) > 3 else None
os.makedirs(out, exist_ok=True)
builds = collections.Counter(); n = 0; got = 0
for d in os.listdir(root):
    p = os.path.join(root, d)
    if not os.path.isdir(p): continue
    for f in os.listdir(p):
        fp = os.path.join(p, f)
        with open(fp, 'rb') as fh: head = fh.read(80)
        bid = head[1:65].decode('latin1', 'replace')
        builds[bid] += 1
        if want_build and bid != want_build: continue
        data = open(fp, 'rb').read(); n += 1
        i = data.find(b'kk_apple10\x00')
        if i < 0: continue
        txt = None
        for off in range(i, min(len(data), i + 400)):
            if data[off] == 0x78 and data[off + 1] in (0x01, 0x5e, 0x9c, 0xda):
                try: txt = zlib.decompress(data[off:]); break
                except Exception: pass
        if txt is None:
            for off in range(i, min(len(data), i + 400)):
                try: txt = zlib.decompressobj(-15).decompress(data[off:]); 
                except Exception: continue
                if b'metal_stdlib' in txt: break
                txt = None
        if not txt: continue
        k = 0
        while True:
            s = txt.find(b'#include <metal_stdlib>', k)
            if s < 0: break
            e = txt.find(b'\x00', s); e = len(txt) if e < 0 else e
            msl = txt[s:e]; h = hashlib.sha1(msl).hexdigest()[:16]
            open(os.path.join(out, h + '.metal'), 'wb').write(msl); got += 1; k = e
print('builds', builds.most_common(5)); print('read', n, 'msl', got)
