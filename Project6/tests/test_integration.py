import unittest
from server.server import Server
from client.client import Client

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # 创建测试数据库
        self.db_path = "test_db.json"
        with open(self.db_path, 'w') as f:
            json.dump(["password1", "secret@123", "qwerty"], f)
        
        self.server = Server(db_path=self.db_path, m=100, k=3, tau=5)
        self.client = Client()
    
    def test_password_leaked(self):
        # 测试泄露的密码
        self.assertTrue(self.client.check_password("password1", self.server))
        self.assertTrue(self.client.check_password("secret@123", self.server))
    
    def test_password_safe(self):
        # 测试安全的密码
        self.assertFalse(self.client.check_password("safe_password", self.server))
        self.assertFalse(self.client.check_password("another_safe", self.server))
    
    def test_add_password(self):
        # 添加新密码并测试
        self.server.add_password("new_password")
        self.assertTrue(self.client.check_password("new_password", self.server))

if __name__ == '__main__':
    unittest.main()