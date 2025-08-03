# SM4-GCM模式优化实现

## 1. GCM模式原理
GCM（Galois/Counter Mode）是一种认证加密模式，结合了CTR加密和GMAC认证。

### 1.1 数学基础
GCM基于GF(2¹²⁸)伽罗瓦域运算，使用不可约多项式：
$$p(x) = x^{128} + x^7 + x^2 + x + 1$$

### 1.2 加密认证流程
$$
\begin{align*}
&\text{输入: } K, IV, P, AAD \\
&\text{输出: } C, Tag \\
\\
&1.\ H = E_K(0^{128}) \\
&2.\ J_0 = \begin{cases} 
      IV || 0^{31}1 & \text{if } len(IV) = 96 \\
      GHASH_H(IV) & \text{otherwise}
   \end{cases} \\
&3.\ C = CTR\_MODE(K, J_0 + 1, P) \\
&4.\ u = 128 \lceil len(C)/128 \rceil - len(C) \\
&5.\ v = 128 \lceil len(AAD)/128 \rceil - len(AAD) \\
&6.\ S = GHASH_H(AAD || 0^v || C || 0^u || len(AAD) || len(C)) \\
&7.\ T = MSB_t(E_K(J_0) \oplus S)
\end{align*}
$$

## 2. GHASH优化技术

### 2.1 GHASH算法
$$
\text{GHASH}(H, A, C) = \left( \sum_{i=1}^m X_i \cdot H^{m+1-i} \right) \oplus E_k(J_0)
$$
### 2.2 AES-NI辅助GHASH

通过域同构复用AES-NI指令：

$$
GHASH_{SM4} = \phi^{-1} ( GHASH_{AES} ( \phi(H), \phi(A), \phi(C) ) )
$$

### 2.3 Karatsuba算法优化
使用Karatsuba算法加速GF(2¹²⁸)乘法：
$$a \times b = (a_H \cdot b_H) \cdot x^{128} + [(a_H + a_L)(b_H + b_L) + a_H b_H + a_L b_L] \cdot x^{64} + a_L b_L$$

在伽罗瓦域中：
$$a \times b \mod p(x) = [(a_H + a_L)(b_H + b_L) + a_L b_L] \cdot x^{64} + a_L b_L + a_H b_H \cdot (x^7 + x^2 + x + 1)$$

### 2.4 PCLMULQDQ指令优化
Intel PCLMULQDQ指令实现64位多项式乘法：
```c
__m128i gf128_mult(__m128i a, __m128i b) {
    __m128i t1 = _mm_clmulepi64_si128(a, b, 0x00); // a_low * b_low
    __m128i t2 = _mm_clmulepi64_si128(a, b, 0x11); // a_high * b_high
    __m128i t3 = _mm_clmulepi64_si128(a, b, 0x01); // a_low * b_high
    __m128i t4 = _mm_clmulepi64_si128(a, b, 0x10); // a_high * b_low
    
    t3 = _mm_xor_si128(t3, t4);
    t4 = _mm_slli_si128(t3, 8);
    t3 = _mm_srli_si128(t3, 8);
    
    t1 = _mm_xor_si128(t1, t4);
    t2 = _mm_xor_si128(t2, t3);
    
    // 模约简
    const __m128i mod = _mm_set_epi32(0, 0, 0, 0x87);
    __m128i t5 = _mm_clmulepi64_si128(t2, mod, 0x00);
    __m128i t6 = _mm_clmulepi64_si128(t2, mod, 0x10);
    
    return _mm_xor_si128(t1, _mm_xor_si128(t5, t6));
}
```



## 3. SM4-GCM完整实现

### 3.1 加密流程

```c
int sm4_gcm_encrypt(const uint8_t *key, const uint8_t *iv, size_t iv_len,
                   const uint8_t *aad, size_t aad_len,
                   const uint8_t *plaintext, size_t pt_len,
                   uint8_t *ciphertext, uint8_t *tag, size_t tag_len) {
    // 1. 生成J0
    uint8_t J0[16] = {0};
    process_iv(key, iv, iv_len, J0);
    
    // 2. 计算H
    uint8_t H[16] = {0};
    sm4_encrypt(key, H, H);
    
    // 3. CTR模式加密
    uint32_t ctr[4];
    memcpy(ctr, J0, 16);
    for (size_t i = 0; i < pt_len; i += 16) {
        // 更新计数器
        increment_ctr(ctr);
        // 加密计数器
        sm4_encrypt(key, (uint8_t*)ctr, keystream);
        // 异或加密
        for (int j = 0; j < min(16, pt_len-i); j++) {
            ciphertext[i+j] = plaintext[i+j] ^ keystream[j];
        }
    }
    
    // 4. 计算GHASH
    uint8_t ghash_val[16];
    compute_ghash(H, aad, aad_len, ciphertext, pt_len, ghash_val);
    
    // 5. 生成标签
    sm4_encrypt(key, J0, J0);
    for (size_t i = 0; i < tag_len; i++) {
        tag[i] = ghash_val[i] ^ J0[i];
    }
    
    return 0;
}
```
