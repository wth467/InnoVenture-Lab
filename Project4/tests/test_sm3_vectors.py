import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.sm3_ref import hexdigest as sm3_hex_ref
from src.sm3_opt import sm3_single_block_fast

def test_sm3_abc_vector():
    # SM3("abc") 已知测试向量（从标准/参考实现取得）
    data = b"abc"
    expected = "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0"
    assert sm3_hex_ref(data) == expected
    # 优化实现的单块快速路径应与参考实现一致
    out = sm3_single_block_fast(data)
    assert out.hex() == expected
