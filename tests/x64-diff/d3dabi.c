#define COBJMACROS
#define WIDL_C_INLINE_WRAPPERS
#define INITGUID
#include <windows.h>
#include <d3d12.h>
#include <dxgi1_4.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <xmmintrin.h>
uint64_t abi_call(void *fn, const uint64_t *args, const uint8_t *pattern, uint8_t *after);
static int fails, passes;
static void check(const char *name, void *fn, uint64_t a0, uint64_t a1, uint64_t a2, uint64_t a3, int rounds)
{
   uint8_t pat[224], after[224]; uint64_t args[4] = { a0, a1, a2, a3 };
   for (int round = 0; round < rounds; round++) {
      for (int i = 0; i < 224; i++) pat[i] = (uint8_t)(0x5a ^ (i * 37) ^ (round * 91));
      if (round == 1) for (int i = 0; i < 40; i++) { float f = 1.5f + i; memcpy(pat + i * 4, &f, 4); }
      memset(after, 0xcc, sizeof after); unsigned mb = _mm_getcsr();
      abi_call(fn, args, pat, after); unsigned ma = _mm_getcsr();
      char why[256] = ""; int bad = 0;
      for (int r = 0; r < 10; r++) if (memcmp(pat + r * 16, after + r * 16, 16)) { bad = 1;
         snprintf(why + strlen(why), sizeof why - strlen(why), " xmm%d(%s%s)", r + 6, memcmp(pat + r * 16, after + r * 16, 8) ? "lo" : "", memcmp(pat + r * 16 + 8, after + r * 16 + 8, 8) ? "hi" : ""); }
      static const char *gn[] = { "rbx", "rbp", "rdi", "rsi", "r12", "r13", "r14", "r15" };
      for (int r = 0; r < 8; r++) if (memcmp(pat + 160 + r * 8, after + 160 + r * 8, 8)) { bad = 1; snprintf(why + strlen(why), sizeof why - strlen(why), " %s", gn[r]); }
      if ((mb & 0xffc0) != (ma & 0xffc0)) { bad = 1; snprintf(why + strlen(why), sizeof why - strlen(why), " mxcsr %04x->%04x", mb, ma); }
      if (bad) { printf("FAIL %s:%s\n", name, why); fails++; return; }
   }
   printf("PASS %s\n", name); passes++;
}
#define VT(obj, idx) ((*(void ***)(obj))[idx])
int main(void)
{
   setvbuf(stdout, NULL, _IONBF, 0);
   ID3D12Device *dev = NULL; HRESULT hr = D3D12CreateDevice(NULL, D3D_FEATURE_LEVEL_12_0, &IID_ID3D12Device, (void **)&dev);
   printf("INFO D3D12CreateDevice %#lx\n", hr); if (FAILED(hr)) return 1;
   D3D12_DESCRIPTOR_HEAP_DESC hd = { D3D12_DESCRIPTOR_HEAP_TYPE_SAMPLER, 64, D3D12_DESCRIPTOR_HEAP_FLAG_NONE, 0 };
   ID3D12DescriptorHeap *sh = NULL; ID3D12Device_CreateDescriptorHeap(dev, &hd, &IID_ID3D12DescriptorHeap, (void **)&sh);
   hd.Type = D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV; hd.NumDescriptors = 256; ID3D12DescriptorHeap *rh = NULL; ID3D12Device_CreateDescriptorHeap(dev, &hd, &IID_ID3D12DescriptorHeap, (void **)&rh);
   D3D12_CPU_DESCRIPTOR_HANDLE s0 = ID3D12DescriptorHeap_GetCPUDescriptorHandleForHeapStart(sh), r0 = ID3D12DescriptorHeap_GetCPUDescriptorHandleForHeapStart(rh);
   static D3D12_SAMPLER_DESC sd = { D3D12_FILTER_ANISOTROPIC, D3D12_TEXTURE_ADDRESS_MODE_WRAP, D3D12_TEXTURE_ADDRESS_MODE_WRAP, D3D12_TEXTURE_ADDRESS_MODE_WRAP, -0.5f, 16, D3D12_COMPARISON_FUNC_NEVER, {0}, 0.0f, 3.402823466e+38f };
   D3D12_HEAP_PROPERTIES hp = { D3D12_HEAP_TYPE_UPLOAD }; D3D12_RESOURCE_DESC rd = { D3D12_RESOURCE_DIMENSION_BUFFER, 0, 65536, 1, 1, 1, DXGI_FORMAT_UNKNOWN, {1, 0}, D3D12_TEXTURE_LAYOUT_ROW_MAJOR, 0 };
   ID3D12Resource *buf = NULL; hr = ID3D12Device_CreateCommittedResource(dev, &hp, 0, &rd, D3D12_RESOURCE_STATE_GENERIC_READ, NULL, &IID_ID3D12Resource, (void **)&buf); printf("INFO buffer %#lx\n", hr);
   static D3D12_CONSTANT_BUFFER_VIEW_DESC cbv; cbv.BufferLocation = ID3D12Resource_GetGPUVirtualAddress(buf); cbv.SizeInBytes = 256;
   static D3D12_RANGE rr = { 0, 0 }; static void *mapped;
   ID3D12CommandAllocator *ca = NULL; ID3D12Device_CreateCommandAllocator(dev, D3D12_COMMAND_LIST_TYPE_DIRECT, &IID_ID3D12CommandAllocator, (void **)&ca);
   ID3D12GraphicsCommandList *cl = NULL; ID3D12Device_CreateCommandList(dev, 0, D3D12_COMMAND_LIST_TYPE_DIRECT, ca, NULL, &IID_ID3D12GraphicsCommandList, (void **)&cl);
   static uint32_t consts[16] = { 1, 2, 3, 4 };
   /* ID3D12Device vtable: 15 GetNodeCount ... indices from d3d12.h order */
   check("Device.GetDescriptorHandleIncrementSize", (void *)dev->lpVtbl->GetDescriptorHandleIncrementSize, (uint64_t)dev, D3D12_DESCRIPTOR_HEAP_TYPE_SAMPLER, 0, 0, 3);
   check("Device.CreateSampler", (void *)dev->lpVtbl->CreateSampler, (uint64_t)dev, (uint64_t)&sd, s0.ptr, 0, 3);
   check("Device.CreateConstantBufferView", (void *)dev->lpVtbl->CreateConstantBufferView, (uint64_t)dev, (uint64_t)&cbv, r0.ptr, 0, 3);
   check("Device.CopyDescriptorsSimple", (void *)dev->lpVtbl->CopyDescriptorsSimple, (uint64_t)dev, 1, r0.ptr + 64, r0.ptr, 3);
   check("Resource.Map", (void *)buf->lpVtbl->Map, (uint64_t)buf, 0, (uint64_t)&rr, (uint64_t)&mapped, 3);
   check("Resource.Unmap", (void *)buf->lpVtbl->Unmap, (uint64_t)buf, 0, (uint64_t)&rr, 0, 3);
   check("Resource.GetGPUVirtualAddress", (void *)buf->lpVtbl->GetGPUVirtualAddress, (uint64_t)buf, 0, 0, 0, 3);
   check("CommandList.SetGraphicsRoot32BitConstants", (void *)cl->lpVtbl->SetGraphicsRoot32BitConstants, (uint64_t)cl, 0, 4, (uint64_t)consts, 3);
   check("CommandList.IASetPrimitiveTopology", (void *)cl->lpVtbl->IASetPrimitiveTopology, (uint64_t)cl, D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST, 0, 0, 3);
   check("CommandList.SetGraphicsRootConstantBufferView", (void *)cl->lpVtbl->SetGraphicsRootConstantBufferView, (uint64_t)cl, 0, cbv.BufferLocation, 0, 3);
   check("CommandList.Close", (void *)cl->lpVtbl->Close, (uint64_t)cl, 0, 0, 0, 1);
   check("Allocator.Reset", (void *)ca->lpVtbl->Reset, (uint64_t)ca, 0, 0, 0, 1);
   check("Device.AddRef", (void *)dev->lpVtbl->AddRef, (uint64_t)dev, 0, 0, 0, 1);
   check("Device.Release", (void *)dev->lpVtbl->Release, (uint64_t)dev, 0, 0, 0, 1);
   IDXGIFactory4 *fac = NULL; hr = CreateDXGIFactory2(0, &IID_IDXGIFactory4, (void **)&fac);
   if (SUCCEEDED(hr)) { check("DXGIFactory.AddRef", (void *)fac->lpVtbl->AddRef, (uint64_t)fac, 0, 0, 0, 1); check("DXGIFactory.Release", (void *)fac->lpVtbl->Release, (uint64_t)fac, 0, 0, 0, 1); }
   printf("SUMMARY d3dabi pass=%d fail=%d\n", passes, fails);
   return 0;
}
