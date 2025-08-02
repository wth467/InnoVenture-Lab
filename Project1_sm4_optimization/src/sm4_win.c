#include "sm4.h"
#include <windows.h>
#include <intrin.h>

// Windows专用的字节序处理函数
uint32_t byteswap_uint32(uint32_t value) {
    return _byteswap_ulong(value);
}

// Windows专用的内存对齐分配
void* aligned_malloc(size_t size, size_t alignment) {
    return _aligned_malloc(size, alignment);
}

// Windows专用的内存对齐释放
void aligned_free(void* ptr) {
    _aligned_free(ptr);
}

// Windows专用的轮转指令
uint32_t rotl(uint32_t x, int n) {
    return _rotl(x, n);
}

// Windows专用的SIMD指令实现
#if defined(_MSC_VER) && defined(__AVX2__)
#include <immintrin.h>

__m128i sm4_sbox_aesni_win(__m128i x) {
    const __m128i zero_key = _mm_setzero_si128();
    return _mm_aesenclast_si128(x, zero_key);
}

void sm4_aesni_encrypt_blocks_win(const uint8_t *in, uint8_t *out, size_t blocks, 
                                 const uint32_t rk[32]) {
    // 实现与Linux版本类似的AES-NI优化
    // ...
}

#endif