from core.auth import get_api_key
from compute.handlers.interface import InterfaceHandler
from compute.handlers.server import ServerHandler


def initialize_compute(mcp, zone_urls):
    """全てのハンドラーを初期化する

    Args:
        mcp: MCPクライアント
        zone_urls: ゾーンURLの辞書

    Returns:
        dict: 初期化されたハンドラーの辞書
    """

    api_key = get_api_key()

    return {
        "server": ServerHandler(mcp, zone_urls, api_key),
        "interface": InterfaceHandler(mcp, zone_urls, api_key),
    }
