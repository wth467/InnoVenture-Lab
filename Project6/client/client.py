from .query_handler import QueryHandler
from server.crypto_utils import CryptoUtils

class Client:
    def __init__(self):
        self.crypto = CryptoUtils()
        self.query_handler = QueryHandler(self.crypto.pairing, self.crypto.P)
    
    def check_password(self, password, server):
        """检查密码是否泄露"""
        # 准备查询
        U, r = self.query_handler.prepare_query(password)
        
        # 发送查询到服务器
        V, tbf_bits = server.process_query(U)
        
        # 验证响应
        return self.query_handler.verify_response(V, r, tbf_bits)