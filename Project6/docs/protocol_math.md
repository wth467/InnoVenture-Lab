# Google Password Checkup 协议数学推导

## 1. 协议目标
- 客户端检查密码是否泄露，无需透露密码
- 服务器不学习客户端查询内容
- 防止暴力破解攻击

## 2. 密码学基础
### 双线性映射
设：
- \(\mathbb{G}_1, \mathbb{G}_2, \mathbb{G}_T\)：素数阶 \(q\) 的循环群
- \(P \in \mathbb{G}_1, Q \in \mathbb{G}_2\)：生成元
- \(e: \mathbb{G}_1 \times \mathbb{G}_2 \to \mathbb{G}_T\)：双线性映射，满足：
  \[
  e(aP, bQ) = e(P, Q)^{ab} \quad \forall a,b \in \mathbb{Z}_q
  \]

### 哈希函数
- \(H_1: \{0,1\}^* \to \mathbb{G}_1\)：密码到群元素的哈希

## 3. 协议流程

### 服务器初始化
1. 生成私钥 \(s \xleftarrow{\$} \mathbb{Z}_q^*\)
2. 对每个密码 \(x \in D\) 计算：
   \[
   t_x = e(H_1(x), sP) \in \mathbb{G}_T
   \]
3. 构建阈值布隆过滤器 \(BF\)：
   \[
   \forall t_x \in S, \forall i \in [k]: \quad \text{BF}[H_i(t_x) \mod m] += 1
   \]

### 客户端查询（密码 \(p\)）
1. 生成随机数 \(r \xleftarrow{\$} \mathbb{Z}_q^*\)
2. 计算：
   \[
   U = r \cdot H_1(p) \in \mathbb{G}_1
   \]
3. 发送 \(U\) 到服务器

### 服务器响应
1. 计算：
   \[
   V = s \cdot U \in \mathbb{G}_1
   \]
2. 返回 \((V, \text{BF})\)

### 客户端验证
1. 计算：
   \[
   T = e(V, P) = e(s \cdot r \cdot H_1(p), P) = e(H_1(p), P)^{sr}
   \]
2. 检查布隆过滤器：
   \[
   \forall i \in [k]: \quad \text{BF}[H_i(T) \mod m] > 0
   \]
3. 若所有位置非零，则密码可能泄露

## 4. 正确性证明
\[
T = e(V, P) = e(s \cdot U, P) = e(s \cdot r \cdot H_1(p), P)
\]
\[
= e(H_1(p), P)^{s \cdot r} = e(H_1(p), sP)^r = t_p^r
\]

当密码 \(p\) 在数据库中时，\(t_p \in S\)，对应的布隆过滤器位置被设置。

## 5. 安全特性
1. **隐私性**：服务器仅收到 \(U = r \cdot H_1(p)\)，无法恢复 \(p\)
2. **安全性**：客户端仅学习布尔结果，不知完整数据库
3. **抗暴力破解**：每次查询使用随机 \(r\)，阻止离线猜测