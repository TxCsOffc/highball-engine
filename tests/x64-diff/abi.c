/* abitest: does every Windows API / CRT function the game might call keep the x64 non-volatile registers
 * (xmm6-xmm15 all 128 bits, rbx, rbp, rdi, rsi, r12-r15), the MXCSR control bits and DF clear? */
#include <windows.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>
#include <xmmintrin.h>
uint64_t abi_call(void *fn, const uint64_t *args, const uint8_t *pattern, uint8_t *after);
static int fails, passes;
static uint8_t buf1[4096], buf2[4096];
static CRITICAL_SECTION cs; static SRWLOCK srw = SRWLOCK_INIT; static HANDLE ev; static DWORD tls; static LONG addrv;
static float fbits(float f) { return f; }
static void check(const char *name, void *fn, uint64_t a0, uint64_t a1, uint64_t a2, uint64_t a3)
{
   uint8_t pat[224], after[224]; uint64_t args[4] = { a0, a1, a2, a3 };
   int rounds = strstr(name, "SRWLockExclusive") ? 1 : 3;
   for (int round = 0; round < rounds; round++) {
      for (int i = 0; i < 224; i++) pat[i] = (uint8_t)(0x5a ^ (i * 37) ^ (round * 91));
      /* make the xmm halves look like floats and NaN-ish patterns too */
      if (round == 1) for (int i = 0; i < 40; i++) { float f = 1.5f + i; memcpy(pat + i * 4, &f, 4); }
      if (round == 2) for (int i = 0; i < 20; i++) { uint64_t n = 0x7ff8dead00000000ull + i; memcpy(pat + i * 8, &n, 8); }
      memset(after, 0xcc, sizeof after);
      unsigned mx_before = _mm_getcsr();
      abi_call(fn, args, pat, after);
      unsigned mx_after = _mm_getcsr();
      int bad = 0; char why[256] = "";
      for (int r = 0; r < 10; r++) if (memcmp(pat + r * 16, after + r * 16, 16)) {
         bad = 1; int lo = memcmp(pat + r * 16, after + r * 16, 8) != 0, hi = memcmp(pat + r * 16 + 8, after + r * 16 + 8, 8) != 0;
         snprintf(why + strlen(why), sizeof why - strlen(why), " xmm%d(%s%s)", r + 6, lo ? "lo" : "", hi ? "hi" : ""); }
      static const char *gn[] = { "rbx", "rbp", "rdi", "rsi", "r12", "r13", "r14", "r15" };
      for (int r = 0; r < 8; r++) if (memcmp(pat + 160 + r * 8, after + 160 + r * 8, 8)) { bad = 1; snprintf(why + strlen(why), sizeof why - strlen(why), " %s", gn[r]); }
      if ((mx_before & 0xffc0) != (mx_after & 0xffc0)) { bad = 1; snprintf(why + strlen(why), sizeof why - strlen(why), " mxcsr %04x->%04x", mx_before, mx_after); }
      if (bad) { printf("FAIL %s round %d:%s\n", name, round, why); fails++; return; }
   }
   printf("PASS %s\n", name); passes++;
}
static DWORD WINAPI thr(void *p) { return 0; }
static void CALLBACK fiberfn(void *p) { SwitchToFiber(p); }
int main(void)
{
   setvbuf(stdout, NULL, _IONBF, 0);
   HMODULE k32 = GetModuleHandleA("kernel32.dll"), nt = GetModuleHandleA("ntdll.dll"), kb = GetModuleHandleA("kernelbase.dll");
   HMODULE ucrt = LoadLibraryA("ucrtbase.dll"), msvcrt = LoadLibraryA("msvcrt.dll"), vcr = LoadLibraryA("vcruntime140.dll");
   InitializeCriticalSection(&cs); ev = CreateEventA(NULL, TRUE, FALSE, NULL); tls = TlsAlloc();
   float f1 = 0.7f, f2 = 3.3f; double d1 = 0.7, d2 = 3.3; uint64_t F1, F2, D1, D2; memcpy(&F1, &f1, 4); F1 &= 0xffffffff; memcpy(&F2, &f2, 4); F2 &= 0xffffffff; memcpy(&D1, &d1, 8); memcpy(&D2, &d2, 8);
   struct { const char *mod; HMODULE h; const char *fn; uint64_t a[4]; } t[] = {
      { "ucrt", ucrt, "memcpy", { (uint64_t)buf1, (uint64_t)buf2, 1000, 0 } }, { "ucrt", ucrt, "memmove", { (uint64_t)buf1 + 3, (uint64_t)buf1, 2000, 0 } },
      { "ucrt", ucrt, "memset", { (uint64_t)buf1, 0x41, 3000, 0 } }, { "ucrt", ucrt, "memcmp", { (uint64_t)buf1, (uint64_t)buf2, 500, 0 } },
      { "ucrt", ucrt, "strlen", { (uint64_t)"hello world", 0, 0, 0 } }, { "ucrt", ucrt, "malloc", { 4096, 0, 0, 0 } },
      { "ucrt", ucrt, "sqrt", { 0, 0, 0, 0 } }, { "ucrt", ucrt, "floor", { 0, 0, 0, 0 } },
      { "vcruntime", vcr, "memcpy", { (uint64_t)buf1, (uint64_t)buf2, 1000, 0 } }, { "vcruntime", vcr, "memset", { (uint64_t)buf1, 0, 999, 0 } },
      { "vcruntime", vcr, "memmove", { (uint64_t)buf1, (uint64_t)buf1 + 7, 1500, 0 } },
      { "msvcrt", msvcrt, "memcpy", { (uint64_t)buf1, (uint64_t)buf2, 1000, 0 } },
      { "k32", k32, "EnterCriticalSection", { (uint64_t)&cs, 0, 0, 0 } }, { "k32", k32, "LeaveCriticalSection", { (uint64_t)&cs, 0, 0, 0 } },
      { "k32", k32, "TryEnterCriticalSection", { (uint64_t)&cs, 0, 0, 0 } }, { "k32", k32, "LeaveCriticalSection", { (uint64_t)&cs, 0, 0, 0 } },
      { "k32", k32, "AcquireSRWLockExclusive", { (uint64_t)&srw, 0, 0, 0 } }, { "k32", k32, "ReleaseSRWLockExclusive", { (uint64_t)&srw, 0, 0, 0 } },
      { "k32", k32, "AcquireSRWLockShared", { (uint64_t)&srw, 0, 0, 0 } }, { "k32", k32, "ReleaseSRWLockShared", { (uint64_t)&srw, 0, 0, 0 } },
      { "k32", k32, "SetEvent", { 0, 0, 0, 0 } }, { "k32", k32, "ResetEvent", { 0, 0, 0, 0 } }, { "k32", k32, "WaitForSingleObject", { 0, 0, 0, 0 } },
      { "k32", k32, "QueryPerformanceCounter", { (uint64_t)buf1, 0, 0, 0 } }, { "k32", k32, "QueryPerformanceFrequency", { (uint64_t)buf1, 0, 0, 0 } },
      { "k32", k32, "GetTickCount64", { 0, 0, 0, 0 } }, { "k32", k32, "GetSystemTimePreciseAsFileTime", { (uint64_t)buf1, 0, 0, 0 } },
      { "k32", k32, "Sleep", { 0, 0, 0, 0 } }, { "k32", k32, "SwitchToThread", { 0, 0, 0, 0 } }, { "k32", k32, "GetCurrentThreadId", { 0, 0, 0, 0 } },
      { "k32", k32, "TlsGetValue", { 0, 0, 0, 0 } }, { "k32", k32, "TlsSetValue", { 0, 0x1234, 0, 0 } }, { "k32", k32, "FlsGetValue", { 1, 0, 0, 0 } },
      { "k32", k32, "HeapAlloc", { 0, 0, 256, 0 } }, { "k32", k32, "GetProcessHeap", { 0, 0, 0, 0 } },
      { "k32", k32, "VirtualAlloc", { 0, 65536, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE } },
      { "k32", k32, "GetLastError", { 0, 0, 0, 0 } }, { "k32", k32, "SetLastError", { 5, 0, 0, 0 } },
      { "kb", kb, "WakeByAddressSingle", { (uint64_t)&addrv, 0, 0, 0 } }, { "kb", kb, "WaitOnAddress", { (uint64_t)&addrv, (uint64_t)&addrv + 0, 4, 0 } },
      { "nt", nt, "RtlCaptureStackBackTrace", { 0, 8, (uint64_t)buf1, 0 } }, { "nt", nt, "RtlQueryPerformanceCounter", { (uint64_t)buf1, 0, 0, 0 } },
      { "nt", nt, "NtYieldExecution", { 0, 0, 0, 0 } }, { "nt", nt, "RtlEnterCriticalSection", { (uint64_t)&cs, 0, 0, 0 } }, { "nt", nt, "RtlLeaveCriticalSection", { (uint64_t)&cs, 0, 0, 0 } },
      { "nt", nt, "RtlCompareMemory", { (uint64_t)buf1, (uint64_t)buf2, 512, 0 } }, { "nt", nt, "RtlCopyMemory", { (uint64_t)buf1, (uint64_t)buf2, 512, 0 } },
      { "nt", nt, "RtlMoveMemory", { (uint64_t)buf1, (uint64_t)buf2, 512, 0 } }, { "nt", nt, "RtlFillMemory", { (uint64_t)buf1, 512, 7, 0 } }, { "nt", nt, "RtlZeroMemory", { (uint64_t)buf1, 512, 0, 0 } },
   };
   for (unsigned i = 0; i < sizeof t / sizeof t[0]; i++) {
      if (!strcmp(t[i].fn, "SetEvent") || !strcmp(t[i].fn, "ResetEvent")) t[i].a[0] = (uint64_t)ev;
      if (!strcmp(t[i].fn, "WaitForSingleObject")) { t[i].a[0] = (uint64_t)ev; t[i].a[1] = 0; }
      if (!strcmp(t[i].fn, "TlsGetValue") || !strcmp(t[i].fn, "TlsSetValue")) t[i].a[0] = tls;
      if (!strcmp(t[i].fn, "HeapAlloc")) t[i].a[0] = (uint64_t)GetProcessHeap();
      if (!strcmp(t[i].fn, "WaitOnAddress")) { static LONG cmp = 1; t[i].a[1] = (uint64_t)&cmp; t[i].a[3] = 0; }
      void *fn = t[i].h ? (void *)GetProcAddress(t[i].h, t[i].fn) : NULL;
      char name[96]; snprintf(name, sizeof name, "%s.%s", t[i].mod, t[i].fn);
      if (!fn) { printf("SKIP %s (not found)\n", name); continue; }
      check(name, fn, t[i].a[0], t[i].a[1], t[i].a[2], t[i].a[3]);
   }
   /* float math through the CRT: the arguments go in xmm0/xmm1, set by a C wrapper */
   static const char *fm[] = { "sinf", "cosf", "tanf", "sqrtf", "powf", "expf", "logf", "atan2f", "floorf", "ceilf", "fmodf", "acosf", "asinf", "atanf", "sin", "cos", "pow", "exp", "log", "atan2", "fmod", "exp2f", "log2f", "roundf", "truncf", "lrintf", "hypotf" };
   for (unsigned i = 0; i < sizeof fm / sizeof fm[0]; i++) {
      void *fn = GetProcAddress(ucrt, fm[i]); char name[64]; snprintf(name, sizeof name, "ucrt.%s", fm[i]);
      if (!fn) { printf("SKIP %s\n", name); continue; }
      check(name, fn, 0, 0, 0, 0);
   }
   printf("SUMMARY abitest pass=%d fail=%d\n", passes, fails);
   return 0;
}
