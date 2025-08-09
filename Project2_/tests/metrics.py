import numpy as np

def normalized_correlation(orig_wm, extracted_wm):
    """
    计算归一化相关系数 (NC)
    """
    orig_flat = orig_wm.flatten().astype(np.float32)
    extr_flat = extracted_wm.flatten().astype(np.float32)
    
    # 归一化
    orig_flat = (orig_flat - np.mean(orig_flat)) / np.std(orig_flat)
    extr_flat = (extr_flat - np.mean(extr_flat)) / np.std(extr_flat)
    
    return np.corrcoef(orig_flat, extr_flat)[0, 1]

def bit_error_rate(orig_wm, extracted_wm):
    """
    计算误码率 (BER)
    """
    orig_binary = (orig_wm > 128).astype(int)
    extr_binary = (extracted_wm > 128).astype(int)
    
    total_bits = orig_binary.size
    error_bits = np.sum(orig_binary != extr_binary)
    
    return error_bits / total_bits

def similarity_report(orig_wm, extracted_wm):
    """
    生成相似度报告
    """
    nc = normalized_correlation(orig_wm, extracted_wm)
    ber = bit_error_rate(orig_wm, extracted_wm)
    
    return {
        "NC": round(nc, 4),
        "BER": round(ber, 4),
        "Similarity": f"{max(0, nc * 100):.1f}%"
    }