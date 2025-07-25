from appliance.handlers.database import DatabaseHandler
from appliance.handlers.loadbalancer import LoadbalancerHandler
from appliance.handlers.vpn_router import VpnRouterHandler
from core.auth import get_api_key


def initialize_appliance(mcp, zone_urls):
    """全てのハンドラーを初期化する

    Args:
        mcp: MCPクライアント
        zone_urls: ゾーンURLの辞書

    Returns:
        dict: 初期化されたハンドラーの辞書
    """

    api_key = get_api_key()

    return {
        "database": DatabaseHandler(mcp, zone_urls, api_key),
        "loadbalancer": LoadbalancerHandler(mcp, zone_urls, api_key),
        "vpnrouter": VpnRouterHandler(mcp, zone_urls, api_key),
    }
