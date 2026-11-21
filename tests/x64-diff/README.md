# x64-diff: x86 reference runs against the arm64 line

These tools run the same x86-64 code twice: as a macOS x86-64 program under Rosetta 2, which is the reference,
and as a Windows x64 program under Wine on the arm64 line (FEX). They then compare every result bit.

| Tool | What it checks |
|---|---|
| `fexdiff_gen.py` → `fexdiff.c` | 455 SSE/AVX/AVX2/FMA/F16C/x87 instructions, register forms, 64 cases (special and random values) in each of 7 MXCSR modes (rounding, FTZ, DAZ) |
| `fexdiff3_gen.py` → `fexdiff3.c` | 230 more: VEX memory operands, 256-bit loads/stores, gathers, `vmaskmov`, broadcasts, inserts/extracts, lane shuffles, SSE/AVX mixing (upper ymm halves), BMI1/BMI2/LZCNT/POPCNT/CRC32, `cmpxchg`, `xadd` |
| `crtdiff.c` | ucrtbase math and conversions (`floor`, `lrint`, `sin`, `pow`, `fmod`, `strtof`, casts, ...) under `_mm_setcsr` and `_controlfp` states; compare an ARM64EC Wine against an x64 Wine |
| `abi.c` + `abi_asm.S` | x64 callee-saved state across calls into Wine (CRT, kernel32, kernelbase, ntdll): xmm6-xmm15 (all 128 bits), rbx, rbp, rdi, rsi, r12-r15, MXCSR control bits |
| `d3dabi.c` + `abi_asm.S` | the same check across D3D12/DXGI methods (vkd3d-proton and DXVK as ARM64EC) |
| `mesa_cache_msl.py` | pulls every MSL source out of a KosmicKrisp Mesa disk cache, so two builds (arm64, x86_64) can be compared shader by shader |

## Build and run

```sh
TC=~/Developer/hb-wine/toolchains/llvm-mingw/bin
python3 fexdiff_gen.py                    # writes fexdiff.c
clang -arch x86_64 -O1 -mavx2 -mfma -mf16c -msse4.2 fexdiff.c -o fexdiff_mac
$TC/x86_64-w64-mingw32-clang -O1 -mavx2 -mfma -mf16c -msse4.2 fexdiff.c -o fexdiff.exe
arch -x86_64 ./fexdiff_mac > ref.txt
WINEPREFIX=<arm64 bottle> <engine>/bin/wine fexdiff.exe > fex.txt    # HB_FEX_* variables apply
python3 fexdiff_cmp.py ref.txt fex.txt
```

`fexdiff3` builds the same way with `-mbmi -mbmi2 -mlzcnt -mpopcnt` added. Its comparison is `fexdiff3_cmp.py`
(it reads `ref.txt` and `fex.txt`).

The ABI tests need no reference. Build with `$TC/x86_64-w64-mingw32-clang -O1 abi.c abi_asm.S -o abitest.exe`.
For `d3dabi.c`, add `-ld3d12 -ldxgi -luuid` and run with the renderer's `WINEDLLPATH_PREPEND`,
`WINEDLLOVERRIDES` and `VK_DRIVER_FILES`. Each one prints `PASS`/`FAIL` lines and a `SUMMARY`.

## Results on FEX (M5 Max, Wine 11.18 arm64, 2026-11-21)

- **`HB_FEX_LAZY_AFP=0`.** Values match Rosetta everywhere except the NaN sign of `vfmaddsub`/`vfmsubadd`.
  `vroundps`/`vroundss` don't set MXCSR.PE.
- **`HB_FEX_LAZY_AFP=1`.** Values differ in 165 instructions: NaN propagation, FTZ applied to inputs, and
  denormal min/max. The fix that stops scalar `MINSS`/`MAXSS`/`MINSD`/`MAXSD` from zeroing the upper lanes is in 0035.
- **Rosetta 2 itself is wrong in three places.** `vpsllvq` with counts above 63 (it should give 0),
  the flags of `cmpxchg` (it computes them reversed), and `adcx`/`adox` (SIGILL).
- **ABI.** 76 Wine functions and the D3D12 calls tested keep every callee-saved register.
