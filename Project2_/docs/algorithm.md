# 基于DCT的数字水印算法

## 1. 算法原理
本系统采用**离散余弦变换(DCT)**在频域嵌入水印，核心思想是利用人类视觉系统(HVS)的特性：
- 人眼对高频变化不敏感
- 对中频区域的轻微修改不易察觉
- 对亮度变化比色度变化更敏感

### 水印嵌入过程
1. **预处理**：
   - 输入图像转换到YUV空间，仅处理Y（亮度）通道
   - 水印图像二值化（0/255）

2. **分块处理**：
   $$ \text{图像分块} \rightarrow 8\times8 \text{ 小块} $$

3. **DCT变换**：
   $$ F(u,v) = \frac{2}{N} c(u)c(v) \sum_{x=0}^{7}\sum_{y=0}^{7} f(x,y) \cos\left(\frac{(2x+1)u\pi}{16}\right) \cos\left(\frac{(2y+1)v\pi}{16}\right) $$
   $$ c(k) = \begin{cases} \frac{1}{\sqrt{2}} & k=0 \\ 1 & \text{其他} \end{cases} $$

4. **系数修改**：
   - 选择中频系数位置：`(3,4), (4,3), (4,4), (3,5), (5,3)`
   - 修改规则：
     $$ C_{\text{new}}(u,v) = \begin{cases} 
        C(u,v) \cdot (1 + \alpha) & \text{水印位}=1 \\
        C(u,v) \cdot (1 - \alpha) & \text{水印位}=0 
     \end{cases} $$

5. **逆DCT重建**：
   $$ f(x,y) = \frac{2}{N} \sum_{u=0}^{7}\sum_{v=0}^{7} c(u)c(v) F(u,v) \cos\left(\frac{(2x+1)u\pi}{16}\right) \cos\left(\frac{(2y+1)v\pi}{16}\right) $$

### 水印提取过程
1. **攻击估计**（可选）：
   - 使用霍夫变换检测直线角度
   - 旋转校正图像

2. **系数提取**：
   $$ \text{比特位} = \begin{cases} 
      1 & \text{if } C(u,v) > \text{邻居均值} \\
      0 & \text{otherwise}
   \end{cases} $$

3. **水印增强**：
   - 中值滤波去噪
   - 形态学操作（开运算+闭运算）

## 2. 鲁棒性设计
1. **抗几何攻击**：
   - 随机分布嵌入位置
   - 旋转攻击自动检测与校正
   
2. **抗信号处理**：
   - 中频区域嵌入抵抗JPEG压缩
   - 自适应强度调整抵抗对比度变化

3. **抗裁剪攻击**：
   - 水印信息重复嵌入
   - 冗余编码设计

## 3. 评估指标
1. **归一化相关系数(NC)**：
   $$ \text{NC} = \frac{\sum_i \sum_j W(i,j) W'(i,j)}{\sqrt{\sum_i \sum_j W(i,j)^2} \sqrt{\sum_i \sum_j W'(i,j)^2}} $$

2. **误码率(BER)**：
   $$ \text{BER} = \frac{\text{错误比特数}}{\text{总比特数}} \times 100\% $$

3. **视觉相似度**：
   - 结构相似性(SSIM)
   - 峰值信噪比(PSNR)