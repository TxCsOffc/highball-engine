# Generates fexdiff.c: every instruction below runs on the same pseudo-random and special operands under several
# MXCSR modes; each result (all destination bits, MXCSR afterwards, RFLAGS for compares) is printed as one line.
ops = []
def bin128(name, ins): ops.append(('x', name, ins))      # op %xmm1, %xmm0  (dst xmm0, src xmm1)
def avx128(name, ins): ops.append(('v', name, ins))      # vop %xmm2, %xmm1, %xmm0
def avx256(name, ins): ops.append(('y', name, ins))      # vop %ymm2, %ymm1, %ymm0
def fma(name, ins): ops.append(('f', name, ins))         # dst xmm0 also read
def flags(name, ins): ops.append(('c', name, ins))       # comiss style, result in RFLAGS
def cvtgpr(name, ins): ops.append(('g', name, ins))      # xmm -> r64
def gprcvt(name, ins): ops.append(('h', name, ins))      # r64 -> xmm
for p in ('ss','sd','ps','pd'):
    for o in ('add','sub','mul','div','min','max','sqrt'):
        bin128(o+p, '%s%s %%%%xmm1, %%%%xmm0' % (o, p))
    for imm in range(8):
        bin128('cmp%d%s' % (imm, p), 'cmp%s $%d, %%%%xmm1, %%%%xmm0' % (p, imm))
    for imm in (0,1,2,3,4,8,9,10,11,12):
        if p in ('ss','sd'):
            bin128('round%d%s' % (imm, p), 'round%s $%d, %%%%xmm1, %%%%xmm0' % (p, imm))
        else:
            bin128('round%d%s' % (imm, p), 'round%s $%d, %%%%xmm1, %%%%xmm0' % (p, imm))
for o in ('haddps','hsubps','addsubps','haddpd','hsubpd','addsubpd','andps','andnps','orps','xorps','unpcklps','unpckhps',
          'unpcklpd','unpckhpd','movss','movsd','cvtss2sd','cvtsd2ss','cvtdq2ps','cvtps2dq','cvttps2dq','cvtpd2dq','cvttpd2dq',
          'cvtdq2pd','cvtpd2ps','cvtps2pd','pminsd','pmaxsd','pminud','pmaxud','pmulld','pmuludq','pmuldq','packssdw','packusdw',
          'packsswb','packuswb','paddd','psubd','pcmpgtd','pcmpeqd','pshufb','pmaddwd','pmulhw','pavgw','psadbw'):
    bin128(o, '%s %%%%xmm1, %%%%xmm0' % o)
for imm in (0x1b, 0xe4, 0x4e, 0x00, 0xff):
    bin128('shufps%x' % imm, 'shufps $%d, %%%%xmm1, %%%%xmm0' % imm)
for imm in (0xff, 0x71, 0x3f, 0xf1, 0x55):
    bin128('dpps%x' % imm, 'dpps $%d, %%%%xmm1, %%%%xmm0' % imm)
for imm in (0x31, 0x33):
    bin128('dppd%x' % imm, 'dppd $%d, %%%%xmm1, %%%%xmm0' % imm)
for imm in (0x10, 0x5d, 0xa0):
    bin128('insertps%x' % imm, 'insertps $%d, %%%%xmm1, %%%%xmm0' % imm)
for p in ('ss','sd','ps','pd'):
    for o in ('add','sub','mul','div','min','max','sqrt'):
        if o == 'sqrt' and p in ('ps','pd'):
            avx128('v'+o+p, 'v%s%s %%%%xmm2, %%%%xmm0' % (o, p))
        else:
            avx128('v'+o+p, 'v%s%s %%%%xmm2, %%%%xmm1, %%%%xmm0' % (o, p))
    for imm in (0,1,2,3,4,5,6,7,0x11,0x13,0x18,0x1d,0x1e):
        avx128('vcmp%x%s' % (imm, p), 'vcmp%s $%d, %%%%xmm2, %%%%xmm1, %%%%xmm0' % (p, imm))
