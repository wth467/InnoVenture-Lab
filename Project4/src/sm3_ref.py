from __future__ import annotations
import struct
from typing import List

MASK32 = 0xFFFFFFFF

def _rol(x: int, n: int) -> int:
    """32 位循环左移（中文注释）"""
    n &= 31
    return ((x << n) & MASK32) | ((x & MASK32) >> (32 - n))

def P0(x: int) -> int:
    """置换函数 P0(X) = X ^ (X <<< 9) ^ (X <<< 17)"""
    return x ^ _rol(x, 9) ^ _rol(x, 17)

def P1(x: int) -> int:
    """置换函数 P1(X) = X ^ (X <<< 15) ^ (X <<< 23)"""
    return x ^ _rol(x, 15) ^ _rol(x, 23)

def FF(j: int, x: int, y: int, z: int) -> int:
    """
    布尔函数 FF_j
    j in [0,15] : X ^ Y ^ Z
    j in [16,63]: (X & Y) | (X & Z) | (Y & Z)
    """
    if 0 <= j <= 15:
        return x ^ y ^ z
    return ((x & y) | (x & z) | (y & z)) & MASK32

def GG(j: int, x: int, y: int, z: int) -> int:
    """
    布尔函数 GG_j
    j in [0,15] : X ^ Y ^ Z
    j in [16,63]: (X & Y) | ((~X) & Z)
    """
    if 0 <= j <= 15:
        return x ^ y ^ z
    return ((x & y) | (((~x) & MASK32) & z)) & MASK32

# 初始化向量 IV（规范给定）
IV = [
    0x7380166F,
    0x4914B2B9,
    0x172442D7,
    0xDA8A0600,
    0xA96F30BC,
    0x163138AA,
    0xE38DEE4D,
    0xB0FB0E4E,
]

# 常量 T_j
T_j = [0x79CC4519] * 16 + [0x7A879D8A] * 48

def _pad(message: bytes) -> bytes:
    """
    SM3 填充函数：
    1. 追加 1 比特（0x80）
    2. 填充若干 0x00，直到消息位长 ≡ 448 (mod 512)
    3. 追加 64-bit 大端表示的原始消息长度（bits）
    返回填充后的字节串
    """
    ml = len(message) * 8
    msg = bytearray(message)
    msg.append(0x80)
    while (len(msg) * 8) % 512 != 448:
        msg.append(0x00)
    msg += struct.pack(">Q", ml)
    return bytes(msg)

def _expand_block(block: bytes) -> (List[int], List[int]):
    """
    扩展单个 512-bit 块（64 字节）为 W[0..67] 与 Wp[0..63]
    返回 (W, Wp)
    """
    assert len(block) == 64
    # W0..W15
    W = list(struct.unpack(">16I", block))
    # W16..W67，根据规范递推
    for j in range(16, 68):
        x = W[j - 16] ^ W[j - 9] ^ _rol(W[j - 3], 15)
        Wj = P1(x) ^ _rol(W[j - 13], 7) ^ W[j - 6]
        W.append(Wj & MASK32)
    # W'j = Wj ^ W_{j+4}, j=0..63
    Wp = [(W[j] ^ W[j + 4]) & MASK32 for j in range(64)]
    return W, Wp

def compress(V: List[int], block: bytes) -> List[int]:
    """
    压缩函数 CF，输入当前链值 V (8*32bit) 与 64 字节块 block，
    返回新的链值 V'
    """
    W, Wp = _expand_block(block)
    A, B, C, D, E, F, G, H = V
    for j in range(64):
        SS1 = _rol((_rol(A, 12) + E + _rol(T_j[j], j)) & MASK32, 7)
        SS2 = SS1 ^ _rol(A, 12)
        TT1 = (FF(j, A, B, C) + D + SS2 + Wp[j]) & MASK32
        TT2 = (GG(j, E, F, G) + H + SS1 + W[j]) & MASK32
        D = C
        C = _rol(B, 9)
        B = A
        A = TT1
        H = G
        G = _rol(F, 19)
        F = E
        E = P0(TT2)
    # 链值异或更新
    return [((V[i] ^ v) & MASK32) for i, v in enumerate([A, B, C, D, E, F, G, H])]

def sm3_hash(data: bytes) -> bytes:
    """
    计算 SM3 摘要并返回 32 字节（二进制）
    典型用法：sm3_hash(b"abc")
    """
    msg = _pad(data)
    V = IV.copy()
    for i in range(0, len(msg), 64):
        block = msg[i:i + 64]
        V = compress(V, block)
    return b"".join(struct.pack(">I", v & MASK32) for v in V)

def hexdigest(data: bytes) -> str:
    """返回十六进制字符串表示"""
    return sm3_hash(data).hex()

# 当模块作为脚本运行时，输出几个测试向量
if __name__ == "__main__":
    tests = [b"", b"abc", b"message digest"]
    for t in tests:
        print(f"m={t!r}, sm3={hexdigest(t)}")
