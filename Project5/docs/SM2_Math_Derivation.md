# SM2椭圆曲线密码算法数学推导

## 1. 有限域椭圆曲线基础

### 1.1 有限域定义
设有限域 $\mathbb{F}_q$，其中 $q$ 为素数幂：
$$
q = p^m \quad (p \text{ 为素数}, m \geq 1)
$$
- 当 $m=1$ 时为素数域
- 当 $m\geq2$ 时为扩展域
- $m=2$ 时为二元域

### 1.2 椭圆曲线方程
定义在 $\mathbb{F}_q$ 上的椭圆曲线方程：
$$
y^2 = x^3 + ax + b \mod q
$$
其中 $a, b \in \mathbb{F}_q$ 且满足 $4a^3 + 27b^2 \neq 0 \mod q$。

### 1.3 点加法公式
设 $P = (x_1, y_1)$, $Q = (x_2, y_2)$，则 $R = P + Q = (x_3, y_3)$ 计算如下：

**当 $P \neq Q$ 时（点加）:**
$$
\lambda = \frac{y_2 - y_1}{x_2 - x_1} \mod q
$$
$$
x_3 = \lambda^2 - x_1 - x_2 \mod q
$$
$$
y_3 = \lambda(x_1 - x_3) - y_1 \mod q
$$

**当 $P = Q$ 时（倍点）:**
$$
\lambda = \frac{3x_1^2 + a}{2y_1} \mod q
$$
$$
x_3 = \lambda^2 - 2x_1 \mod q
$$
$$
y_3 = \lambda(x_1 - x_3) - y_1 \mod q
$$

### 1.4 标量乘法
使用 double-and-add 算法计算 $Q = kP$：
```python
def scalar_mult(k: int, P: Point) -> Point:
    Q = INFINITY  # 无穷远点
    while k > 0:
        if k & 1:   # 如果最低位为1
            Q = point_add(Q, P)
        P = point_double(P)
        k >>= 1     # 右移一位
    return Q
```
## 2. SM2数字签名算法
### 2.1 参数定义
SM2使用特定参数：
素数 $q$ = 8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3
系数 $a$ = 787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498
系数 $b$ = 63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A
基点 $G$ = (421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D, 
   0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2)
阶 $n$ = 8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
余因子 $h = 1$
### 2.2 签名生成
计算 $Z_A = SM3(ENTL_A \parallel ID_A \parallel a \parallel b \parallel x_G \parallel y_G \parallel x_A \parallel y_A)$
构造 $M = Z_A \parallel \text{原始消息}$
计算 $e = H_v(M)$
生成随机数 $k \in [1, n-1]$
计算 $(x_1, y_1) = kG$
计算 $r = (e + x_1) \mod n$
若 $r=0$ 或 $r+k=n$ 则返回步骤4
计算 $s = (1 + d_A)^{-1} \cdot (k - r \cdot d_A) \mod n$
若 $s=0$ 则返回步骤4
输出签名 $(r, s)$
### 2.3 签名验证
检查 $r, s \in [1, n-1]$
计算 $Z_A$（同签名步骤1）
构造 $M' = Z_A \parallel \text{原始消息}$
计算 $e' = H_v(M')$
计算 $t = (r + s) \mod n$
计算 $(x_1', y_1') = sG + tP_A$
计算 $R = (e' + x_1') \mod n$
验证 $R = r$
## 3. 正确性证明
验证等式推导：
$$
\begin{align*}
sG + tP_A &= sG + (r + s)P_A \
&= sG + (r + s)d_AG \
&= [s + (r + s)d_A]G \
&= [s(1 + d_A) + r d_A]G
\end{align*}
$$
由签名公式：
$$
s = (1 + d_A)^{-1}(k - r d_A) \mod n
$$
可得：
$$
s(1 + d_A) = k - r d_A \mod n
$$
代入前式：
$$
[s(1 + d_A) + r d_A]G = (k - r d_A + r d_A)G = kG
$$
因此 $x_1' = x_1$，故 $R = e' + x_1' = e + x_1 = r$，验证通过。
## 4. SM2加密算法
### 4.1 密钥派生函数(KDF)
```python
def kdf(z: bytes, klen: int) -> bytes:
    v = 32  # SM3输出长度(字节)
    ct = 0x00000001
    ha = b''
    
    for i in range(ceil(klen / v)):
        data = z + ct.to_bytes(4, 'big')
        ha_i = sm3_hash(data)
        ha += ha_i
        ct += 1
    
    return ha[:klen]
```
### 4.2 加密流程
生成随机数 $k \in [1, n-1]$
计算 $C_1 = kG = (x_1, y_1)$
计算 $S = hP_B$，若 $S=\mathcal{O}$ 报错（无效公钥）
计算 $(x_2, y_2) = kP_B$
计算 $t = KDF(x_2 \parallel y_2, \text{明文长度})$
若 $t$ 全为0则返回步骤1
计算 $C_2 = M \oplus t$
计算 $C_3 = Hash(x_2 \parallel M \parallel y_2)$
输出密文 $C = C_1 \parallel C_2 \parallel C_3$
### 4.3 解密流程
验证 $C_1$ 在曲线上
计算 $S = hC_1$，若 $S=\mathcal{O}$ 报错
计算 $(x_2, y_2) = d_BC_1$
计算 $t = KDF(x_2 \parallel y_2, \text{密文长度})$
若 $t$ 全为0则报错
计算 $M' = C_2 \oplus t$
计算 $u = Hash(x_2 \parallel M' \parallel y_2)$，验证 $u = C_3$
输出明文 $M'$