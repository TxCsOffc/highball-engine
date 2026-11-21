# fexdiff3: each test runs an asm snippet with ymm0=R, ymm1=A, ymm2=B, ymm3=I (small lane indices), rsi=M (256 bytes),
# rax/rcx/rdx/rbx random; dumps ymm0, ymm1, M[0..95], rax, rcx, rflags(arith bits) as hex.
T = []
def t(name, asm, kind='f'): T.append((name, asm, kind))
# VEX scalar with memory operands
for o in ('vaddss','vsubss','vmulss','vdivss','vminss','vmaxss','vsqrtss'):
    t(o+'_m', o + ' 8(%%rsi), %%xmm1, %%xmm0')
for o in ('vaddsd','vmulsd','vdivsd','vminsd','vmaxsd','vsqrtsd'):
    t(o+'_m', o + ' 8(%%rsi), %%xmm1, %%xmm0', 'd')
for o in ('vfmadd231ss','vfmadd213ss','vfmadd132ss','vfnmadd231ss','vfmsub231ss','vfnmsub213ss'):
    t(o+'_m', o + ' 4(%%rsi), %%xmm1, %%xmm0')
for o in ('vfmadd231ps','vfmadd213ps','vfnmadd231ps','vfmsub213ps','vfmadd231pd'):
    t(o+'_my', o + ' 32(%%rsi), %%ymm1, %%ymm0', 'd' if o.endswith('pd') else 'f')
for imm in (0,1,2,3,4,9,10,11):
    t('vroundss%d_m' % imm, 'vroundss $%d, 12(%%%%rsi), %%%%xmm1, %%%%xmm0' % imm)
    t('vroundps%d_my' % imm, 'vroundps $%d, (%%%%rsi), %%%%ymm0' % imm)
