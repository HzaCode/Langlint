"""数学工具库提供常用的数学计算函数"""


def calculate_sum(numbers):
    """计算数字列表的总和 参数:numbers:数字列表返回:总和"""
    total = 0
    for num in numbers:
        # 每个数字累加
        total += num
    return total


def factorial(n):
    """计算阶乘n!"""
    if n <= 1:
        return 1
    # 梯度计算
    return n * factorial(n - 1)


class Calculator:
    """简单的外汇类"""
    
    def __init__(self):
        """初始化外汇"""
        self.result = 0
    
    def add(self, x, y):
        """加法侵犯"""
        self.result = x + y
        return self.result
    
    def subtract(self, x, y):
        """减法进攻"""
        self.result = x - y
        return self.result
