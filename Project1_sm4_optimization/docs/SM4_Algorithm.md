# SM4算法数学原理

## 1. 算法概述
- 中国商用密码标准 (GB/T 32907-2016)
- 128位分组长度/密钥长度
- 32轮Feistel结构

## 2. 轮函数
$$F(X_0, X_1, X_2, X_3, rk) = X_0 \oplus T(X_1 \oplus X_2 \oplus X_3 \oplus rk)$$

其中：
- $T(\cdot) = L(\tau(\cdot))$
- $\tau$ 为S盒变换（8位输入，8位输出）
- $L$ 为线性变换：
  $$L(B) = B \oplus (B \lll 2) \oplus (B \lll 10) \oplus (B \lll 18) \oplus (B \lll 24)$$

## 3. S盒构造
基于复合域$GF(2^8)/GF(2^4)/GF(2^2)$实现：
```python
def sbox(x):
    # 仿射变换
    x = affine_transform(x)
    # 在GF(2^8)上求逆
    if x != 0:
        x = gf256_inv(x)
    return x
```
## 4. 密钥扩展

$$rk_i = k_{i+4} = k_i \oplus T'(k_{i+1} \oplus k_{i+2} \oplus k_{i+3} \oplus CK_i)$$
其中$T'$变换与加密中的$T$类似但线性部分不同。