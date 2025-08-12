from ecdsa import ecdsa_sign, ecdsa_verify, hash_to_int
from sm2 import scalar_mult, G, N, mod_inv
import secrets

def forge_satoshi_signature():
    """伪造中本聪签名演示"""
    # 中本聪的私钥（示例值）
    satoshi_priv = 0x18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725
    satoshi_pub = scalar_mult(satoshi_priv, G)
    
    print("=== 伪造中本聪签名演示 ===")
    print(f"中本聪公钥: {satoshi_pub}")
    
    # 重用的k值
    k = secrets.randbelow(N - 1) + 1
    
    # 中本聪签名两条不同消息
    msg1 = b"Send 10 BTC to Alice"
    msg2 = b"Send 5 BTC to Bob"
    r1, s1 = ecdsa_sign(msg1, satoshi_priv, k)
    r2, s2 = ecdsa_sign(msg2, satoshi_priv, k)
    
    print(f"消息1签名: (r={hex(r1)}, s={hex(s1)})")
    print(f"消息2签名: (r={hex(r2)}, s={hex(s2)})")
    
    # 恢复私钥
    e1 = hash_to_int(msg1) % N
    e2 = hash_to_int(msg2) % N
    
    numerator = (s1 * e2 - s2 * e1) % N
    denominator = (s2 * r1 - s1 * r2) % N
    recovered_priv = (numerator * mod_inv(denominator, N)) % N
    
    # 验证私钥
    assert recovered_priv == satoshi_priv
    print(f"[+] 成功恢复中本聪私钥: {hex(recovered_priv)}")
    
    # 使用恢复的私钥伪造签名
    forged_msg = b"Transfer all BTC to Attacker"
    forged_sig = ecdsa_sign(forged_msg, recovered_priv, k)
    
    # 验证伪造的签名
    is_valid = ecdsa_verify(forged_msg, forged_sig, satoshi_pub)
    print(f"[+] 伪造签名验证结果: {'成功' if is_valid else '失败'}")
    print(f"伪造消息: {forged_msg.decode()}")
    print(f"伪造签名: (r={hex(forged_sig[0])}, s={hex(forged_sig[1])})")

if __name__ == "__main__":
    forge_satoshi_signature()