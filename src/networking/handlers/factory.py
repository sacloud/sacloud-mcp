from core.auth import get_api_key
from networking.handlers.bridge import BridgeHandler
from networking.handlers.router import RouterHandler
from networking.handlers.switch import SwitchHandler


def initialize_networking(mcp, zone_urls):
    """全てのハンドラーを初期化する

    Args:
        mcp: MCPクライアント
        zone_urls: ゾーンURLの辞書

    Returns:
        dict: 初期化されたハンドラーの辞書
    """

    api_key = get_api_key()

    return {
        "bridge": BridgeHandler(mcp, zone_urls, api_key),
        "switch": SwitchHandler(mcp, zone_urls, api_key),
        "router": RouterHandler(mcp, zone_urls, api_key),
    }