for p in ('ps','pd'):
    for o in ('add','sub','mul','div','min','max','sqrt','addsub','hadd'):
        if o == 'sqrt':
            avx256('v'+o+p+'y', 'v%s%s %%%%ymm2, %%%%ymm0' % (o, p))
        else:
            avx256('v'+o+p+'y', 'v%s%s %%%%ymm2, %%%%ymm1, %%%%ymm0' % (o, p))
    for imm in (0,1,9,10,11):
        avx256('vround%d%sy' % (imm, p), 'vround%s $%d, %%%%ymm2, %%%%ymm0' % (p, imm))
avx256('vdppsy', 'vdpps $0xff, %%ymm2, %%ymm1, %%ymm0')
avx256('vcvtps2pdy', 'vcvtps2pd %%xmm2, %%ymm0'); avx256('vcvtpd2psy', 'vcvtpd2ps %%ymm2, %%xmm0')
avx256('vcvtdq2psy', 'vcvtdq2ps %%ymm2, %%ymm0'); avx256('vcvtps2dqy', 'vcvtps2dq %%ymm2, %%ymm0'); avx256('vcvttps2dqy', 'vcvttps2dq %%ymm2, %%ymm0')
avx256('vcvtph2psy', 'vcvtph2ps %%xmm2, %%ymm0')
for imm in (0,1,2,3,4):
    avx128('vcvtps2ph%d' % imm, 'vcvtps2ph $%d, %%%%xmm2, %%%%xmm0' % imm)
for f in ('vfmadd','vfmsub','vfnmadd','vfnmsub'):
    for order in ('132','213','231'):
        for p in ('ss','sd','ps','pd'):
            fma(f+order+p, '%s%s%s %%%%xmm2, %%%%xmm1, %%%%xmm0' % (f, order, p))
for f in ('vfmaddsub231ps','vfmsubadd231ps','vfmaddsub231pd'):
    fma(f, '%s %%%%xmm2, %%%%xmm1, %%%%xmm0' % f)
for o in ('comiss','ucomiss','comisd','ucomisd'):
    flags(o, '%s %%%%xmm1, %%%%xmm0' % o)
for o in ('cvtss2si','cvttss2si','cvtsd2si','cvttsd2si'):
    cvtgpr(o+'q', '%s %%%%xmm1, %%%%rax' % o); cvtgpr(o+'l', '%s %%%%xmm1, %%%%eax' % o)
for o in ('cvtsi2ssq','cvtsi2sdq','cvtsi2ssl','cvtsi2sdl'):
    reg = '%%rax' if o.endswith('q') else '%%eax'
    gprcvt(o, '%s %s, %%%%xmm0' % (o, reg))

for o in ('rcpps','rcpss','rsqrtps','rsqrtss'):
    bin128(o, '%s %%%%xmm1, %%%%xmm0' % o)
for o in ('vrcpps','vrsqrtps'):
    avx256(o+'y', '%s %%%%ymm2, %%%%ymm0' % o)
for o in ('pmaddubsw','pmulhrsw','pmulhuw','pmullw','pminsw','pmaxsw','pminub','pmaxub','pabsd','pabsw','psignd','phaddd','phaddw','phsubd',
          'paddusw','psubusb','paddsw','pcmpgtq','pcmpeqq','pminsb','pmaxsb','pminuw','pmaxuw','punpcklbw','punpckhwd','psllw','psrad','psrlq','pslld'):
    bin128(o, '%s %%%%xmm1, %%%%xmm0' % o)
for o in ('vpermps','vpermd','vpsllvd','vpsrlvd','vpsravd','vpmulld','vpmaddwd','vpminsd','vpmaxsd','vpaddd','vpsubd','vpcmpgtd','vpshufb','vpackssdw','vpunpckldq','vpmuldq','vpmulhrsw','vpavgb','vpsadbw','vpermilps','vpsignd'):
    avx256(o+'y', '%s %%%%ymm2, %%%%ymm1, %%%%ymm0' % o)
