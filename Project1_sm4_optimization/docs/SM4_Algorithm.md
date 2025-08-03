# SM4分组密码算法

## 1. 算法概述
- **发布时间**：2006年（最初用于WAPI无线安全协议）
- **国家标准**：GMT 002-2012, GBT 32907-2016
- **结构类型**：不平衡Feistel网络
- **分组长度**：128位
- **密钥长度**：128位
- **轮数**：32轮

## 2. 轮函数数学表示
### 加密过程
设输入分组为 
$$(X_0, X_1, X_2, X_3) \in (F_2^{32})^4$$
，轮密钥 
$$rk_i \in F_2^{32}$$.  

对于 i = 0 到 31：
$$X_{i+4} = F(X_i, X_{i+1}, X_{i+2}, X_{i+3}, rk_i) = X_i \oplus T(X_{i+1} \oplus X_{i+2} \oplus X_{i+3} \oplus rk_i)$$

最终密文：
$$(X_{35}, X_{34}, X_{33}, X_{32})$$

### 核心变换 $T(\cdot)$
$$T(\cdot) = L(\tau(\cdot))$$

- **非线性变换 $\tau$**：
  $$\tau(A) = (Sbox(a_0), Sbox(a_1), Sbox(a_2), Sbox(a_3)), \quad A \in \mathbb{F}_2^{32}$$
  
- **线性变换 $L$**：
  $$L(B) = B \oplus (B \lll 2) \oplus (B \lll 10) \oplus (B \lll 18) \oplus (B \lll 24)$$

## 3. S盒代数结构
### 数学表达式
$$Sbox_{SM4}(x) = \left[ (x \cdot A)^{-1} \cdot A \right] \oplus \left[ x \cdot L \right]$$

- **有限域**：
$$GF(2^8)$$
，不可约多项式
$$g(x) = x^8 + x^7 + x^6 + x^5 + x^4 + x^2 + 1$$


## 4. 密钥扩展算法
主密钥 $MK = (MK_0, MK_1, MK_2, MK_3)$：
$$K_i = MK_i \oplus FK_i$$
其中系统参数 $FK = (\mathtt{0xA3B1BAC6}, \mathtt{0x56AA3350}, \mathtt{0x677D9197}, \mathtt{0xB27022DC})$

轮密钥生成：
$$rk_i = K_{i+4} = K_i \oplus T'(K_{i+1} \oplus K_{i+2} \oplus K_{i+3} \oplus CK_i)$$
其中 $T'$ 使用修改的线性层：
$$L'(B) = B \oplus (B \lll 13) \oplus (B \lll 22)$$
$CK_i$ 为固定参数，通过 $(4i+j) \times 7 \mod 256$ 计算
## 5. 安全分析

### 差分/线性分析

- **最佳差分概率**：
$$2^{-6}$$
（优于AES的$2^{-6}$）
- **全轮安全余量**：
$$32 \times 2^{-6} = 2^{-192} < 2^{-128}$$
