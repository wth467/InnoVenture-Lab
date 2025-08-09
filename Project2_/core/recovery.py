import cv2
import numpy as np

def estimate_rotation(img, step=1):
    """
    估计并纠正旋转攻击
    :param img: 被旋转的图像
    :param step: 角度搜索步长
    :return: 纠正后的图像, 估计的旋转角度
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 使用霍夫变换检测直线
    lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
    
    if lines is not None:
        angles = []
        for line in lines:
            rho, theta = line[0]
            angle = np.degrees(theta) - 90
            if abs(angle) < 45:  # 只考虑接近水平的线
                angles.append(angle)
        
        if angles:
            median_angle = np.median(angles)
            h, w = img.shape[:2]
            M = cv2.getRotationMatrix2D((w/2, h/2), median_angle, 1)
            corrected = cv2.warpAffine(img, M, (w, h))
            return corrected, median_angle
    
    return img, 0

def enhance_watermark(wm_extracted, kernel_size=3):
    """
    增强提取的水印
    :param wm_extracted: 提取的水印图像
    :param kernel_size: 形态学操作核大小
    :return: 增强后的水印
    """
    # 1. 中值滤波去除噪声
    filtered = cv2.medianBlur(wm_extracted, kernel_size)
    
    # 2. 自适应阈值处理
    binary = cv2.adaptiveThreshold(
        filtered, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # 3. 形态学操作增强
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    
    # 4. 轮廓筛选 - 移除小噪点
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(closed)
    for cnt in contours:
        if cv2.contourArea(cnt) > 10:  # 只保留面积大于10的轮廓
            cv2.drawContours(mask, [cnt], -1, 255, -1)
    
    return mask