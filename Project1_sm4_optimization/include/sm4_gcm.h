#ifndef SM4_GCM_H
#define SM4_GCM_H

#include <stddef.h>
#include <stdint.h>

// GCM加密
int sm4_gcm_encrypt(const uint8_t *key, const uint8_t *iv, size_t iv_len,
                   const uint8_t *aad, size_t aad_len,
                   const uint8_t *plaintext, size_t pt_len,
                   uint8_t *ciphertext, uint8_t *tag, size_t tag_len);

// GCM解密
int sm4_gcm_decrypt(const uint8_t *key, const uint8_t *iv, size_t iv_len,
                   const uint8_t *aad, size_t aad_len,
                   const uint8_t *ciphertext, size_t ct_len,
                   const uint8_t *tag, size_t tag_len,
                   uint8_t *plaintext);

// GHASH函数（用于高级优化）
void ghash(const uint8_t *h, const uint8_t *aad, size_t aad_len,
          const uint8_t *ciphertext, size_t ct_len,
          uint8_t *tag);

// 常量定义
#define SM4_GCM_IV_MIN_SIZE 8
#define SM4_GCM_IV_MAX_SIZE 1024
#define SM4_GCM_TAG_MIN_SIZE 4
#define SM4_GCM_TAG_MAX_SIZE 16

// 错误代码
#define SM4_GCM_SUCCESS 0
#define SM4_GCM_AUTH_FAILED -1
#define SM4_GCM_INVALID_IV_LEN -2
#define SM4_GCM_INVALID_TAG_LEN -3

#endif // SM4_GCM_H