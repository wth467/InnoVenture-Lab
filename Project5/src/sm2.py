import hashlib
import secrets
from typing import Tuple, Optional

# SM2椭圆曲线参数
P = 0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3
A = 0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498
B = 0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A
G_X = 0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D
G_Y = 0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2
N = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7

class Point:
    """椭圆曲线点类"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y
    
    def __str__(self) -> str:
        return f"({hex(self.x)}, {hex(self.y)})"

# 无穷远点
INFINITY = Point(0, 0)

# 基点G
G = Point(G_X, G_Y)

def mod_inv(a: int, n: int) -> int:
    """扩展欧几里得算法求模逆"""
    t, new_t = 0, 1
    r, new_r = n, a
    
    while new_r != 0:
        quotient = r // new_r
        t, new_t = new_t, t - quotient * new_t
        r, new_r = new_r, r - quotient * new_r
    
    if r > 1:
        raise ValueError("a is not invertible")
    if t < 0:
        t += n
    
    return t

def point_add(P: Point, Q: Point) -> Point:
    """椭圆曲线点加法"""
    if P == INFINITY:
        return Q
    if Q == INFINITY:
        return P
    if P.x == Q.x and P.y != Q.y:
        return INFINITY
    
    if P == Q:
        # 倍点公式
        lam = (3 * P.x * P.x + A) * mod_inv(2 * P.y, P) % P
    else:
        # 点加公式
        lam = (Q.y - P.y) * mod_inv(Q.x - P.x, P) % P
    
    x3 = (lam * lam - P.x - Q.x) % P
    y3 = (lam * (P.x - x3) - P.y) % P
    
    return Point(x3, y3)

def point_double(P: Point) -> Point:
    """椭圆曲线倍点运算"""
    return point_add(P, P)

def scalar_mult(k: int, P: Point) -> Point:
    """Double-and-Add标量乘法"""
    Q = INFINITY
    while k > 0:
        if k & 1:
            Q = point_add(Q, P)
        P = point_double(P)
        k >>= 1
    return Q

def hash_msg(msg: bytes) -> int:
    """消息哈希函数（简化版，实际应使用SM3）"""
    return int.from_bytes(hashlib.sha256(msg).digest(), 'big')

def sm3_hash(data: bytes) -> bytes:
    """SM3哈希函数（简化实现）"""
    # 实际应用中应使用国密SM3标准实现
    return hashlib.sha256(data).digest()

def compute_za(user_id: str, public_key: Point) -> bytes:
    """计算ZA值"""
    entla = len(user_id).to_bytes(2, 'big')
    data = entla + user_id.encode() + A.to_bytes(32, 'big') + B.to_bytes(32, 'big')
    data += G_X.to_bytes(32, 'big') + G_Y.to_bytes(32, 'big')
    data += public_key.x.to_bytes(32, 'big') + public_key.y.to_bytes(32, 'big')
    return sm3_hash(data)

def sm2_sign(private_key: int, msg: bytes, user_id: str, k: Optional[int] = None) -> Tuple[int, int]:
    """SM2签名算法"""
    public_key = scalar_mult(private_key, G)
    za = compute_za(user_id, public_key)
    e = int.from_bytes(sm3_hash(za + msg), 'big') % N
    
    while True:
        if k is None:
            k = secrets.randbelow(N - 1) + 1
        
        kG = scalar_mult(k, G)
        r = (e + kG.x) % N
        if r == 0 or r + k == N:
            k = None
            continue
        
        s = (mod_inv(1 + private_key, N) * (k - r * private_key)) % N
        if s == 0:
            k = None
            continue
        
        return r, s

def sm2_verify(public_key: Point, msg: bytes, signature: Tuple[int, int], user_id: str) -> bool:
    """SM2签名验证"""
    r, s = signature
    if not (1 <= r < N) or not (1 <= s < N):
        return False
    
    za = compute_za(user_id, public_key)
    e = int.from_bytes(sm3_hash(za + msg), 'big') % N
    t = (r + s) % N
    
    point1 = scalar_mult(s, G)
    point2 = scalar_mult(t, public_key)
    xy = point_add(point1, point2)
    
    R = (e + xy.x) % N
    return R == r

def sm2_keygen() -> Tuple[int, Point]:
    """生成SM2密钥对"""
    private_key = secrets.randbelow(N - 1) + 1
    public_key = scalar_mult(private_key, G)
    return private_key, public_key