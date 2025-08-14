import unittest
from server.crypto_utils import CryptoUtils

class TestCryptoUtils(unittest.TestCase):
    def setUp(self):
        self.crypto = CryptoUtils(qbits=160, rbits=80)  # 小参数加速测试
    
    def test_bilinear_property(self):
        a = Element.random(self.crypto.pairing, Zr)
        b = Element.random(self.crypto.pairing, Zr)
        
        # e(aP, bQ) = e(P, Q)^{ab}
        left = self.crypto.pairing.apply(self.crypto.P * a, self.crypto.Q * b)
        right = self.crypto.pairing.apply(self.crypto.P, self.crypto.Q) ** (a * b)
        
        self.assertEqual(left, right)
    
    def test_hash_to_g1(self):
        pwd = "test_password"
        H1 = self.crypto.hash_to_g1(pwd)
        self.assertTrue(H1.is_valid())
        self.assertEqual(H1.element_type(), 'G1')
    
    def test_t_x_computation(self):
        s = self.crypto.generate_secret()
        t_x = self.crypto.compute_t_x("password123", s)
        self.assertTrue(t_x.element_type(), 'GT')

if __name__ == '__main__':
    unittest.main()