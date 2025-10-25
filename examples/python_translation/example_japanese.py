"""データ处理ユーティリティ"""


def process_data(data):
    """データを处理する 引数: 数据: 处理するデータ 戻り値: 处理されたデータ"""
    # データを検证
    if not data:
        return None
    
    # データを変换
    result = [x * 2 for x in data]
    return result


def validate_input(value):
    """入力値を検证する"""
    # 値が正の数かチェック
    if value > 0:
        return True
    return False
