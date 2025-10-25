#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file for language filter functionality.
This is a pure English docstring and should NOT be detected.
"""

def function_with_english_comment():
    """
    This is a pure English function docstring.
    It should be ignored by the language filter.
    """
    # This is an English comment
    print("Hello, World!")


def function_with_chinese_comment():
    """
    这是一个包含中文的函数文档字符串。
    应该被识别为需要翻译的内容。
    """
    # 这是一个中文注释
    print("你好，世界！")


def function_with_mixed_content():
    """
    This function has mixed content.
    这个函数包含混合内容。
    """
    # Pure English comment - should be ignored
    x = 1
    
    # 中文注释 - 应该被识别
    y = 2
    
    # Mixed: This is English and 这是中文
    z = 3


class EnglishClass:
    """Pure English class docstring."""
    
    def method(self):
        """English method docstring."""
        pass


class ChineseClass:
    """包含中文的类文档字符串"""
    
    def method(self):
        """中文方法文档字符串"""
        # 中文注释
        pass


# English comment at the end
# 中文注释在最后

