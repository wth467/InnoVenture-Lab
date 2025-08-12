from __future__ import annotations
from typing import List
from .sm3_ref import IV, MASK32, _rol, P0, sm3_hash  # 复用参考实现中的函数与常量

# 为了速度在本模块内再定义本地 rol（减少全局查找）
def _rol_local(x: int, n: int) -> int:
    n &= 31
    return ((x << n) & MASK32) | ((x & MASK32) >> (32 - n))

# 复制 T_j 常量（本地使用）
T = [0x79CC4519] * 16 + [0x7A879D8A] * 48

def sm3_single_block_fast(message: bytes) -> bytes:
    """
    单块快速路径：适用于填充后只需一个 512-bit 块的消息（len < 56）
    思路：避免多次内存分配、减少函数调用、把循环体局部化以减少查找开销
    """
    mlen = len(message)
    if mlen >= 56:
        # 若消息太长，回退到通用实现
        return sm3_hash(message)
    # 构建 64 字节块
    block = bytearray(64)
    block[0:mlen] = message
    block[mlen] = 0x80
    bit_len = mlen * 8
    block[-8:] = bit_len.to_bytes(8, "big")
    # W0..W15 解包
    W = [0] * 68
    for i in range(16):
        W[i] = int.from_bytes(block[i*4:(i+1)*4], "big")
    # W16..W67 扩展（内联 P1 的计算）
    for j in range(16, 68):
        x = W[j - 16] ^ W[j - 9] ^ _rol_local(W[j - 3], 15)
        # 直接内联 P1(x) = x ^ (x<<<15) ^ (x<<<23) 的部分以减少函数调用
        Wj = (x ^ _rol_local(x, 15) ^ _rol_local(W[j - 13], 7) ^ W[j - 6]) & MASK32
        W[j] = Wj
    # W' 计算
    Wp = [(W[j] ^ W[j + 4]) & MASK32 for j in range(64)]
    # 压缩环节（局部变量用于减少属性/全局查找）
    A, B, C, D, E, F, G, H = IV[:]  # 复制 IV
    for j in range(64):
        SS1 = _rol_local((_rol_local(A, 12) + E + _rol_local(T[j], j)) & MASK32, 7)
        SS2 = SS1 ^ _rol_local(A, 12)
        if j < 16:
            FFv = A ^ B ^ C
            GGv = E ^ F ^ G
        else:
            FFv = ((A & B) | (A & C) | (B & C)) & MASK32
            GGv = ((E & F) | (((~E) & MASK32) & G)) & MASK32
        TT1 = (FFv + D + SS2 + Wp[j]) & MASK32
        TT2 = (GGv + H + SS1 + W[j]) & MASK32
        D = C
        C = _rol_local(B, 9)
        B = A
        A = TT1
        H = G
        G = _rol_local(F, 19)
        F = E
        E = P0(TT2)
    V = [(IV[i] ^ v) & MASK32 for i, v in enumerate([A, B, C, D, E, F, G, H])]
    return b"".join(x.to_bytes(4, "big") for x in V)

def sm3_hash_many(messages: List[bytes]) -> List[bytes]:
    """
    批量哈希接口：对大量短消息（比如 Merkle 叶子）可以显著降低 Python 调用开销。
    简单策略：若消息长度 < 56 则走单块快速路径，否则使用参考实现。
    """
    out = []
    for m in messages:
        if len(m) < 56:
            out.append(sm3_single_block_fast(m))
        else:
            out.append(sm3_hash(m))
    return out

# 测试可用性
if __name__ == "__main__":
    for s in [b"", b"abc", b"hello world"]:
        print(s, "->", sm3_single_block_fast(s).hex())
