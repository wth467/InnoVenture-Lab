import cv2
import numpy as np
import json
from pathlib import Path
from tqdm import tqdm

from core.recovery import enhance_watermark
from core.dct_watermark import DCTWatermark
from core.attacks import ImageAttacks
from .metrics import similarity_report
from utils.pool import parallel_process

def test_robustness(orig_img, orig_wm, attack_types, output_dir="results"):
    """
    水印鲁棒性测试
    :param orig_img: 原始图像
    :param orig_wm: 原始水印
    :param attack_types: 攻击类型列表
    :param output_dir: 结果输出目录
    """
    # 初始化水印系统
    watermarker = DCTWatermark(password=1234)
    
    # 嵌入水印
    watermarked = watermarker.embed(orig_img, orig_wm)
    cv2.imwrite(f"{output_dir}/watermarked.jpg", watermarked)
    
    # 测试每种攻击
    results = []
    for attack in tqdm(attack_types, desc="Testing attacks"):
        # 应用攻击
        if attack == "original":
            attacked_img = watermarked
            attack_name = "原始图像"
        else:
            attacked_img = getattr(ImageAttacks, attack)(watermarked)
            attack_name = attack.replace('_', ' ').title()
        
        # 保存攻击后图像
        attack_img_path = f"{output_dir}/{attack}.jpg"
        cv2.imwrite(attack_img_path, attacked_img)
        
        # 提取水印
        extracted_wm = watermarker.extract(
            attacked_img, 
            orig_wm.shape,
            estimate_attack=True
        )
        
        # 增强水印
        enhanced_wm = enhance_watermark(extracted_wm)
        
        # 保存提取的水印
        wm_path = f"{output_dir}/{attack}_wm.png"
        cv2.imwrite(wm_path, enhanced_wm)
        
        # 计算相似度
        report = similarity_report(orig_wm, enhanced_wm)
        
        results.append({
            "attack": attack_name,
            "image": Path(attack_img_path).name,
            "watermark": Path(wm_path).name,
            **report
        })
    
    # 保存结果
    with open(f"{output_dir}/results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

def batch_test(image_paths, wm_path, output_dir="batch_results"):
    """
    批量测试多张图像
    """
    orig_wm = cv2.imread(wm_path, cv2.IMREAD_GRAYSCALE)
    
    tasks = []
    for img_path in image_paths:
        orig_img = cv2.imread(img_path)
        tasks.append((orig_img, orig_wm))
    
    # 并行处理
    attack_types = ["original", "shift", "crop", "adjust_contrast", "rotate", "add_noise"]
    results = parallel_process(
        tasks, 
        lambda args: test_robustness(*args, attack_types, output_dir),
        n_jobs=4
    )
    
    return results