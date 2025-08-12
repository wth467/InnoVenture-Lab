import time
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.merkle_rfc6962 import MerkleTree

def bench(num_leaves: int = 1000, leaf_size: int = 32, memory_friendly: bool = True):
    print(f"基准：leaf_count={num_leaves}, leaf_size={leaf_size}, memory_friendly={memory_friendly}")
    leaves = [os.urandom(leaf_size) for _ in range(num_leaves)]
    t0 = time.perf_counter()
    tree = MerkleTree(leaves, memory_friendly=memory_friendly)
    t1 = time.perf_counter()
    print(f"构建完成，耗时 {t1 - t0:.2f} 秒")
    print("root:", tree.get_root().hex())
    if not memory_friendly:
        idx = num_leaves // 2
        t2 = time.perf_counter()
        proof = tree.inclusion_proof(idx)
        t3 = time.perf_counter()
        print(f"生成包含证明耗时 {t3 - t2:.6f} 秒，证明长度 {len(proof)}")
        ok = MerkleTree.verify_inclusion(leaves[idx], idx, proof, tree.get_root())
        print("验证包含证明:", ok)

if __name__ == "__main__":
    # 默认参数（方便在普通机器上快速跑）
    bench(num_leaves=2000, leaf_size=32, memory_friendly=False)
