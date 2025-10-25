"""
数学工具库
提供常用的数学计算函数
"""


def calculate_sum(numbers):
    """
    计算数字列表的总和
    
    参数:
        numbers: 数字列表
    
    返回:
        总和
    """
    total = 0
    for num in numbers:
        # 累加每个数字
        total += num
    return total


def factorial(n):
    """计算阶乘 n!"""
    if n <= 1:
        return 1
    # 递归计算
    return n * factorial(n - 1)


class Calculator:
    """简单的计算器类"""
    
    def __init__(self):
        """初始化计算器"""
        self.result = 0
    
    def add(self, x, y):
        """加法运算"""
        self.result = x + y
        return self.result
    
    def subtract(self, x, y):
        """减法运算"""
        self.result = x - y
        return self.result