t('vmovss_load', 'vmovss 4(%%rsi), %%xmm0'); t('vmovss_merge', 'vmovss %%xmm2, %%xmm1, %%xmm0')
t('vmovss_store', 'vmovss %%xmm1, 4(%%rsi)'); t('vmovsd_load', 'vmovsd 8(%%rsi), %%xmm0', 'd')
t('vmovlps', 'vmovlps 8(%%rsi), %%xmm1, %%xmm0'); t('vmovhps', 'vmovhps 8(%%rsi), %%xmm1, %%xmm0'); t('vmovhps_st', 'vmovhps %%xmm1, 8(%%rsi)')
t('vinsertps_m', 'vinsertps $0x30, 12(%%rsi), %%xmm1, %%xmm0'); t('vinsertps_r', 'vinsertps $0x9d, %%xmm2, %%xmm1, %%xmm0')
t('vextractps', 'vextractps $2, %%xmm1, 4(%%rsi)'); t('vpextrd', 'vpextrd $3, %%xmm1, %%eax'); t('vpinsrd', 'vpinsrd $1, 4(%%rsi), %%xmm1, %%xmm0')
t('vcvtsi2ss_m', 'vcvtsi2ssl 4(%%rsi), %%xmm1, %%xmm0'); t('vcvtsi2sd_q', 'vcvtsi2sdq %%rax, %%xmm1, %%xmm0', 'd'); t('vcvtsi2ss_q', 'vcvtsi2ssq %%rax, %%xmm1, %%xmm0')
t('vcvttss2si_m', 'vcvttss2si 4(%%rsi), %%eax'); t('vcvtss2si_m', 'vcvtss2si 4(%%rsi), %%rax'); t('vcvttsd2si_m', 'vcvttsd2si 8(%%rsi), %%rax', 'd')
t('vcvtss2sd_m', 'vcvtss2sd 4(%%rsi), %%xmm1, %%xmm0'); t('vcvtsd2ss_m', 'vcvtsd2ss 8(%%rsi), %%xmm1, %%xmm0', 'd')
t('vcvtps2pd_my', 'vcvtps2pd (%%rsi), %%ymm0'); t('vcvtpd2ps_my', 'vcvtpd2psy (%%rsi), %%xmm0', 'd'); t('vcvtdq2ps_my', 'vcvtdq2ps (%%rsi), %%ymm0', 'i')
t('vcvttps2dq_my', 'vcvttps2dq (%%rsi), %%ymm0'); t('vcvtps2dq_my', 'vcvtps2dq (%%rsi), %%ymm0'); t('vcvtph2ps_m', 'vcvtph2ps (%%rsi), %%ymm0', 'h')
t('vcvtps2ph_m', 'vcvtps2ph $4, %%ymm1, (%%rsi)'); t('vcvtps2ph0_m', 'vcvtps2ph $0, %%ymm1, 16(%%rsi)')
# 256-bit loads/stores/broadcasts/inserts
t('vbroadcastss_m', 'vbroadcastss 4(%%rsi), %%ymm0'); t('vbroadcastss_r', 'vbroadcastss %%xmm1, %%ymm0'); t('vbroadcastsd_m', 'vbroadcastsd 8(%%rsi), %%ymm0', 'd')
t('vbroadcastf128', 'vbroadcastf128 16(%%rsi), %%ymm0'); t('vpbroadcastd_m', 'vpbroadcastd 4(%%rsi), %%ymm0', 'i'); t('vpbroadcastb', 'vpbroadcastb %%xmm1, %%ymm0', 'i')
t('vpbroadcastw_m', 'vpbroadcastw 2(%%rsi), %%ymm0', 'i'); t('vpbroadcastq', 'vpbroadcastq %%xmm1, %%ymm0', 'i')
t('vinsertf128_m', 'vinsertf128 $1, 16(%%rsi), %%ymm1, %%ymm0'); t('vinsertf128_0', 'vinsertf128 $0, %%xmm2, %%ymm1, %%ymm0')
t('vextractf128_m', 'vextractf128 $1, %%ymm1, 32(%%rsi)'); t('vextractf128_r', 'vextractf128 $1, %%ymm1, %%xmm0'); t('vextracti128', 'vextracti128 $1, %%ymm2, %%xmm0', 'i')
t('vmaskmovps_ld', 'vmaskmovps (%%rsi), %%ymm2, %%ymm0'); t('vmaskmovps_st', 'vmaskmovps %%ymm1, %%ymm2, 8(%%rsi)'); t('vmaskmovpd_st', 'vmaskmovpd %%ymm1, %%ymm2, 8(%%rsi)', 'd')
t('vpmaskmovd_ld', 'vpmaskmovd 4(%%rsi), %%ymm2, %%ymm0', 'i'); t('vpmaskmovd_st', 'vpmaskmovd %%ymm1, %%ymm2, 4(%%rsi)', 'i'); t('vmaskmovps_ld128', 'vmaskmovps 4(%%rsi), %%xmm2, %%xmm0')
t('vmovups_ld', 'vmovups 4(%%rsi), %%ymm0'); t('vmovups_st', 'vmovups %%ymm1, 4(%%rsi)'); t('vmovntps', 'vmovntps %%ymm1, 32(%%rsi)\\n sfence')
t('vlddqu', 'vlddqu 3(%%rsi), %%ymm0', 'i'); t('vmovddup_y', 'vmovddup %%ymm1, %%ymm0', 'd'); t('vmovsldup_y', 'vmovsldup %%ymm1, %%ymm0'); t('vmovshdup_m', 'vmovshdup (%%rsi), %%ymm0')
# gathers (indices from ymm3 / xmm3 = 0..15)
t('vgatherdps', 'vmovaps %%ymm2, %%ymm4\\n vgatherdps %%ymm4, (%%rsi,%%ymm3,4), %%ymm0'); t('vgatherdps_x', 'vmovaps %%xmm2, %%xmm4\\n vgatherdps %%xmm4, 8(%%rsi,%%xmm3,4), %%xmm0')
t('vgatherqps', 'vmovaps %%xmm2, %%xmm4\\n vgatherqps %%xmm4, (%%rsi,%%ymm5,4), %%xmm0'); t('vgatherdpd', 'vmovapd %%ymm2, %%ymm4\\n vgatherdpd %%ymm4, (%%rsi,%%xmm3,8), %%ymm0', 'd')
t('vpgatherdd', 'vmovdqa %%ymm2, %%ymm4\\n vpgatherdd %%ymm4, (%%rsi,%%ymm3,4), %%ymm0', 'i'); t('vpgatherdq', 'vmovdqa %%ymm2, %%ymm4\\n vpgatherdq %%ymm4, (%%rsi,%%xmm3,8), %%ymm0', 'i')
t('vgatherdps_mask', 'vmovaps %%ymm2, %%ymm4\\n vgatherdps %%ymm4, (%%rsi,%%ymm3,4), %%ymm0\\n vmovaps %%ymm4, %%ymm1')
t('vgatherdps_s2', 'vmovaps %%ymm2, %%ymm4\\n vgatherdps %%ymm4, 2(%%rsi,%%ymm3,2), %%ymm0')
# shuffles / lane ops 256
for imm in (0x1b, 0xb1, 0x4e, 0xe4, 0x00):
    t('vshufps%x_y' % imm, 'vshufps $%d, %%%%ymm2, %%%%ymm1, %%%%ymm0' % imm); t('vpshufd%x_y' % imm, 'vpshufd $%d, %%%%ymm1, %%%%ymm0' % imm, 'i')
    t('vpermilps%x_y' % imm, 'vpermilps $%d, %%%%ymm1, %%%%ymm0' % imm)
