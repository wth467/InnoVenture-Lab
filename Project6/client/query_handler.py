from pypbc import Element
import hashlib

class QueryHandler:
    def __init__(self, pairing, P):
        self.pairing = pairing
        self.P = P
    
    def prepare_query(self, password):
        """准备查询：生成随机数r，计算U = r * H1(p)"""
        # 哈希密码到G1
        h = hashlib.sha256(password.encode()).digest()
        H1_p = Element.from_hash(self.pairing, G1, h)
        
        # 生成随机数r
        r = Element.random(self.pairing, Zr)
        
        # 计算 U = r * H1(p)
        U = H1_p * r
        
        return U, r
    
    def verify_response(self, V, r, tbf_bits, k=3, tau=5):
        """验证服务器响应"""
        # 计算 T = e(V, P)
        T = self.pairing.apply(V, self.P)
        
        # 检查T是否在阈值布隆过滤器中
        T_str = str(T)
        for i in range(k):
            idx = hash(f"{T_str}-{i}") % len(tbf_bits)
            if tbf_bits[idx] == 0:  # 如果任一位置为0，则密码安全
                return False
        
        return True  # 所有位置非0，密码可能泄露