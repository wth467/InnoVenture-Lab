from sm2 import scalar_mult, G, N, mod_inv
import hashlib

def hash_to_int(msg: bytes) -> int:
    """比特币消息哈希（双重SHA256）"""
    return int.from_bytes(
        hashlib.sha256(
            hashlib.sha256(msg).digest()
        ).digest(), 
        'big'
    )

def ecdsa_sign(msg: bytes, private_key: int, k: int) -> Tuple[int, int]:
    """ECDSA签名算法"""
    R = scalar_mult(k, G)
    r = R.x % N
    if r == 0:
        raise ValueError("r is zero, try different k")
    
    e = hash_to_int(msg) % N
    s = mod_inv(k, N) * (e + r * private_key) % N
    if s == 0:
        raise ValueError("s is zero, try different k")
    
    return r, s

def ecdsa_verify(msg: bytes, signature: Tuple[int, int], public_key: Point) -> bool:
    """ECDSA签名验证"""
    r, s = signature
    if not (1 <= r < N) or not (1 <= s < N):
        return False
    
    e = hash_to_int(msg) % N
    w = mod_inv(s, N)
    u1 = (e * w) % N
    u2 = (r * w) % N
    
    point1 = scalar_mult(u1, G)
    point2 = scalar_mult(u2, public_key)
    R = point_add(point1, point2)
    
    return R.x % N == r