for imm in (1, 4, 8, 12, 15):
    t('vpalignr%d_y' % imm, 'vpalignr $%d, %%%%ymm2, %%%%ymm1, %%%%ymm0' % imm, 'i'); t('vpsrldq%d_y' % imm, 'vpsrldq $%d, %%%%ymm1, %%%%ymm0' % imm, 'i'); t('vpslldq%d_y' % imm, 'vpslldq $%d, %%%%ymm1, %%%%ymm0' % imm, 'i')
t('vpermilps_v', 'vpermilps %%ymm3, %%ymm1, %%ymm0'); t('vpermilpd_v', 'vpermilpd %%ymm3, %%ymm1, %%ymm0', 'd'); t('vpermps_m', 'vpermps (%%rsi), %%ymm3, %%ymm0')
t('vperm2i128', 'vperm2i128 $0x13, %%ymm2, %%ymm1, %%ymm0', 'i'); t('vunpcklps_y', 'vunpcklps %%ymm2, %%ymm1, %%ymm0'); t('vunpckhpd_y', 'vunpckhpd %%ymm2, %%ymm1, %%ymm0', 'd')
t('vpmovzxbd', 'vpmovzxbd 4(%%rsi), %%ymm0', 'i'); t('vpmovsxwd', 'vpmovsxwd (%%rsi), %%ymm0', 'i'); t('vpmovzxwq', 'vpmovzxwq %%xmm1, %%ymm0', 'i'); t('vpmovsxbw', 'vpmovsxbw %%xmm1, %%ymm0', 'i')
t('vpmovzxdq', 'vpmovzxdq 8(%%rsi), %%ymm0', 'i'); t('vpackusdw_y', 'vpackusdw %%ymm2, %%ymm1, %%ymm0', 'i'); t('vpackuswb_y', 'vpackuswb %%ymm2, %%ymm1, %%ymm0', 'i')
for imm in range(0, 32, 3):
    t('vcmpps%d_y' % imm, 'vcmpps $%d, %%%%ymm2, %%%%ymm1, %%%%ymm0' % imm); t('vcmpss%d_m' % imm, 'vcmpss $%d, 4(%%%%rsi), %%%%xmm1, %%%%xmm0' % imm)
