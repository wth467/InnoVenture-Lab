import cv2
import numpy as np
import os
import json
from pathlib import Path
from tqdm import tqdm
from core.recovery import enhance_watermark
from core.dct_watermark import DCTWatermark
from core.attacks import ImageAttacks
from .metrics import similarity_report
from utils.pool import parallel_process

def test_robustness(orig_img, orig_wm, attack_types, output_dir="results", success_threshold=0.7):
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化水印系统
    watermarker = DCTWatermark(password=1234, alpha=0.1)
    
    # 嵌入水印
    watermarked = watermarker.embed(orig_img, orig_wm)
    
    # 测试每种攻击
    results = []
    for attack in attack_types:
        # 应用攻击
        if attack == "original":
            attacked_img = watermarked
            attack_name = "原始图像"
        else:
            attack_func = getattr(ImageAttacks, attack)
            attacked_img = attack_func(watermarked)
            attack_name = attack.replace('_', ' ').title()
        
        # 提取水印
        extracted_wm = watermarker.extract(
            attacked_img, 
            orig_wm.shape,
            estimate_attack=True
        )
        
        # 增强水印
        enhanced_wm = enhance_watermark(extracted_wm)
        
        # 计算相似度
        report = similarity_report(orig_wm, enhanced_wm)
        nc = report["NC"]
        
        # 判断是否成功
        success = nc > success_threshold
        status = "✗ 失败" if success else "✓ 成功"
        
        results.append({
            "攻击类型": attack_name,
            "状态": status
        })
    
    return results

def print_test_results(results):
    """
    打印格式化的测试结果
    """
    print("\n" + "=" * 50)
    print("数字水印鲁棒性测试报告")
    print("=" * 50)
    print(f"{'攻击类型':<20} | {'状态':<10}")
    print("-" * 50)
    
    for res in results:
        print(f"{res['攻击类型']:<20} | {res['状态']}")
    
    # 计算成功率
    success_count = sum(1 for res in results if "成功" in res["状态"])
    success_rate = success_count / len(results) * 100
    print("-" * 50)
    print(f"测试完成 | 成功率: {success_rate:.1f}% ({success_count}/{len(results)})")
    print("=" * 50 + "\n")

def simple_robustness_test(img_path, wm_path, attacks=None):
    
    # 加载图像和水印
    img = cv2.imread(img_path)
    wm = cv2.imread(wm_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None or wm is None:
        print("错误：无法加载图像或水印文件")
        return
    
    print(f"开始测试: 图像={os.path.basename(img_path)}, 水印={os.path.basename(wm_path)}")
    
    # 运行测试
    results = test_robustness(img, wm, attacks)
    
    # 打印结果
    print_test_results(results)
    
    return results