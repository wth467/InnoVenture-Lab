# SM2签名算法误用场景分析

## 1. 同一用户重用随机数k

### 1.1 攻击原理
当用户对两条不同消息 $M_1, M_2$ 使用相同的 $k$ 进行签名时：

签名1:
$$
\begin{cases}
r_1 = (e_1 + x_1) \mod n \\
s_1 = (1 + d_A)^{-1}(k - r_1 d_A) \mod n
\end{cases}
$$

签名2:
$$
\begin{cases}
r_2 = (e_2 + x_1) \mod n \\
s_2 = (1 + d_A)^{-1}(k - r_2 d_A) \mod n
\end{cases}
$$

从签名方程可得：
$$
s_1(1 + d_A) = k - r_1 d_A \\
s_2(1 + d_A) = k - r_2 d_A
$$

两式相减：
$$
(s_1 - s_2)(1 + d_A) = (r_2 - r_1)d_A
$$

解得私钥：
$$
d_A = \frac{s_2 - s_1}{s_1 - s_2 + r_1 - r_2} \mod n
$$

### 1.2 POC验证代码
```python
def same_user_reuse_k():
    dA, PA = sm2_keygen()
    k = secrets.randbelow(N - 1) + 1
    
    # 对两条消息使用相同k签名
    r1, s1 = sm2_sign(dA, b"Message1", "user", k)
    r2, s2 = sm2_sign(dA, b"Message2", "user", k)
    
    # 计算私钥
    num = (s2 - s1) % N
    den = (s1 - s2 + r1 - r2) % N
    dA_recovered = (num * mod_inv(den, N)) % N
    
    assert dA_recovered == dA
    print("私钥恢复成功:", hex(dA_recovered))
```

## 2.不同用户重用随机数k
### 2.1 攻击原理
当用户A和用户B使用相同的 $k$ 签名时：
用户A的签名:
$$
s_1 = (1 + d_A)^{-1}(k - r_1 d_A) \mod n
$$
用户B的签名:
$$
s_2 = (1 + d_B)^{-1}(k - r_2 d_B) \mod n
$$
对于用户A，可解出 $k$:
$$
k = s_1(1 + d_A) + r_1 d_A \mod n
$$
代入用户B的方程：
$$
s_2(1 + d_B) = k - r_2 d_B
$$
解得用户B的私钥：
$$
d_B = \frac{k - s_2}{s_2 + r_2} \mod n
$$

## 3. 相同d和k用于SM2和ECDSA
### 3.1 攻击原理
当用户对两条消息分别使用SM2和ECDSA算法，但使用相同的 $d$ 和 $k$：
ECDSA签名:
$$
\begin{cases}
r_1 = x(kG) \mod n \
s_1 = k^{-1}(e_1 + r_1 d) \mod n
\end{cases}
$$
SM2签名:
$$
\begin{cases}
r_2 = (e_2 + x(kG)) \mod n \
s_2 = (1 + d)^{-1}(k - r_2 d) \mod n
\end{cases}
$$
从ECDSA方程可得：
$$
k = s_1^{-1}(e_1 + r_1 d) \mod n
$$
代入SM2方程：
$$
s_2(1 + d) = k - r_2 d = s_1^{-1}(e_1 + r_1 d) - r_2 d
$$
整理得：
$$
d = \frac{s_1 s_2 - e_1}{r_1 - s_1(s_2 + r_2)} \mod n
$$

## 4. 伪造中本聪签名
### 4.1 攻击原理
比特币使用ECDSA签名，若签名重用 $k$：
$$
\begin{cases}
s_1 = k^{-1}(e_1 + r d) \mod n \
s_2 = k^{-1}(e_2 + r d) \mod n
\end{cases}
$$
联立方程消去 $d$：
$$
k(s_1 - s_2) \equiv e_1 - e_2 \mod n
$$
解得 $k$：
$$
k = (e_1 - e_2)(s_1 - s_2)^{-1} \mod n
$$
代入第一个方程得私钥：
$$
d = r^{-1}(s_1 k - e_1) \mod n
$$
