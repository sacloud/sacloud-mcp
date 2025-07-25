from typing import Dict, Any, Union
from mcp.server.fastmcp import Context

from core.auth import SacloudApiKey
from core.handlers.base import BaseHandler, HttpMethod


class ZoneHandler(BaseHandler):
    """ゾーン取得用のハンドラークラス"""

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """ゾーンハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、ゾーン取得用のツールを登録。

        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
        """
        super().__init__(mcp, zone_urls, api_key)

        # ツールを登録
        self.mcp.tool(name="get_zone_list")(self.get_zone_list)

    async def get_zone_list(self, ctx: Context) -> Union[Dict[str, Any], str]:
        """さくらのクラウドで利用可能なゾーン一覧を取得します

        Returns:
            dict: ゾーン一覧のJSONレスポンス
        """
        # すべてのゾーンで同じ結果が返されるため、最初のゾーンを使用
        first_zone_url = next(iter(self.zone_urls.values()), None)
        url = f"{first_zone_url}zone"

        # 基底クラスの統一API処理を使用
        return await self.handle_api_request(ctx, HttpMethod.GET, url)
