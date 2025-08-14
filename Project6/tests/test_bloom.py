import unittest
from bloom.tbf import ThresholdBloomFilter

class TestThresholdBloomFilter(unittest.TestCase):
    def test_add_and_check(self):
        tbf = ThresholdBloomFilter(m=100, k=3, tau=5)
        
        # 添加元素
        tbf.add("item1")
        tbf.add("item2")
        
        # 检查存在元素
        self.assertTrue(tbf.check("item1"))
        self.assertTrue(tbf.check("item2"))
        
        # 检查不存在元素
        self.assertFalse(tbf.check("item3"))
    
    def test_threshold(self):
        tbf = ThresholdBloomFilter(m=10, k=1, tau=3)
        
        # 添加元素3次（达到阈值）
        for _ in range(3):
            tbf.add("item")
        
        # 计数器应等于阈值
        self.assertEqual(tbf.bits[tbf._hash("item", 0)], 3)
        
        # 继续添加不应超过阈值
        tbf.add("item")
        self.assertEqual(tbf.bits[tbf._hash("item", 0)], 3)

if __name__ == '__main__':
    unittest.main()