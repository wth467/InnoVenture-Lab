import cv2
import numpy as np
import random

class ImageAttacks:
    @staticmethod
    def random_flip(img):
        """随机翻转"""
        if random.random() > 0.5:
            return cv2.flip(img, 1)  # 水平翻转
        return cv2.flip(img, 0)      # 垂直翻转

    @staticmethod
    def shift(img, dx=10, dy=5):
        """平移攻击"""
        return np.roll(img, shift=(dy, dx), axis=(0, 1))

    @staticmethod
    def crop(img, ratio=0.1):
        """截取攻击"""
        h, w = img.shape[:2]
        crop_h = int(h * ratio)
        crop_w = int(w * ratio)
        
        # 随机选择截取位置
        start_y = random.randint(0, crop_h)
        start_x = random.randint(0, crop_w)
        
        # 创建新图像并填充黑色
        attacked = img.copy()
        attacked[start_y:start_y+crop_h, start_x:start_x+crop_w] = 0
        return attacked

    @staticmethod
    def adjust_contrast(img, factor=1.5):
        """调整对比度"""
        mean = np.mean(img, axis=(0,1))
        return np.clip((img - mean) * factor + mean, 0, 255).astype(np.uint8)

    @staticmethod
    def rotate(img, angle=5):
        """旋转攻击"""
        h, w = img.shape[:2]
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
        return cv2.warpAffine(img, M, (w, h))

    @staticmethod
    def add_noise(img, strength=0.05):
        """添加噪声"""
        noise = np.random.normal(0, strength * 255, img.shape)
        return np.clip(img + noise, 0, 255).astype(np.uint8)

    @staticmethod
    def jpeg_compress(img, quality=70):
        """JPEG压缩攻击"""
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, enc_img = cv2.imencode('.jpg', img, encode_param)
        return cv2.imdecode(enc_img, 1)

    @staticmethod
    def apply_random_attack(img):
        """应用随机攻击"""
        attacks = [
            lambda x: ImageAttacks.shift(x, random.randint(5, 20)), 
            lambda x: ImageAttacks.crop(x, random.uniform(0.05, 0.2)),
            lambda x: ImageAttacks.adjust_contrast(x, random.uniform(0.7, 1.8)),
            lambda x: ImageAttacks.rotate(x, random.uniform(-10, 10)),
            lambda x: ImageAttacks.add_noise(x, random.uniform(0.02, 0.1)),
            lambda x: ImageAttacks.jpeg_compress(x, random.randint(40, 90))
        ]
        return random.choice(attacks)(img)