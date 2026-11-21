/* Calls ucrtbase math/conversion functions on fixed inputs under several MXCSR / _controlfp states and prints all result bits. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <stdlib.h>
#include <xmmintrin.h>
static uint64_t rs = 0x243f6a8885a308d3ull;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static const float spf[] = { 0.0f, -0.0f, 0.5f, -0.5f, 1.5f, -1.5f, 2.5f, -2.5f, 0.49999997f, 1e-40f, -1e-40f, 1.17549435e-38f, 3.4e38f, -3.4e38f,
   2147483648.0f, -2147483648.0f, 4294967296.0f, 1e10f, -1e10f, 8388608.5f, 16777217.0f, 0.1f, 3.14159265f, 1e-7f, 6.67f, 3.33f, 0.7f };
static double randd(void) { uint64_t r = rnd(); switch (r & 7) {
   case 0: return spf[(r >> 8) % (sizeof(spf) / sizeof(spf[0]))];
   case 1: { uint64_t b = rnd(); double d; memcpy(&d, &b, 8); return d; }
   case 2: return ((double)(int64_t)(rnd() >> 20) / 4096.0);
   case 3: return ((double)(int32_t)(rnd()) / 65536.0) * 1e-30;
   default: return ((double)(int32_t)(rnd() >> 32)) / 1024.0; } }
static uint32_t fb(float f) { uint32_t u; memcpy(&u, &f, 4); return u; }
static uint64_t db(double d) { uint64_t u; memcpy(&u, &d, 8); return u; }
#define F1(fn) printf(#fn " %s %08x -> %08x\n", mode, fb(x), fb(fn(x)))
#define D1(fn) printf(#fn " %s %016llx -> %016llx\n", mode, (unsigned long long)db(d), (unsigned long long)db(fn(d)))
#define F2(fn) printf(#fn " %s %08x %08x -> %08x\n", mode, fb(x), fb(y), fb(fn(x, y)))
#define D2(fn) printf(#fn " %s %016llx %016llx -> %016llx\n", mode, (unsigned long long)db(d), (unsigned long long)db(e), (unsigned long long)db(fn(d, e)))
#define I1(fn, T) printf(#fn " %s %016llx -> %llx\n", mode, (unsigned long long)db(d), (unsigned long long)(T)fn(d))
#define IF1(fn, T) printf(#fn " %s %08x -> %llx\n", mode, fb(x), (unsigned long long)(T)fn(x))
static void run(const char *mode)
{
   rs = 0x243f6a8885a308d3ull;
   for (int i = 0; i < 400; i++) {
      double d = randd(), e = randd(); float x = (float)d, y = (float)e;
      F1(floorf); F1(ceilf); F1(roundf); F1(truncf); F1(rintf); F1(nearbyintf); F1(sqrtf); F1(sinf); F1(cosf); F1(tanf); F1(expf); F1(exp2f); F1(logf); F1(log2f); F1(log10f);
      F1(asinf); F1(acosf); F1(atanf); F1(sinhf); F1(tanhf); F1(cbrtf); F1(fabsf); F1(log1pf); F1(expm1f);
      F2(powf); F2(atan2f); F2(fmodf); F2(fminf); F2(fmaxf); F2(hypotf); F2(remainderf); F2(copysignf);
      D1(floor); D1(ceil); D1(round); D1(trunc); D1(rint); D1(nearbyint); D1(sqrt); D1(sin); D1(cos); D1(tan); D1(exp); D1(log); D1(log2); D1(log10);
      D1(asin); D1(acos); D1(atan); D1(cbrt); D1(exp2);
      D2(pow); D2(atan2); D2(fmod); D2(fmin); D2(fmax); D2(hypot); D2(remainder);
      I1(lrint, long long); I1(llrint, long long); I1(lround, long long); I1(llround, long long);
      IF1(lrintf, long long); IF1(llrintf, long long); IF1(lroundf, long long);
      { int ex; double m = frexp(d, &ex); printf("frexp %s %016llx -> %016llx %d\n", mode, (unsigned long long)db(d), (unsigned long long)db(m), ex); }
      { double ip; double f = modf(d, &ip); printf("modf %s %016llx -> %016llx %016llx\n", mode, (unsigned long long)db(d), (unsigned long long)db(f), (unsigned long long)db(ip)); }
      { float ip; float f = modff(x, &ip); printf("modff %s %08x -> %08x %08x\n", mode, fb(x), fb(f), fb(ip)); }
      printf("ldexp %s %016llx %d -> %016llx\n", mode, (unsigned long long)db(d), (int)(e) % 64, (unsigned long long)db(ldexp(d, (int)(e) % 64)));
      { char buf[64]; snprintf(buf, sizeof buf, "%.9g", x); printf("printf %s %08x -> %s strtof %08x\n", mode, fb(x), buf, fb(strtof(buf, NULL))); }
      { volatile double vd = d; volatile float vf = x; printf("cast %s %016llx -> i32 %x i64 %llx u32 %x f->i32 %x\n", mode, (unsigned long long)db(d), (int)vd, (long long)vd, (unsigned)vd, (int)vf); }
   }
   printf("state %s mxcsr %08x controlfp %08x\n", mode, _mm_getcsr(), _controlfp(0, 0));
}
int main(void)
{
   setvbuf(stdout, NULL, _IOFBF, 1 << 20);
   unsigned base = _mm_getcsr();
   run("default");
   _mm_setcsr((base & ~0x6000) | 0x2000); run("mxcsr-rcdown");
   _mm_setcsr((base & ~0x6000) | 0x4000); run("mxcsr-rcup");
   _mm_setcsr((base & ~0x6000) | 0x6000); run("mxcsr-rczero");
   _mm_setcsr(base | 0x8040); run("mxcsr-ftzdaz");
   _mm_setcsr(base);
   unsigned cw; _controlfp_s(&cw, _RC_DOWN, _MCW_RC); run("cfp-rcdown");
   _controlfp_s(&cw, _RC_NEAR, _MCW_RC); _controlfp_s(&cw, _DN_FLUSH, _MCW_DN); run("cfp-dnflush");
   _controlfp_s(&cw, _DN_SAVE, _MCW_DN);
   return 0;
}