t('vblendvps_m', 'vblendvps %%ymm2, (%%rsi), %%ymm1, %%ymm0'); t('vtestps', 'vtestps %%ymm2, %%ymm1'); t('vtestpd', 'vtestpd %%ymm2, %%ymm1', 'd')
t('vpsllvq', 'vpsllvq %%ymm3, %%ymm1, %%ymm0', 'i'); t('vpsrlvq', 'vpsrlvq %%ymm2, %%ymm1, %%ymm0', 'i'); t('vpsravd_big', 'vpsravd %%ymm2, %%ymm1, %%ymm0', 'i')
t('vpsrld_x', 'vpsrld %%xmm3, %%ymm1, %%ymm0', 'i'); t('vpsraw_i', 'vpsraw $3, %%ymm1, %%ymm0', 'i'); t('vpmuludq_y', 'vpmuludq %%ymm2, %%ymm1, %%ymm0', 'i'); t('vpmulhuw_y', 'vpmulhuw %%ymm2, %%ymm1, %%ymm0', 'i')
t('vpminud_y', 'vpminud %%ymm2, %%ymm1, %%ymm0', 'i'); t('vpcmpeqq_y', 'vpcmpeqq %%ymm2, %%ymm1, %%ymm0', 'i'); t('vpcmpgtq_y', 'vpcmpgtq %%ymm2, %%ymm1, %%ymm0', 'i'); t('vpabsd_y', 'vpabsd %%ymm1, %%ymm0', 'i')
t('vpmovmskb_y', 'vpmovmskb %%ymm1, %%eax', 'i'); t('vmovmskpd_y', 'vmovmskpd %%ymm1, %%eax', 'd')
# SSE/AVX mixing: legacy SSE must preserve the upper ymm half, VEX.128 must zero it
t('mix_legacy_addps', 'addps %%xmm2, %%xmm0'); t('mix_legacy_movss', 'movss 4(%%rsi), %%xmm0'); t('mix_legacy_cvtsi2ss', 'cvtsi2ss %%eax, %%xmm0')
t('mix_legacy_sqrtss', 'sqrtss %%xmm2, %%xmm0'); t('mix_legacy_shufps', 'shufps $0x1b, %%xmm2, %%xmm0'); t('mix_legacy_pinsrd', 'pinsrd $2, %%eax, %%xmm0', 'i')
t('mix_vex128_addps', 'vaddps %%xmm2, %%xmm1, %%xmm0'); t('mix_vzeroupper_then_sse', 'vzeroupper\\n addps %%xmm2, %%xmm0'); t('mix_vzeroall', 'vzeroall\\n vmovaps %%ymm1, %%ymm1')
t('mix_movd', 'vmovd %%eax, %%xmm0', 'i'); t('mix_legacy_movd', 'movd %%eax, %%xmm0', 'i'); t('mix_legacy_movlps', 'movlps 8(%%rsi), %%xmm0'); t('mix_legacy_cvtss2sd', 'cvtss2sd %%xmm2, %%xmm0')
# BMI1/BMI2/LZCNT/POPCNT and flags
for o in ('andn %%rcx, %%rdx, %%rax', 'bextr %%rcx, %%rdx, %%rax', 'blsi %%rdx, %%rax', 'blsr %%rdx, %%rax', 'blsmsk %%rdx, %%rax', 'tzcnt %%rdx, %%rax', 'lzcnt %%rdx, %%rax',
          'popcnt %%rdx, %%rax', 'pdep %%rcx, %%rdx, %%rax', 'pext %%rcx, %%rdx, %%rax', 'shlx %%rcx, %%rdx, %%rax', 'shrx %%rcx, %%rdx, %%rax', 'sarx %%rcx, %%rdx, %%rax',
          'rorx $13, %%rdx, %%rax', 'mulx %%rcx, %%rbx, %%rax', 'bzhi %%rcx, %%rdx, %%rax', 'tzcnt %%edx, %%eax', 'lzcnt %%edx, %%eax', 'bsf %%rdx, %%rax', 'bsr %%rdx, %%rax',
          'imul %%rcx, %%rax', 'crc32q %%rcx, %%rax', 'crc32l %%ecx, %%eax', 'crc32b %%cl, %%eax', 'bt %%rcx, %%rax', 'btc %%rcx, %%rax',
          'shld %%cl, %%rdx, %%rax', 'shrd %%cl, %%rdx, %%rax', 'rcl %%cl, %%rax', 'rcr $3, %%rax', 'sar %%cl, %%eax', 'neg %%rax', 'cmpxchg %%rcx, (%%rsi)', 'xadd %%rax, 8(%%rsi)'):
    t('g_' + o.split()[0] + ('_' + o.split()[1].strip('%,$') if o.split()[0] in ('tzcnt','lzcnt','crc32b','crc32l','crc32q','rcr','sar') else '') + '_%d' % len(T), o, 'g')
