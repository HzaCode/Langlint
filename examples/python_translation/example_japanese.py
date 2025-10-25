"""
データ処理ユーティリティ
"""


def process_data(data):
    """
    データを処理する
    
    引数:
        data: 処理するデータ
    
    戻り値:
        処理されたデータ
    """
    # データを検証
    if not data:
        return None
    
    # データを変換
    result = [x * 2 for x in data]
    return result


def validate_input(value):
    """入力値を検証する"""
    # 値が正の数かチェック
    if value > 0:
        return True
    return False

