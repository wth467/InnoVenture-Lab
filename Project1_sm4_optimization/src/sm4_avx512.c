#include "sm4.h"
#include "simd_utils.h"
#include <immintrin.h>

#if defined(__AVX512F__) && defined(__GFNI__)

// 用于字节序转换的掩码
static const __m512i swap_mask = _mm512_set_epi8(
    12,13,14,15, 8,9,10,11, 4,5,6,7, 0,1,2,3,
    12,13,14,15, 8,9,10,11, 4,5,6,7, 0,1,2,3,
    12,13,14,15, 8,9,10,11, 4,5,6,7, 0,1,2,3,
    12,13,14,15, 8,9,10,11, 4,5,6,7, 0,1,2,3
);

// 用于S盒的仿射矩阵
static const __m512i affine_mat = _mm512_set1_epi64(0xC3A5E87F6B90D219);

// AVX-512优化的线性变换
__m512i sm4_linear_transform_avx512(__m512i x) {
    __m512i t2 = _mm512_rol_epi32(x, 2);
    __m512i t10 = _mm512_rol_epi32(x, 10);
    __m512i t18 = _mm512_rol_epi32(x, 18);
    __m512i t24 = _mm512_rol_epi32(x, 24);
    
    return _mm512_xor_epi32(
        _mm512_xor_epi32(x, t2),
        _mm512_xor_epi32(t10, _mm512_xor_epi32(t18, t24))
    );
}

// AVX-512优化的SM4加密（处理4个块）
void sm4_avx512_encrypt_blocks(const uint8_t *in, uint8_t *out, size_t blocks,
                              const uint32_t rk[32]) {
    // 将轮密钥加载到寄存器中
    __m512i round_keys[32];
    for (int i = 0; i < 32; i++) {
        round_keys[i] = _mm512_set1_epi32(rk[i]);
    }
    
    for (size_t i = 0; i < blocks; i += 4) {
        // 加载4个块
        __m512i data = _mm512_loadu_si512(in + i * SM4_BLOCK_SIZE);
        
        // 初始置换
        __m512i state = _mm512_shuffle_epi8(data, swap_mask);
        
        // 32轮加密
        for (int r = 0; r < 32; r++) {
            // 轮密钥加
            __m512i t = _mm512_xor_epi32(
                _mm512_xor_epi32(
                    _mm512_xor_epi32(
                        _mm512_srli_epi32(state, 24),
                        _mm512_srli_epi32(_mm512_slli_epi32(state, 8), 24)
                    ),
                    _mm512_xor_epi32(
                        _mm512_srli_epi32(_mm512_slli_epi32(state, 16), 24),
                        round_keys[r])
                );
            
            // 使用GFNI实现S盒
            t = _mm512_gf2p8affineinv_epi64_epi8(t, affine_mat, 0);
            
            // 线性变换
            __m512i l = sm4_linear_transform_avx512(t);
            
            // Feistel结构更新
            __m512i new_val = _mm512_xor_epi32(
                _mm512_srli_epi32(state, 96), l);
            state = _mm512_alignr_epi32(state, new_val, 3);
        }
        
        // 最终置换
        __m512i result = _mm512_shuffle_epi8(state, swap_mask);
        _mm512_storeu_si512(out + i * SM4_BLOCK_SIZE, result);
    }
}

#endif // __AVX512F__ && __GFNI__