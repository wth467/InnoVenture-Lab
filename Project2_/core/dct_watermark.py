import cv2
import numpy as np
from .recovery import estimate_rotation

class DCTWatermark:
    def __init__(self, password=0, block_size=8, alpha=0.2):
        """
        基于DCT的数字水印系统
        :param password: 随机种子，用于确定嵌入位置
        :param block_size: DCT块大小
        :param alpha: 水印嵌入强度
        """
        self.password = password
        self.block_size = block_size
        self.alpha = alpha
        np.random.seed(password)
        
        # 定义中频系数位置 (避免直流分量和最低频)
        self.mid_freq_positions = [
            (4, 4), (4, 3), (3, 4), (5, 3), (3, 5)
        ]

    def _get_block_positions(self, total_blocks):
        """生成随机的块嵌入位置"""
        positions = np.random.permutation(total_blocks)
        return positions

    def embed(self, img, watermark):
        """
        嵌入水印到图像中
        :param img: 原始图像 (BGR格式)
        :param watermark: 二维水印图像 (0-255灰度图)
        :return: 含水印图像 (BGR格式)
        """
        # 转换到YUV空间，仅处理Y通道
        yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        y_channel = yuv[:, :, 0].astype(np.float32)
        
        # 将水印二值化并展平
        wm_binary = (watermark > 128).astype(np.uint8)
        wm_flat = wm_binary.flatten()
        wm_size = wm_flat.size
        
        # 图像分块
        h, w = y_channel.shape
        blocks_h = h // self.block_size
        blocks_w = w // self.block_size
        total_blocks = blocks_h * blocks_w
        
        if wm_size > total_blocks:
            raise ValueError("水印太大，无法嵌入")
        
        # 随机选择嵌入位置
        positions = self._get_block_positions(total_blocks)[:wm_size]
        
        # 在每个块中嵌入水印
        block_index = 0
        for pos in positions:
            i = (pos // blocks_w) * self.block_size
            j = (pos % blocks_w) * self.block_size
            block = y_channel[i:i+self.block_size, j:j+self.block_size]
            
            # DCT变换
            dct_block = cv2.dct(block)
            
            # 选择嵌入位置
            u, v = self.mid_freq_positions[block_index % len(self.mid_freq_positions)]
            
            # 嵌入水印
            if wm_flat[block_index] == 1:
                dct_block[u, v] = dct_block[u, v] * (1 + self.alpha)
            else:
                dct_block[u, v] = dct_block[u, v] * (1 - self.alpha)
            
            # 逆DCT
            y_channel[i:i+self.block_size, j:j+self.block_size] = cv2.idct(dct_block)
            block_index += 1
        
        # 合并通道
        yuv[:, :, 0] = np.clip(y_channel, 0, 255).astype(np.uint8)
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    def extract(self, img, wm_shape, estimate_attack=False):
        """
        从图像中提取水印
        :param img: 可能被攻击的含水印图像
        :param wm_shape: 水印原始形状 (h, w)
        :param estimate_attack: 是否估计旋转攻击
        :return: 提取的水印图像
        """
        # 估计并纠正旋转攻击
        if estimate_attack:
            img, angle = estimate_rotation(img)
        
        yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        y_channel = yuv[:, :, 0].astype(np.float32)
        
        # 图像分块
        h, w = y_channel.shape
        blocks_h = h // self.block_size
        blocks_w = w // self.block_size
        total_blocks = blocks_h * blocks_w
        
        # 获取相同嵌入位置
        positions = self._get_block_positions(total_blocks)[:wm_shape[0]*wm_shape[1]]
        
        # 提取水印位
        wm_bits = []
        block_index = 0
        for pos in positions:
            i = (pos // blocks_w) * self.block_size
            j = (pos % blocks_w) * self.block_size
            block = y_channel[i:i+self.block_size, j:j+self.block_size]
            
            # DCT变换
            dct_block = cv2.dct(block)
            
            # 选择嵌入位置
            u, v = self.mid_freq_positions[block_index % len(self.mid_freq_positions)]
            
            # 提取水印位
            avg_neighbor = np.mean([
                dct_block[u-1, v], dct_block[u+1, v],
                dct_block[u, v-1], dct_block[u, v+1]
            ])
            
            # 计算相对差异
            diff = dct_block[u, v] - avg_neighbor
            threshold = self.alpha * np.abs(avg_neighbor)
            
            if diff > threshold:
                wm_bits.append(255)  # 白色代表1
            elif diff < -threshold:
                wm_bits.append(0)    # 黑色代表0
            else:
                # 不确定的区域，使用邻域平均值
                wm_bits.append(128)
            
            block_index += 1
        
        # 重塑为水印图像
        wm_extracted = np.array(wm_bits).reshape(wm_shape).astype(np.uint8)
        return wm_extracted