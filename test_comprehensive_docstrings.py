# -*- coding: utf-8 -*-
"""这是一个模块级的
多行 docstring
用来测试翻译功能
"""

def single_line_double():
    """这是单行双引号 docstring"""
    pass

def single_line_single():
    '''这是单行单引号 docstring'''
    pass

def multi_line_double():
    """
    这是多行双引号 docstring 的第一行
    这是第二行
    这是第三行
    """
    return True

def multi_line_single():
    '''
    这是多行单引号 docstring 的第一行
    这是第二行
    这是第三行
    '''
    return False

def compact_multi_double():
    """第一行
    第二行
    第三行"""
    pass

def compact_multi_single():
    '''第一行
    第二行
    第三行'''
    pass

class TestClass:
    """类的 docstring
    可能有多行
    描述这个类
    """
    
    def method1(self):
        """方法的 docstring"""
        # 这是一个注释
        pass
    
    def method2(self):
        '''另一个方法
        有多行描述
        '''
        pass

def with_code():
    """计算两个数的和
    参数:
        a: 第一个数
        b: 第二个数
    返回:
        两数之和
    """
    a = 10
    b = 20
    # 执行加法运算
    return a + b


