# SM4算法的SIMD优化技术

## 1. SIMD基础概念
SIMD（Single Instruction, Multiple Data）是一种并行计算技术，允许单条指令同时处理多个数据元素。现代CPU支持的SIMD指令集包括：
- SSE/AVX (Intel)
- NEON (ARM)
- AltiVec (PowerPC)

## 2. AES-NI加速原理
### AES专用指令
```c
// 单轮加密
__m128i _mm_aesenc_si128(__m128i state, __m128i rkey);
// 最终轮加密
__m128i _mm_aesenclast_si128(__m128i state, __m128i rkey);
```
### SM4的AES-NI加速

#### 域同构映射

将计算从\(GF_{SM4}(2^8)\)映射到\(GF_{AES}(2^8)\)：
\[
GF_{SM4}(2^8) \cong GF_{AES}(2^8)
\]
**映射矩阵**\(M\)满足：
\[
\mathbf{x}_{AES} = M \cdot \mathbf{x}_{SM4}
\]

## 3. T-Table优化技术

### SM4 T-Table构造

将\(T(\cdot) = L \circ \tau\)替换为4个预计算表：
\[
T_i[x] = L_i(Sbox(x)), \quad i \in \{0,1,2,3\}
\]
其中\(L_i\)是应用于SBox输出的线性变换部分。  
**表大小**：4 × 256 × 32位 = 4 KB

### SIMD并行处理

使用AVX2并行处理4个分组：

```c
__m256i t0 = _mm256_i32gather_epi32(T0, idx0, 4);
__m256i t1 = _mm256_i32gather_epi32(T1, idx1, 4);
__m256i result = _mm256_xor_si256(t0, t1);
```
