

# 認証関連
INVALID_AUTH_ERROR = '認証情報が設定されていません。ACCESS_TOKEN, ACCESS_TOKEN_SECRET の環境変数を設定してください。'

def get_invalid_zone_message(available_zones: list[str]) -> str:
    """利用可能なゾーン一覧を含む無効ゾーンエラーメッセージを生成"""
    zones_str = ', '.join(available_zones)
    return f"無効なゾーンです。利用可能なゾーン: {zones_str}"