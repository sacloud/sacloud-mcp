from bill.handlers.bill import BillHandler
from core.auth import get_api_key

def initialize_bill(mcp, zone_urls):
    """全てのハンドラーを初期化する

    Args:
        mcp: MCPクライアント
        zone_urls: ゾーンURLの辞書

    Returns:
        dict: 初期化されたハンドラーの辞書
    """

    api_key = get_api_key()

    return {
        "bill": BillHandler(mcp, zone_urls, api_key),
    }
