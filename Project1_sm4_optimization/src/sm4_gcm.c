#include "sm4.h"
#include "sm4_gcm.h"
#include "simd_utils.h"
#include <string.h>
#include <stdlib.h>

// 将64位整数转换为大端字节序
static void u64_to_be(uint64_t val, uint8_t *buf) {
    buf[0] = (uint8_t)(val >> 56);
    buf[1] = (uint8_t)(val >> 48);
    buf[2] = (uint8_t)(val >> 40);
    buf[3] = (uint8_t)(val >> 32);
    buf[4] = (uint8_t)(val >> 24);
    buf[5] = (uint8_t)(val >> 16);
    buf[6] = (uint8_t)(val >> 8);
    buf[7] = (uint8_t)val;
}

// 完整的IV处理函数（用于加密和解密）
static void process_iv(const uint8_t *key, const uint8_t *iv, size_t iv_len, uint8_t *J0) {
    if (iv_len == 12) {
        memcpy(J0, iv, 12);
        J0[15] = 0x01;
    } else {
        memset(J0, 0, 16);
        uint8_t H[16] = {0};
        sm4_encrypt(key, H, H);
        
        size_t iv_blocks = (iv_len + 15) / 16;
        const uint8_t *iv_ptr = iv;
        
        // 预加载 H 到向量寄存器
        __m128i H_vec = _mm_loadu_si128((const __m128i*)H);
        
        for (size_t i = 0; i < iv_blocks; i++) {
            uint8_t block[16] = {0};
            size_t block_len = (i == iv_blocks - 1) ? iv_len % 16 : 16;
            if (block_len == 0) block_len = 16;
            
            memcpy(block, iv_ptr, block_len);
            for (size_t j = 0; j < 16; j++) {
                J0[j] ^= block[j];
            }
            
            __m128i j0_block = _mm_loadu_si128((const __m128i*)J0);
            j0_block = gf128_mult(j0_block, H_vec);
            _mm_storeu_si128((__m128i*)J0, j0_block);
            
            iv_ptr += block_len;
        }
        
        // 添加长度块
        uint8_t len_block[16] = {0};
        u64_to_be((uint64_t)iv_len * 8, len_block + 8);
        
        __m128i j0_vec = _mm_loadu_si128((const __m128i*)J0);
        __m128i len_vec = _mm_loadu_si128((const __m128i*)len_block);
        j0_vec = _mm_xor_si128(j0_vec, len_vec);
        
        j0_vec = gf128_mult(j0_vec, H_vec);
        _mm_storeu_si128((__m128i*)J0, j0_vec);
    }
}