out = [r'''#include <stdio.h>
#include <stdint.h>
#include <string.h>
static uint64_t rs;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static const uint32_t sp32[] = { 0x00000000, 0x80000000, 0x3f800000, 0xbf800000, 0x7f800000, 0xff800000, 0x7fc00000, 0xffc00000, 0x7fa00001, 0x00000001,
   0x80000001, 0x007fffff, 0x00800000, 0x7f7fffff, 0x4f000000, 0xcf000000, 0x3f000000, 0x3fc00000, 0x40200000, 0x4b000001, 0x4effffff, 0x3eaaaaab };
static const uint64_t sp64[] = { 0, 0x8000000000000000ull, 0x3ff0000000000000ull, 0x7ff0000000000000ull, 0x7ff8000000000000ull, 0xfff8000000000000ull,
   0x7ff4000000000001ull, 1, 0x000fffffffffffffull, 0x43e0000000000000ull, 0x41e0000000000000ull, 0x3fe0000000000000ull, 0x4004000000000000ull };
static void fillv(uint8_t *v, int n, char kind)
{
   for (int i = 0; i < n; i += 8) { uint64_t r = rnd(); memcpy(v + i, &r, 8); }
   if (kind == 'f' || kind == 'g') for (int i = 0; i < n / 4; i++) { uint64_t r = rnd(); uint32_t x;
      if ((r & 3) == 0) x = sp32[(r >> 8) % (sizeof(sp32) / 4)]; else if ((r & 3) == 1) { float f = (float)((int32_t)(r >> 16) % 4000) / 32.0f; memcpy(&x, &f, 4); } else continue; memcpy(v + i * 4, &x, 4); }
   if (kind == 'd') for (int i = 0; i < n / 8; i++) { uint64_t r = rnd(); uint64_t x;
      if ((r & 3) == 0) x = sp64[(r >> 8) % (sizeof(sp64) / 8)]; else if ((r & 3) == 1) { double d = (double)((int32_t)(r >> 16) % 4000) / 32.0; memcpy(&x, &d, 8); } else continue; memcpy(v + i * 8, &x, 8); }
   if (kind == 'h') for (int i = 0; i < n / 2; i++) { uint16_t h = (uint16_t)rnd(); if ((h & 7) == 0) h &= 0x83ff; memcpy(v + i * 2, &h, 2); }
}
static void hex(char *o, const uint8_t *v, int n) { static const char h[] = "0123456789abcdef"; for (int i = n - 1; i >= 0; i--) { *o++ = h[v[i] >> 4]; *o++ = h[v[i] & 15]; } *o = 0; }
static const uint32_t modes[] = { 0x1f80, 0x3f80, 0x7f80, 0x9fc0 };
''']
for i, (name, asm, kind) in enumerate(T):
    out.append(r'''static void t_%d(void)
{
   uint8_t R[32] __attribute__((aligned(32))), A[32] __attribute__((aligned(32))), B[32] __attribute__((aligned(32))), I[32] __attribute__((aligned(32))), Q[32] __attribute__((aligned(32))), M[256] __attribute__((aligned(32)));
   uint64_t g[4], fl; char line[700]; uint8_t out[32 + 32 + 96 + 24];
   for (int m = 0; m < 4; m++) for (int c = 0; c < 48; c++) {
      fillv(R, 32, '%c'); fillv(A, 32, '%c'); fillv(B, 32, '%c'); fillv(M, 256, '%c');
      for (int k = 0; k < 8; k++) { uint32_t ix = (uint32_t)(rnd() %% 16); memcpy(I + 4 * k, &ix, 4); }
      for (int k = 0; k < 4; k++) { uint64_t ix = rnd() %% 24; memcpy(Q + 8 * k, &ix, 8); }
      for (int k = 0; k < 4; k++) g[k] = rnd() >> (rnd() & 63);
      if (c & 1) g[1] &= 63;
      uint32_t md = modes[m], mx; __asm__ volatile("ldmxcsr %%0" : : "m"(md));
      __asm__ volatile("vmovdqu (%%[R]), %%%%ymm0\n vmovdqu (%%[A]), %%%%ymm1\n vmovdqu (%%[B]), %%%%ymm2\n vmovdqu (%%[I]), %%%%ymm3\n vmovdqu (%%[Q]), %%%%ymm5\n"
         " mov (%%[g]), %%%%rax\n mov 8(%%[g]), %%%%rcx\n mov 16(%%[g]), %%%%rdx\n mov 24(%%[g]), %%%%rbx\n mov %%[M], %%%%rsi\n"
         " %s\n"
         " vmovdqu %%%%ymm0, (%%[o])\n vmovdqu %%%%ymm1, 32(%%[o])\n mov %%%%rax, 160(%%[o])\n mov %%%%rcx, 168(%%[o])\n pushfq\n pop %%%%rax\n mov %%%%rax, 176(%%[o])\n vzeroupper\n"
         : : [R] "r"(R), [A] "r"(A), [B] "r"(B), [I] "r"(I), [Q] "r"(Q), [g] "r"(g), [M] "r"(M), [o] "r"(out) : "rax", "rbx", "rcx", "rdx", "rsi", "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7", "xmm8", "xmm9", "xmm10", "xmm11", "xmm12", "xmm13", "xmm14", "xmm15", "memory", "cc");
      __asm__ volatile("stmxcsr %%0" : "=m"(mx)); uint32_t def = 0x1f80; __asm__ volatile("ldmxcsr %%0" : : "m"(def));
      memcpy(out + 64, M, 96); memcpy(&fl, out + 176, 8); fl &= 0x8d5; memcpy(out + 176, &fl, 8);
      hex(line, out, 184); printf("%s m%%d c%%d %%s mx%%04x\n", m, c, line, mx & 0xffff);
   }
}
''' % (i, kind, kind if kind != 'h' else 'f', kind if kind != 'h' else 'f', kind, asm, name))
out.append('int main(void) {\n   setvbuf(stdout, 0, _IOFBF, 1 << 20);\n')
for i, (name, asm, kind) in enumerate(T):
    out.append('   rs = 0x9e3779b97f4a7c15ull + %du * 7919u; t_%d();\n' % (i, i))
out.append('   return 0;\n}\n')
open('fexdiff3.c', 'w').write(''.join(out)); print(len(T), 'tests')
