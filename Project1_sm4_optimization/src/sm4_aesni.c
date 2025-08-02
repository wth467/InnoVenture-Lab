#include "sm4.h"
#include <wmmintrin.h>
#include <immintrin.h>

#ifdef __AES__

// 用于字节序转换的掩码
static const __m128i swap_mask = _mm_set_epi8(
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
);

// 线性变换常数
static const __m128i L_mask = _mm_set_epi32(0x03020100, 0x0f0e0d0c, 0x0b0a0908, 0x07060504);

// 使用AES-NI指令实现S盒
static inline __m128i sm4_sbox_aesni(__m128i x) {
    const __m128i zero_key = _mm_setzero_si128();
    // 使用AESENCLAST实现S盒
    return _mm_aesenclast_si128(x, zero_key);
}

// AES-NI优化的线性变换
static inline __m128i sm4_linear_transform(__m128i x) {
    // 应用线性变换: L(B) = B ^ (B <<< 2) ^ (B <<< 10) ^ (B <<< 18) ^ (B <<< 24)
    __m128i t2 = _mm_xor_si128(x, _mm_rol_epi32(x, 2));
    __m128i t10 = _mm_xor_si128(t2, _mm_rol_epi32(x, 10));
    __m128i t18 = _mm_xor_si128(t10, _mm_rol_epi32(x, 18));
    return _mm_xor_si128(t18, _mm_rol_epi32(x, 24));
}

// AES-NI优化的轮函数
static inline __m128i sm4_round(__m128i state, __m128i rk) {
    // 轮密钥加
    __m128i t = _mm_xor_si128(state, rk);
    
    // 应用S盒
    t = sm4_sbox_aesni(t);
    
    // 应用线性变换
    return sm4_linear_transform(t);
}

// AES-NI优化的SM4加密（处理单个块）
void sm4_aesni_encrypt_block(const __m128i* in, __m128i* out, const uint32_t rk[32]) {
    __m128i state = _mm_loadu_si128(in);
    
    // 初始置换
    state = _mm_shuffle_epi8(state, swap_mask);
    
    // 32轮迭代
    for (int i = 0; i < 32; i++) {
        // 广播轮密钥
        __m128i round_key = _mm_set1_epi32(rk[i]);
        
        // Feistel结构
        __m128i new_val = sm4_round(_mm_shuffle_epi32(state, 0x39), round_key);
        state = _mm_alignr_epi8(state, new_val, 12);
    }
    
    // 最终置换
    state = _mm_shuffle_epi8(state, swap_mask);
    _mm_storeu_si128(out, state);
}

// AES-NI优化的SM4加密（处理多个块）
void sm4_aesni_encrypt_blocks(const uint8_t *in, uint8_t *out, size_t blocks, 
                             const uint32_t rk[32]) {
    // 将轮密钥加载到寄存器中
    __m128i round_keys[32];
    for (int i = 0; i < 32; i++) {
        round_keys[i] = _mm_set1_epi32(rk[i]);
    }
    
    for (size_t i = 0; i < blocks; i++) {
        __m128i plain = _mm_loadu_si128((const __m128i*)(in + i * 16));
        __m128i cipher;
        sm4_aesni_encrypt_block(&plain, &cipher, rk);
        _mm_storeu_si128((__m128i*)(out + i * 16), cipher);
    }
}

#endif // __AES__