# uint64_t abi_call(void *fn, const uint64_t *args4, const uint8_t *pattern /* 10*16 xmm + 8*8 gpr */, uint8_t *after /* same layout */)
# Windows x64 ABI: rcx, rdx, r8, r9. Loads the pattern into xmm6-xmm15, rbx, rbp, rdi, rsi, r12-r15, calls fn(args...),
# stores those registers after the call into 'after', returns rax.
    .text
    .globl abi_call
abi_call:
    push %rbp
    push %rbx
    push %rdi
    push %rsi
    push %r12
    push %r13
    push %r14
    push %r15
    sub $(10*16 + 8 + 64), %rsp          # xmm save area + align + scratch
    movdqu %xmm6, 0(%rsp)
    movdqu %xmm7, 16(%rsp)
    movdqu %xmm8, 32(%rsp)
    movdqu %xmm9, 48(%rsp)
    movdqu %xmm10, 64(%rsp)
    movdqu %xmm11, 80(%rsp)
    movdqu %xmm12, 96(%rsp)
    movdqu %xmm13, 112(%rsp)
    movdqu %xmm14, 128(%rsp)
    movdqu %xmm15, 144(%rsp)
    mov %r9, 160(%rsp)                   # after
    mov %rcx, %rax                       # fn
    mov %rdx, %r10                       # args
    movdqu 0(%r8), %xmm6
    movdqu 16(%r8), %xmm7
    movdqu 32(%r8), %xmm8
    movdqu 48(%r8), %xmm9
    movdqu 64(%r8), %xmm10
    movdqu 80(%r8), %xmm11
    movdqu 96(%r8), %xmm12
    movdqu 112(%r8), %xmm13
    movdqu 128(%r8), %xmm14
    movdqu 144(%r8), %xmm15
    mov 160(%r8), %rbx
    mov 168(%r8), %rbp
    mov 176(%r8), %rdi
    mov 184(%r8), %rsi
    mov 192(%r8), %r12
    mov 200(%r8), %r13
    mov 208(%r8), %r14
    mov 216(%r8), %r15
    mov 0(%r10), %rcx
    mov 8(%r10), %rdx
    mov 24(%r10), %r9
    mov 16(%r10), %r8
    sub $40, %rsp                        # shadow space (keeps 16-byte alignment)
    call *%rax
    add $40, %rsp
    mov 160(%rsp), %r10
    movdqu %xmm6, 0(%r10)
    movdqu %xmm7, 16(%r10)
    movdqu %xmm8, 32(%r10)
    movdqu %xmm9, 48(%r10)
    movdqu %xmm10, 64(%r10)
    movdqu %xmm11, 80(%r10)
    movdqu %xmm12, 96(%r10)
    movdqu %xmm13, 112(%r10)
    movdqu %xmm14, 128(%r10)
    movdqu %xmm15, 144(%r10)
    mov %rbx, 160(%r10)
    mov %rbp, 168(%r10)
    mov %rdi, 176(%r10)
    mov %rsi, 184(%r10)
    mov %r12, 192(%r10)
    mov %r13, 200(%r10)
    mov %r14, 208(%r10)
    mov %r15, 216(%r10)
    movdqu 0(%rsp), %xmm6
    movdqu 16(%rsp), %xmm7
    movdqu 32(%rsp), %xmm8
    movdqu 48(%rsp), %xmm9
    movdqu 64(%rsp), %xmm10
    movdqu 80(%rsp), %xmm11
    movdqu 96(%rsp), %xmm12
    movdqu 112(%rsp), %xmm13
    movdqu 128(%rsp), %xmm14
    movdqu 144(%rsp), %xmm15
    add $(10*16 + 8 + 64), %rsp
    pop %r15
    pop %r14
    pop %r13
    pop %r12
    pop %rsi
    pop %rdi
    pop %rbx
    pop %rbp
    ret
