from pypbc import Parameters, Pairing, Element
import hashlib

class CryptoUtils:
    def __init__(self, qbits=512, rbits=160):
        """初始化双线性映射参数"""
        self.params = Parameters(qbits=qbits, rbits=rbits)
        self.pairing = Pairing(self.params)
        self.P = Element.random(self.pairing, G1)  # G1生成元
        self.Q = Element.random(self.pairing, G2)  # G2生成元
    
    def hash_to_g1(self, password):
        """将密码哈希到G1群"""
        h = hashlib.sha256(password.encode()).digest()
        return Element.from_hash(self.pairing, G1, h)
    
    def generate_secret(self):
        """生成服务器私钥"""
        return Element.random(self.pairing, Zr)
    
    def compute_t_x(self, password, s):
        """计算t_x = e(H1(x), sP)"""
        H1_x = self.hash_to_g1(password)
        sP = self.P * s
        return self.pairing.apply(H1_x, sP)