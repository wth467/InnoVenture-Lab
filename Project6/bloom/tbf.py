class ThresholdBloomFilter:
    def __init__(self, m, k, tau):
        """
        初始化阈值布隆过滤器
        :param m: 布隆过滤器位数
        :param k: 哈希函数数量
        :param tau: 计数器阈值
        """
        self.bits = [0] * m  # 初始化所有位为0
        self.m = m
        self.k = k
        self.tau = tau
    
    def add(self, item):
        """添加元素到布隆过滤器"""
        for i in range(self.k):
            idx = self._hash(item, i)
            # 增加计数器但不超过阈值
            if self.bits[idx] < self.tau:
                self.bits[idx] += 1
    
    def check(self, item):
        """检查元素是否可能在集合中"""
        for i in range(self.k):
            idx = self._hash(item, i)
            if self.bits[idx] == 0:
                return False
        return True
    
    def _hash(self, item, seed):
        """哈希函数：item + seed 取模 m"""
        return hash(f"{item}-{seed}") % self.m