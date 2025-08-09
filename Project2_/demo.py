import cv2
import numpy as np
from tests.robustness import test_robustness
from core.dct_watermark import DCTWatermark
from core.attacks import ImageAttacks

# 生成测试水印
wm = np.zeros((32, 32), dtype=np.uint8)
cv2.putText(wm, "W2023", (10, 40), 
           cv2.FONT_HERSHEY_SIMPLEX, 1.2, 255, 3)
cv2.imwrite("watermark.png", wm)

# 读取测试图像
img = cv2.imread('test.png')

# 测试鲁棒性
attacks = ["original", "shift", "crop", "adjust_contrast", "rotate", "add_noise"]
results = test_robustness(img, wm, attacks, "test_results")

# 打印结果
print("鲁棒性测试结果:")
for res in results:
    print(f"{res['attack']:>15} | NC: {res['NC']:.3f} | BER: {res['BER']:.3f}")