for imm in (0x1b, 0xd8, 0x4e):
    avx256('vpermq%x' % imm, 'vpermq $%d, %%%%ymm2, %%%%ymm0' % imm)
    avx256('vpermpd%x' % imm, 'vpermpd $%d, %%%%ymm2, %%%%ymm0' % imm)
for imm in (0x20, 0x31, 0x02):
    avx256('vperm2f128_%x' % imm, 'vperm2f128 $%d, %%%%ymm2, %%%%ymm1, %%%%ymm0' % imm)
for imm in (0x0f, 0xa5):
    avx256('vblendps%x' % imm, 'vblendps $%d, %%%%ymm2, %%%%ymm1, %%%%ymm0' % imm)
avx256('vblendvps', 'vblendvps %%ymm2, %%ymm2, %%ymm1, %%ymm0'); avx256('vpblendvb', 'vpblendvb %%ymm2, %%ymm2, %%ymm1, %%ymm0')
for f in ('vfmadd231ps','vfmsub231ps','vfnmadd231ps','vfmadd213pd','vfmaddsub231ps','vfmsubadd213ps'):
    ops.append(('Y', f+'y', '%s %%%%ymm2, %%%%ymm1, %%%%ymm0' % f))
for imm in (0xff, 0xf1, 0x71):
    avx256('vdpps%xy' % imm, 'vdpps $%d, %%%%ymm2, %%%%ymm1, %%%%ymm0' % imm)
avx256('vhaddpsy2', 'vhaddps %%ymm2, %%ymm1, %%ymm0'); avx256('vmovmskpsy', 'vmovmskps %%ymm2, %%eax\\n vmovd %%eax, %%xmm0')
avx256('vptesty', 'vptest %%ymm2, %%ymm1\\n setc %%al\\n setz %%ah\\n movzwl %%ax, %%eax\\n vmovd %%eax, %%xmm0')
for o in ('fadd','fsub','fmul','fdiv','fsubr','fdivr','fprem','fprem1','fscale','fpatan','fyl2x','fyl2xp1'):
    ops.append(('X2', o, o))
for o in ('fsqrt','fsin','fcos','frndint','f2xm1','fabs','fchs','fxtract','fptan','fsincos'):
    ops.append(('X1', o, o))
for rc in (0, 1, 2, 3):
    ops.append(('XI', 'fistp_rc%d' % rc, '%d' % rc))

