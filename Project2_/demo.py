import cv2
import numpy as np
import os
from tests.robustness import simple_robustness_test, print_test_results

# 创建测试目录
os.makedirs("test_images", exist_ok=True)
os.makedirs("watermarks", exist_ok=True)

# 生成水印
def create_watermark():
    wm = np.zeros((64, 64), dtype=np.uint8)
    cv2.rectangle(wm, (10, 10), (54, 54), 255, 3)
    cv2.putText(wm, "WM", (15, 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    wm_path = "watermarks/simple_wm.png"
    cv2.imwrite(wm_path, wm)
    return wm_path

# 创建测试图像
def create_test_image():
    img = np.zeros((512, 512, 3), dtype=np.uint8)
    cv2.circle(img, (256, 256), 150, (0, 150, 255), -1)
    cv2.rectangle(img, (100, 100), (412, 412), (255, 200, 0), 5)
    img_path = "test_images/circle_square.png"
    cv2.imwrite(img_path, img)
    return img_path

# 主函数
def main():
    print("=" * 50)
    print("数字水印鲁棒性测试系统")
    print("=" * 50)
    
    # 创建测试文件
    wm_path = create_watermark()
    img_path = create_test_image()
    
    print(f"测试图像: {img_path}")
    print(f"水印文件: {wm_path}")
    
    # 定义攻击列表
    attacks = [
        "adjust_contrast",  # 调整对比度
        "rotate",           # 旋转
        "add_noise",        # 添加噪声
        "jpeg_compress"     # JPEG压缩
    ]
    
    # 运行测试
    results = simple_robustness_test(img_path, wm_path, attacks)
    
    # 显示测试结果
    print("测试完成！结果汇总:")
    print_test_results(results)

if __name__ == "__main__":
    main()