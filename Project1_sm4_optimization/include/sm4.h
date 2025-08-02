#ifndef SM4_H
#define SM4_H

#include <stdint.h>
#include <stddef.h>

// SM4块大小
#define SM4_BLOCK_SIZE 16

// 基础实现
void sm4_encrypt(const uint8_t key[16], const uint8_t in[16], uint8_t out[16]);
void sm4_decrypt(const uint8_t key[16], const uint8_t in[16], uint8_t out[16]);

// 密钥扩展
void sm4_key_expansion(const uint8_t mk[16], uint32_t rk[32]);

// T-table优化
void sm4_ttable_encrypt(uint8_t *block, const uint32_t rk[32]);
void sm4_ttable_decrypt(uint8_t *block, const uint32_t rk[32]);

// AES-NI优化
#if defined(__AES__) && defined(__SSE4_1__)
void sm4_aesni_encrypt_blocks(const uint8_t *in, uint8_t *out, size_t blocks, 
                             const uint32_t rk[32]);
#else
// 如果不支持AES-NI，提供空实现
static inline void sm4_aesni_encrypt_blocks(const uint8_t *in, uint8_t *out, 
                                           size_t blocks, const uint32_t rk[32]) {
    (void)in; (void)out; (void)blocks; (void)rk; // 避免未使用参数警告
}
#endif

// AVX-512优化
#if defined(__AVX512F__) && defined(__GFNI__) && defined(__AVX512VL__)
void sm4_avx512_encrypt_blocks(const uint8_t *in, uint8_t *out, size_t blocks,
                              const uint32_t rk[32]);
#else
// 如果不支持AVX-512，提供空实现
static inline void sm4_avx512_encrypt_blocks(const uint8_t *in, uint8_t *out,
                                            size_t blocks, const uint32_t rk[32]) {
    (void)in; (void)out; (void)blocks; (void)rk; // 避免未使用参数警告
}
#endif

// 性能优化选择函数
void sm4_encrypt_optimized(const uint8_t key[16], const uint8_t *in, 
                          uint8_t *out, size_t blocks);

#endif // SM4_H