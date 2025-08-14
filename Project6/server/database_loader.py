import json
import os

class DatabaseLoader:
    @staticmethod
    def load_passwords(file_path):
        """从文件加载密码数据库"""
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def save_passwords(file_path, passwords):
        """保存密码数据库"""
        with open(file_path, 'w') as f:
            json.dump(passwords, f)
    
    @staticmethod
    def preprocess_database(passwords, crypto, s):
        """预处理数据库：计算所有t_x值"""
        return [crypto.compute_t_x(pwd, s) for pwd in passwords]