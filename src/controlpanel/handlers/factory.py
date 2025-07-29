from controlpanel.handlers.icon import IconHandler
from core.auth import get_api_key


def initialize_controlpanel(mcp, zone_urls):
    """全てのハンドラーを初期化する

    Args:
        mcp: MCPクライアント
        zone_urls: ゾーンURLの辞書

    Returns:
        dict: 初期化されたハンドラーの辞書
    """

    api_key = get_api_key()

    return {
        "icon": IconHandler(mcp, zone_urls, api_key),
    }
