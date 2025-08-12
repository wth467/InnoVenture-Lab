from __future__ import annotations
from typing import List
from .sm3_ref import sm3_hash
from .sm3_opt import sm3_hash_many, sm3_single_block_fast

LEAF_PREFIX = b"\x00"
NODE_PREFIX = b"\x01"

def leaf_hash(data: bytes) -> bytes:
    """叶子哈希：H(0x00 || data)"""
    m = LEAF_PREFIX + data
    if len(m) < 56:
        return sm3_single_block_fast(m)
    return sm3_hash(m)

def node_hash(left: bytes, right: bytes) -> bytes:
    """内部节点哈希：H(0x01 || left || right)"""
    m = NODE_PREFIX + left + right
    if len(m) < 56:
        return sm3_single_block_fast(m)
    return sm3_hash(m)

class MerkleTree:
    """
    MerkleTree 类
    - 构建树并保存所有层（默认）
    - memory_friendly 模式：只计算 root，不保存中间层（节省内存）
    """
    def __init__(self, leaves_data: List[bytes], memory_friendly: bool = False):
        self.n = len(leaves_data)
        self.memory_friendly = memory_friendly
        # 批量计算叶子哈希以提升效率
        leaves_msgs = [LEAF_PREFIX + d for d in leaves_data]
        leaves_hashes = sm3_hash_many(leaves_msgs)
        if memory_friendly:
            self.root = self._compute_root_only(leaves_hashes)
            self.levels = []
        else:
            self.levels = [leaves_hashes]
            self._build_levels()

    def _build_levels(self):
        cur = self.levels[0]
        while len(cur) > 1:
            nxt = []
            for i in range(0, len(cur), 2):
                left = cur[i]
                right = cur[i + 1] if i + 1 < len(cur) else cur[i]
                nxt.append(node_hash(left, right))
            self.levels.append(nxt)
            cur = nxt
        self.root = self.levels[-1][0] if self.levels else sm3_hash(b"")

    def _compute_root_only(self, leaves_hashes: List[bytes]) -> bytes:
        cur = leaves_hashes
        while len(cur) > 1:
            nxt = []
            for i in range(0, len(cur), 2):
                left = cur[i]
                right = cur[i + 1] if i + 1 < len(cur) else cur[i]
                nxt.append(node_hash(left, right))
            cur = nxt
        return cur[0] if cur else sm3_hash(b"")

    def get_root(self) -> bytes:
        return self.root

    def inclusion_proof(self, index: int) -> List[bytes]:
        """生成包含证明（从叶子到根的兄弟节点列表）"""
        if self.memory_friendly:
            raise RuntimeError("memory_friendly 模式下不能生成证明")
        if index < 0 or index >= self.n:
            raise IndexError("index out of range")
        proof = []
        idx = index
        for level in self.levels[:-1]:
            if idx % 2 == 0:
                sib = idx + 1 if idx + 1 < len(level) else idx
            else:
                sib = idx - 1
            proof.append(level[sib])
            idx //= 2
        return proof

    @staticmethod
    def verify_inclusion(leaf_data: bytes, index: int, proof: List[bytes], root: bytes) -> bool:
        """验证包含证明"""
        h = leaf_hash(leaf_data)
        idx = index
        for sib in proof:
            if idx % 2 == 0:
                h = node_hash(h, sib)
            else:
                h = node_hash(sib, h)
            idx //= 2
        return h == root
