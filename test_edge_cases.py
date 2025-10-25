# 测试极端情况

def empty_lines_in_docstring():
    """
    第一行
    
    中间有空行
    
    最后一行
    """
    pass

def docstring_with_quotes():
    """这个 docstring 包含 "引号" 和 '单引号'"""
    pass

def nested_quotes():
    '''这是 """三引号""" 在单引号中'''
    pass

def special_chars():
    """包含特殊字符：@#$%^&*()
    换行后还有：【】、；''""
    """
    pass

def very_long_line():
    """这是一个非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的 docstring"""
    pass

def unicode_emoji():
    """包含 emoji 😀 🎉 🚀 的 docstring
    多行测试 ✨ 💡
    """
    pass


