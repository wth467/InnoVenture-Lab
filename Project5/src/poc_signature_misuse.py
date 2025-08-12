from sm2 import sm2_keygen, sm2_sign, scalar_mult, G, N, mod_inv
import secrets

def same_user_reuse_k():
    """同一用户重用k导致私钥泄露"""
    # 生成密钥对
    dA, PA = sm2_keygen()
    user_id = "alice@example.com"
    msg1 = b"Transfer $100 to Bob"
    msg2 = b"Transfer $500 to Eve"
    
    # 重用k进行签名
    k = secrets.randbelow(N - 1) + 1
    r1, s1 = sm2_sign(dA, msg1, user_id, k)
    r2, s2 = sm2_sign(dA, msg2, user_id, k)
    
    # 计算私钥
    numerator = (s2 - s1) % N
    denominator = (s1 - s2 + r1 - r2) % N
    dA_recovered = (numerator * mod_inv(denominator, N)) % N
    
    # 验证私钥
    assert dA_recovered == dA
    print(f"[+] 同一用户重用k攻击成功! 恢复私钥: {hex(dA_recovered)}")

def different_users_reuse_k():
    """不同用户重用k导致私钥泄露"""
    # 生成两个密钥对
    dA, PA = sm2_keygen()
    dB, PB = sm2_keygen()
    
    user_idA = "alice@example.com"
    user_idB = "bob@example.com"
    msg1 = b"Alice's message"
    msg2 = b"Bob's message"
    
    # 重用k进行签名
    k = secrets.randbelow(N - 1) + 1
    r1, s1 = sm2_sign(dA, msg1, user_idA, k)
    r2, s2 = sm2_sign(dB, msg2, user_idB, k)
    
    # Alice计算k
    k_calc = (s1 * (1 + dA) + r1 * dA) % N
    
    # Alice计算Bob的私钥
    numerator = (k_calc - s2) % N
    denominator = (s2 + r2) % N
    dB_recovered = (numerator * mod_inv(denominator, N)) % N
    
    # 验证私钥
    assert dB_recovered == dB
    print(f"[+] 不同用户重用k攻击成功! Alice恢复Bob的私钥: {hex(dB_recovered)}")

def same_d_k_sm2_ecdsa():
    """相同d和k用于SM2和ECDSA导致私钥泄露"""
    from ecdsa import ecdsa_sign, hash_to_int
    
    # 生成密钥对
    d, P = sm2_keygen()
    msg1 = b"ECDSA message"
    msg2 = b"SM2 message"
    user_id = "user@example.com"
    
    # 重用k进行签名
    k = secrets.randbelow(N - 1) + 1
    r_ecdsa, s_ecdsa = ecdsa_sign(msg1, d, k)
    r_sm2, s_sm2 = sm2_sign(d, msg2, user_id, k)
    
    # 计算私钥
    e1 = hash_to_int(msg1) % N
    numerator = (s_ecdsa * s_sm2 - e1) % N
    denominator = (r_ecdsa - s_ecdsa * (s_sm2 + r_sm2)) % N
    d_recovered = (numerator * mod_inv(denominator, N)) % N
    
    # 验证私钥
    assert d_recovered == d
    print(f"[+] SM2和ECDSA重用d,k攻击成功! 恢复私钥: {hex(d_recovered)}")

if __name__ == "__main__":
    print("=== SM2签名误用POC验证 ===")
    same_user_reuse_k()
    different_users_reuse_k()
    same_d_k_sm2_ecdsa()