// GCM模式加密
int sm4_gcm_encrypt(const uint8_t *key, const uint8_t *iv, size_t iv_len,
                   const uint8_t *aad, size_t aad_len,
                   const uint8_t *plaintext, size_t pt_len,
                   uint8_t *ciphertext, uint8_t *tag, size_t tag_len) {
    // 生成初始计数器J0
    uint8_t J0[16] = {0};
    process_iv(key, iv, iv_len, J0);
    
    // 计算GHASH密钥H
    uint8_t H[16] = {0};
    sm4_encrypt(key, H, H);
    
    // CTR模式加密
    uint32_t ctr[4];
    memcpy(ctr, J0, 16);
    
    // 处理完整块
    size_t full_blocks = pt_len / 16;
    for (size_t i = 0; i < full_blocks; i++) {
        // 更新计数器
        for (int j = 15; j >= 12; j--) {
            if (++((uint8_t*)ctr)[j] != 0) break;
        }
        
        // 加密计数器
        uint8_t keystream[16];
        sm4_encrypt(key, (uint8_t*)ctr, keystream);
        
        // 加密数据块
        for (int j = 0; j < 16; j++) {
            ciphertext[i*16+j] = plaintext[i*16+j] ^ keystream[j];
        }
    }
    
    // 处理最后的不完整块
    size_t remaining = pt_len % 16;
    if (remaining > 0) {
        // 更新计数器
        for (int j = 15; j >= 12; j--) {
            if (++((uint8_t*)ctr)[j] != 0) break;
        }
        
        // 加密计数器
        uint8_t keystream[16];
        sm4_encrypt(key, (uint8_t*)ctr, keystream);
        
        // 加密剩余数据
        for (size_t j = 0; j < remaining; j++) {
            ciphertext[full_blocks*16+j] = plaintext[full_blocks*16+j] ^ keystream[j];
        }
    }
    
    // 计算GHASH
    uint8_t ghash_val[16] = {0};
    __m128i g = _mm_setzero_si128();
    __m128i h = _mm_loadu_si128((const __m128i*)H);
    
    // 处理附加认证数据(AAD)
    const uint8_t *aad_ptr = aad;
    size_t aad_remaining = aad_len;
    while (aad_remaining >= 16) {
        __m128i block = _mm_loadu_si128((const __m128i*)aad_ptr);
        g = _mm_xor_si128(g, block);
        g = gf128_mult(g, h);
        
        aad_ptr += 16;
        aad_remaining -= 16;
    }
    
    // 处理剩余的AAD
    if (aad_remaining > 0) {
        uint8_t aad_block[16] = {0};
        memcpy(aad_block, aad_ptr, aad_remaining);
        __m128i block = _mm_loadu_si128((const __m128i*)aad_block);
        g = _mm_xor_si128(g, block);
        g = gf128_mult(g, h);
    }
    
    // 处理密文
    const uint8_t *cipher_ptr = ciphertext;
    size_t cipher_remaining = pt_len;
    while (cipher_remaining >= 16) {
        __m128i block = _mm_loadu_si128((const __m128i*)cipher_ptr);
        g = _mm_xor_si128(g, block);
        g = gf128_mult(g, h);
        
        cipher_ptr += 16;
        cipher_remaining -= 16;
    }
    
    // 处理剩余的密文
    if (cipher_remaining > 0) {
        uint8_t cipher_block[16] = {0};
        memcpy(cipher_block, cipher_ptr, cipher_remaining);
        __m128i block = _mm_loadu_si128((const __m128i*)cipher_block);
        g = _mm_xor_si128(g, block);
        g = gf128_mult(g, h);
    }
    
    // 添加长度块 (AAD长度 + 密文长度)
    uint8_t len_block[16] = {0};
    u64_to_be((uint64_t)aad_len * 8, len_block);
    u64_to_be((uint64_t)pt_len * 8, len_block + 8);
    
    __m128i len_vec = _mm_loadu_si128((const __m128i*)len_block);
    g = _mm_xor_si128(g, len_vec);
    g = gf128_mult(g, h);
    
    _mm_storeu_si128((__m128i*)ghash_val, g);
    
    // 计算最终认证标签
    uint8_t encrypted_j0[16];
    sm4_encrypt(key, J0, encrypted_j0);
    
    for (size_t i = 0; i < tag_len && i < 16; i++) {
        if (i < 16) {
            tag[i] = ghash_val[i] ^ encrypted_j0[i];
        } else {
            tag[i] = encrypted_j0[i]; // 如果tag_len > 16，填充剩余部分
        }
    }
    
    return 0;
}

