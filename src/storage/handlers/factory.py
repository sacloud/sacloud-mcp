from core.auth import get_api_key,get_objectstorage_api_key
from storage.handlers.archive import ArchiveHandler
from storage.handlers.disk import DiskHandler

def initialize_storage(mcp, zone_urls):
    """全てのハンドラーを初期化する

    Args:
        mcp: MCPクライアント
        zone_urls: ゾーンURLの辞書

    Returns:
        dict: 初期化されたハンドラーの辞書
    """

    api_key = get_api_key()
    return {
        'disk': DiskHandler(mcp, zone_urls, api_key),
        'archive': ArchiveHandler(mcp, zone_urls, api_key),
    }
