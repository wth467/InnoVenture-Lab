// 在文件顶部添加
#if defined(__GNUC__) && !defined(__clang__)
    #pragma GCC target("ssse3,sse4.1,pclmul,aes")
#endif

#ifndef SIMD_UTILS_H
#define SIMD_UTILS_H

#include <stdint.h>
#include <immintrin.h>

// 字节序转换
static inline __m128i byteswap_128(__m128i x) {
    return _mm_shuffle_epi8(x, _mm_set_epi8(
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
    ));
}

// GF(2^128)乘法 - 使用PCLMULQDQ指令
static inline __m128i gf128_mult(__m128i a, __m128i b) {
    // 计算低64位和高64位的乘积
    __m128i t1 = _mm_clmulepi64_si128(a, b, 0x00); // a_low * b_low
    __m128i t2 = _mm_clmulepi64_si128(a, b, 0x11); // a_high * b_high
    __m128i t3 = _mm_clmulepi64_si128(a, b, 0x01); // a_low * b_high
    __m128i t4 = _mm_clmulepi64_si128(a, b, 0x10); // a_high * b_low
    
    // 合并中间结果
    t3 = _mm_xor_si128(t3, t4);
    t4 = _mm_slli_si128(t3, 8);
    t3 = _mm_srli_si128(t3, 8);
    
    t1 = _mm_xor_si128(t1, t4);
    t2 = _mm_xor_si128(t2, t3);
    
    // 模约简（多项式 x^128 + x^7 + x^2 + x + 1）
    const __m128i mod = _mm_set_epi32(0, 0, 0, 0x87);
    __m128i t5 = _mm_clmulepi64_si128(t1, mod, 0x10);
    __m128i t6 = _mm_clmulepi64_si128(t1, mod, 0x01);
    
    t1 = _mm_xor_si128(t1, t5);
    t1 = _mm_xor_si128(t1, t6);
    
    t5 = _mm_clmulepi64_si128(t1, mod, 0x10);
    t6 = _mm_clmulepi64_si128(t1, mod, 0x01);
    
    t1 = _mm_xor_si128(t1, t5);
    t1 = _mm_xor_si128(t1, t6);
    
    return _mm_xor_si128(t1, t2);
}

// AVX-512工具函数
#if defined(__AVX512F__) && defined(__GFNI__)

// AVX-512优化的线性变换
static inline __m512i sm4_linear_transform_avx512(__m512i x) {
    __m512i t2 = _mm512_rol_epi32(x, 2);
    __m512i t10 = _mm512_rol_epi32(x, 10);
    __m512i t18 = _mm512_rol_epi32(x, 18);
    __m512i t24 = _mm512_rol_epi32(x, 24);
    
    return _mm512_xor_epi32(
        _mm512_xor_epi32(x, t2),
        _mm512_xor_epi32(t10, _mm512_xor_epi32(t18, t24))
    );
}

// AVX-512优化的GF(2^128)乘法
static inline __m512i gf512_mult(__m512i a, __m512i b) {
    // 拆分为4个128位块分别处理
    __m128i a0 = _mm512_extracti32x4_epi32(a, 0);
    __m128i a1 = _mm512_extracti32x4_epi32(a, 1);
    __m128i a2 = _mm512_extracti32x4_epi32(a, 2);
    __m128i a3 = _mm512_extracti32x4_epi32(a, 3);
    
    __m128i b0 = _mm512_extracti32x4_epi32(b, 0);
    __m128i b1 = _mm512_extracti32x4_epi32(b, 1);
    __m128i b2 = _mm512_extracti32x4_epi32(b, 2);
    __m128i b3 = _mm512_extracti32x4_epi32(b, 3);
    
    __m128i r0 = gf128_mult(a0, b0);
    __m128i r1 = gf128_mult(a1, b1);
    __m128i r2 = gf128_mult(a2, b2);
    __m128i r3 = gf128_mult(a3, b3);
    
    return _mm512_set_m128i(r3, r2, r1, r0);
}

#endif // __AVX512F__ && __GFNI__

#endif // SIMD_UTILS_H