// GCM模式解密
int sm4_gcm_decrypt(const uint8_t *key, const uint8_t *iv, size_t iv_len,
                   const uint8_t *aad, size_t aad_len,
                   const uint8_t *ciphertext, size_t ct_len,
                   const uint8_t *tag, size_t tag_len,
                   uint8_t *plaintext) {
    // 生成初始计数器J0
    uint8_t J0[16] = {0};
    process_iv(key, iv, iv_len, J0);
    
    // 计算GHASH密钥H
    uint8_t H[16] = {0};
    sm4_encrypt(key, H, H);
    
    // 计算GHASH（用于验证标签）
    uint8_t ghash_val[16] = {0};
    __m128i g = _mm_setzero_si128();
    __m128i h = _mm_loadu_si128((const __m128i*)H);
    
    // 处理附加认证数据(AAD)
    const uint8_t *aad_ptr = aad;
    size_t aad_remaining = aad_len;
    while (aad_remaining >= 16) {
        __m128i block = _mm_loadu_si128((const __m128i*)aad_ptr);
        g = _mm_xor_si128(g, block);
        g = gf128_mult(g, h);
        
        aad_ptr += 16;
        aad_remaining -= 16;
    }
    
    // 处理剩余的AAD
    if (aad_remaining > 0) {
        uint8_t aad_block[16] = {0};
        memcpy(aad_block, aad_ptr, aad_remaining);
        __m128i block = _mm_loadu_si128((const __m128i*)aad_block);
        g = _mm_xor_si128(g, block);
        g = gf128_mult(g, h);
    }
    
    // 处理密文
    const uint8_t *cipher_ptr = ciphertext;
    size_t cipher_remaining = ct_len;
    while (cipher_remaining >= 16) {
        __m128i block = _mm_loadu_si128((const __m128i*)cipher_ptr);
        g = _mm_xor_si128(g, block);
        g = gf128_mult(g, h);
        
        cipher_ptr += 16;
        cipher_remaining -= 16;
    }
    
    // 处理剩余的密文
    if (cipher_remaining > 0) {
        uint8_t cipher_block[16] = {0};
        memcpy(cipher_block, cipher_ptr, cipher_remaining);
        __m128i block = _mm_loadu_si128((const __m128i*)cipher_block);
        g = _mm_xor_si128(g, block);
        g = gf128_mult(g, h);
    }
    
    // 添加长度块 (AAD长度 + 密文长度)
    uint8_t len_block[16] = {0};
    u64_to_be((uint64_t)aad_len * 8, len_block);
    u64_to_be((uint64_t)ct_len * 8, len_block + 8);
    
    __m128i len_vec = _mm_loadu_si128((const __m128i*)len_block);
    g = _mm_xor_si128(g, len_vec);
    g = gf128_mult(g, h);
    
    _mm_storeu_si128((__m128i*)ghash_val, g);
    
    // 计算最终认证标签
    uint8_t encrypted_j0[16];
    sm4_encrypt(key, J0, encrypted_j0);
    
    uint8_t computed_tag[16];
    for (int i = 0; i < 16; i++) {
        computed_tag[i] = ghash_val[i] ^ encrypted_j0[i];
    }
    
    // 验证标签
    int tag_mismatch = 0;
    int min_len = tag_len < 16 ? tag_len : 16;
    for (size_t i = 0; i < min_len; i++) {
        if (i < 16) {
            tag_mismatch |= (computed_tag[i] != tag[i]);
        } else {
            tag_mismatch |= (encrypted_j0[i] != tag[i]);
        }
    }
    
    if (tag_mismatch) {
        // 标签不匹配，清除输出
        memset(plaintext, 0, ct_len);
        return -1; // 认证失败
    }
    
    // CTR模式解密
    uint32_t ctr[4];
    memcpy(ctr, J0, 16);
    
    // 处理完整块
    size_t full_blocks = ct_len / 16;
    for (size_t i = 0; i < full_blocks; i++) {
        // 更新计数器
        for (int j = 15; j >= 12; j--) {
            if (++((uint8_t*)ctr)[j] != 0) break;
        }
        
        // 加密计数器
        uint8_t keystream[16];
        sm4_encrypt(key, (uint8_t*)ctr, keystream);
        
        // 解密密文块
        for (int j = 0; j < 16; j++) {
            plaintext[i*16+j] = ciphertext[i*16+j] ^ keystream[j];
        }
    }
    
    // 处理最后的不完整块
    size_t remaining = ct_len % 16;
    if (remaining > 0) {
        // 更新计数器
        for (int j = 15; j >= 12; j--) {
            if (++((uint8_t*)ctr)[j] != 0) break;
        }
        
        // 加密计数器
        uint8_t keystream[16];
        sm4_encrypt(key, (uint8_t*)ctr, keystream);
        
        // 解密剩余数据
        for (size_t j = 0; j < remaining; j++) {
            plaintext[full_blocks*16+j] = ciphertext[full_blocks*16+j] ^ keystream[j];
        }
    }
    
    return 0;
}