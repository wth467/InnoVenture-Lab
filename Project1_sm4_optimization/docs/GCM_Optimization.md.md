# SM4-GCM优化原理

## 1. GCM模式结构
$$\begin{align*}
C_i &= E_k(CTR + i) \oplus P_i \\
Tag &= GHASH(H, AAD, C) \oplus E_k(J_0)
\end{align*}$$

## 2. GHASH优化
使用Karatsuba算法加速$GF(2^{128})$乘法：
$$a \times b = (a_H \cdot b_H) \cdot x^{128} + [(a_H + a_L)(b_H + b_L) + a_H b_H + a_L b_L] \cdot x^{64} + a_L b_L$$

## 3. CLMUL指令加速
Intel PCLMULQDQ指令单周期完成64×64位多项式乘法：
```nasm
vpclmulqdq zmm0, zmm1, zmm2, 0x00  ; 计算低64位乘积
vpclmulqdq zmm3, zmm1, zmm2, 0x11  ; 计算高64位乘积
```
## 4. 并行处理

使用AVX-512同时处理4个GHASH块HASH块：

```c
__m512i ghash_4blocks(__m512i h, __m512i y, const uint8_t* data) {
    __m512i blocks = _mm512_loadu_si512(data);
    y = _mm512_xor_si512(y, blocks);
    return gf512_mult(y, h);
}
```
