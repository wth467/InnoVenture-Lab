from .database_loader import DatabaseLoader
from .crypto_utils import CryptoUtils
from ..bloom.tbf import ThresholdBloomFilter

class Server:
    def __init__(self, db_path='passwords.json', m=10000, k=3, tau=5):
        self.crypto = CryptoUtils()
        self.s = self.crypto.generate_secret()  # 服务器私钥
        self.db_path = db_path
        
        # 加载并预处理数据库
        passwords = DatabaseLoader.load_passwords(db_path)
        self.S = DatabaseLoader.preprocess_database(passwords, self.crypto, self.s)
        
        # 初始化阈值布隆过滤器
        self.tbf = ThresholdBloomFilter(m, k, tau)
        for t_x in self.S:
            self.tbf.add(str(t_x))  # Element转换为字符串存储
    
    def get_public_key(self):
        """获取服务器公钥 sP"""
        return self.crypto.P * self.s
    
    def process_query(self, U):
        """处理客户端查询"""
        # 计算 V = s * U
        V = U * self.s
        
        # 返回响应：V和阈值布隆过滤器状态
        return V, self.tbf.bits
    
    def add_password(self, password):
        """添加新密码到数据库"""
        passwords = DatabaseLoader.load_passwords(self.db_path)
        if password not in passwords:
            passwords.append(password)
            DatabaseLoader.save_passwords(self.db_path, passwords)
            
            # 更新集合和布隆过滤器
            t_x = self.crypto.compute_t_x(password, self.s)
            self.S.append(t_x)
            self.tbf.add(str(t_x))