out = []
out.append(r'''#include <stdio.h>
#include <stdint.h>
#include <string.h>
static uint64_t rs = 0x9e3779b97f4a7c15ull;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static const uint32_t sp32[] = { 0x00000000, 0x80000000, 0x3f800000, 0xbf800000, 0x7f800000, 0xff800000, 0x7fc00000, 0xffc00000,
   0x7fa00001, 0xffa12345, 0x7fc0dead, 0x00000001, 0x80000001, 0x007fffff, 0x00800000, 0x7f7fffff, 0xff7fffff, 0x4f000000,
   0xcf000000, 0x5f000000, 0xdf000000, 0x3f000000, 0x3fc00000, 0x40200000, 0x3effffff, 0x4b000001, 0x4effffff, 0x4f7fffff };
static const uint64_t sp64[] = { 0, 0x8000000000000000ull, 0x3ff0000000000000ull, 0xbff0000000000000ull, 0x7ff0000000000000ull,
   0xfff0000000000000ull, 0x7ff8000000000000ull, 0xfff8000000000000ull, 0x7ff4000000000001ull, 0x7ff8dead00000000ull,
   1, 0x8000000000000001ull, 0x000fffffffffffffull, 0x0010000000000000ull, 0x7fefffffffffffffull, 0x43e0000000000000ull,
   0xc3e0000000000000ull, 0x41e0000000000000ull, 0xc1e0000000000000ull, 0x3fe0000000000000ull, 0x3ff8000000000000ull,
   0x4004000000000000ull, 0x43dfffffffffffffull, 0x41dfffffffc00000ull };
static void fill(uint8_t *v, int n, int k, int kind)
{  /* kind 0: float lanes, 1: double lanes */
   for (int i = 0; i < n; i += 8) { uint64_t r = rnd(); memcpy(v + i, &r, 8); }
   if (kind == 0) for (int i = 0; i < n / 4; i++) { uint64_t r = rnd(); uint32_t x;
      if ((r & 3) == 0) x = sp32[(r >> 8) % (sizeof(sp32) / 4)]; else if ((r & 3) == 1) { float f = (float)((int32_t)(r >> 16) % 2000) / 16.0f; memcpy(&x, &f, 4); } else continue;
      memcpy(v + i * 4, &x, 4); }
   else for (int i = 0; i < n / 8; i++) { uint64_t r = rnd(); uint64_t x;
      if ((r & 3) == 0) x = sp64[(r >> 8) % (sizeof(sp64) / 8)]; else if ((r & 3) == 1) { double d = (double)((int32_t)(r >> 16) % 2000) / 16.0; memcpy(&x, &d, 8); } else continue;
      memcpy(v + i * 8, &x, 8); }
   (void)k;
}
static void hex(char *o, const uint8_t *v, int n) { static const char h[] = "0123456789abcdef"; for (int i = n - 1; i >= 0; i--) { *o++ = h[v[i] >> 4]; *o++ = h[v[i] & 15]; } *o = 0; }
static const uint32_t modes[] = { 0x1f80, 0x3f80, 0x5f80, 0x7f80, 0x9f80, 0x1fc0, 0x9fc0 };
#define CASES 64
''')
for kind, name, ins in ops:
    isd = (('sd' in name[-3:] or 'pd' in name) and 'ps' not in name[-3:]) or kind in ('X1','X2','XI')
    k = 1 if isd else 0
    if kind in ('x',):
        body = '"movdqu (%%[a]), %%%%xmm0\\n movdqu (%%[b]), %%%%xmm1\\n %s\\n movdqu %%%%xmm0, (%%[r])\\n" : : [a] "r"(a), [b] "r"(b), [r] "r"(r) : "xmm0", "xmm1", "memory"' % ins
        nbytes = 16
    elif kind == 'v' or kind == 'f':
        body = '"vmovdqu (%%[r]), %%%%xmm0\\n vmovdqu (%%[a]), %%%%xmm1\\n vmovdqu (%%[b]), %%%%xmm2\\n %s\\n vmovdqu %%%%ymm0, (%%[r])\\n vzeroupper\\n" : : [a] "r"(a), [b] "r"(b), [r] "r"(r) : "xmm0", "xmm1", "xmm2", "memory"' % ins
        nbytes = 32
    elif kind == 'X1' or kind == 'X2':
        two = kind == 'X2'
        A = 'fldl (%[a])\\n'; B = 'fldl (%[b])\\n' if two else ''
        op = ins + (' %%st, %%st(1)\\n fstp %%st(0)' if ins in ('fadd','fsub','fmul','fdiv','fsubr','fdivr') else '')
        tail = 'fstpt 16(%[r])\\n' if ins in ('fprem','fprem1','fscale','fxtract','fptan','fsincos','fpatan','fyl2x','fyl2xp1') and False else ''
        extra = 'fstpt 16(%[r])\\n' if ins in ('fprem','fprem1','fscale','fxtract','fptan','fsincos') else ''
        body = '"fninit\\n ' + B + A + op + '\\n fstpt (%[r])\\n ' + extra + 'fnstsw %%ax\\n mov %%ax, 10(%[r])\\n fninit\\n" : : [a] "r"(a), [b] "r"(b), [r] "r"(r) : "rax", "memory", "st", "st(1)"'
        nbytes = 32
    elif kind == 'XI':
        body = '"fninit\\n fnstcw (%%[r])\\n movzwl (%%[r]), %%%%eax\\n and $0xf3ff, %%%%eax\\n or $%d, %%%%eax\\n mov %%%%ax, (%%[r])\\n fldcw (%%[r])\\n fldl (%%[a])\\n fistpll (%%[r])\\n fnstsw %%%%ax\\n mov %%%%ax, 8(%%[r])\\n fninit\\n" : : [a] "r"(a), [r] "r"(r) : "rax", "memory"' % (int(ins) << 10)
        nbytes = 16
    elif kind == 'Y':
        body = '"vmovdqu (%%[r]), %%%%ymm0\\n vmovdqu (%%[a]), %%%%ymm1\\n vmovdqu (%%[b]), %%%%ymm2\\n %s\\n vmovdqu %%%%ymm0, (%%[r])\\n vzeroupper\\n" : : [a] "r"(a), [b] "r"(b), [r] "r"(r) : "xmm0", "xmm1", "xmm2", "memory"' % ins
        nbytes = 32
    elif kind == 'y':
        body = '"vmovdqu (%%[r]), %%%%ymm0\\n vmovdqu (%%[a]), %%%%ymm1\\n vmovdqu (%%[b]), %%%%ymm2\\n %s\\n vmovdqu %%%%ymm0, (%%[r])\\n vzeroupper\\n" : : [a] "r"(a), [b] "r"(b), [r] "r"(r) : "xmm0", "xmm1", "xmm2", "memory"' % ins
        nbytes = 32
    elif kind == 'c':
        body = '"movdqu (%%[a]), %%%%xmm0\\n movdqu (%%[b]), %%%%xmm1\\n %s\\n pushfq\\n pop %%%%rax\\n mov %%%%rax, (%%[r])\\n" : : [a] "r"(a), [b] "r"(b), [r] "r"(r) : "rax", "xmm0", "xmm1", "memory", "cc"' % ins
        nbytes = 8
    elif kind == 'g':
        body = '"movq $0x1234567812345678, %%%%rax\\n movdqu (%%[b]), %%%%xmm1\\n %s\\n mov %%%%rax, (%%[r])\\n" : : [b] "r"(b), [r] "r"(r) : "rax", "xmm1", "memory"' % ins
        nbytes = 8
    elif kind == 'h':
        body = '"movdqu (%%[a]), %%%%xmm0\\n mov (%%[b]), %%%%rax\\n %s\\n movdqu %%%%xmm0, (%%[r])\\n" : : [a] "r"(a), [b] "r"(b), [r] "r"(r) : "rax", "xmm0", "memory"' % ins
        nbytes = 16
    out.append('''static void t_%s(void)
{
   uint8_t a[32], b[32], r[32]; char line[200]; uint32_t mx;
   for (int m = 0; m < 7; m++) for (int c = 0; c < CASES; c++) {
      fill(a, 32, c, %d); fill(b, 32, c, %d); fill(r, 32, c, %d);
      if (%d) { int64_t iv = (int64_t)rnd() >> (rnd() & 63); memcpy(b, &iv, 8); }
      uint32_t md = modes[m]; __asm__ volatile("ldmxcsr %%0" : : "m"(md));
      __asm__ volatile(%s);
      __asm__ volatile("stmxcsr %%0" : "=m"(mx)); uint32_t def = 0x1f80; __asm__ volatile("ldmxcsr %%0" : : "m"(def));
      if (%d) { uint64_t f; memcpy(&f, r, 8); f &= 0x8d5; memcpy(r, &f, 8); }
      hex(line, r, %d); printf("%s m%%d c%%d %%s mx%%04x\\n", m, c, line, mx & 0xffff);
   }
}
''' % (name, k, k, k, 1 if kind == 'h' else 0, body, 1 if kind == 'c' else 0, nbytes, name))
out.append('int main(int argc, char **argv) {\n   setvbuf(stdout, 0, _IOFBF, 1 << 20);\n')
for kind, name, ins in ops:
    out.append('   rs = 0x9e3779b97f4a7c15ull ^ %du; t_%s();\n' % (sum(map(ord, name)) * 7919 % 100000, name))
out.append('   return 0;\n}\n')
open('fexdiff.c','w').write(''.join(out))
print(len(ops), 'instructions')
