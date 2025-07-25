from core.auth import get_api_key,get_objectstorage_api_key
from objectstorage.handlers.objectstorage import ObjectStorageHandler


def initialize_objectstorage(mcp, objectstorage_zone_urls):
    """全てのハンドラーを初期化する

    Args:
        mcp: MCPクライアント
        objectstorage_zone_urls: オブジェクトストレージ用ゾーンURLの辞書

    Returns:
        dict: 初期化されたハンドラーの辞書
    """

    api_key = get_api_key()
    objectstorage_api_key = get_objectstorage_api_key()
    return {
        'objectstorage': ObjectStorageHandler(mcp, objectstorage_zone_urls, api_key,objectstorage_api_key),
    }
