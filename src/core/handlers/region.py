from typing import Dict, Any, Union
from mcp.server.fastmcp import Context

from core.auth import SacloudApiKey, check_auth
from core.handlers import BaseHandler, HttpMethod


class RegionHandler(BaseHandler):
    """リージョン取得用のハンドラークラス"""

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """リージョンハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、リージョン取得用のツールを登録。

        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
            api_key: さくらのクラウドAPIキー
        """
        super().__init__(mcp, zone_urls, api_key)

        # ツールを登録
        self.mcp.tool(name="get_region_list")(self.get_region_list)

    ### MCPツールメソッド

    async def get_region_list(self, ctx: Context) -> Union[Dict[str, Any], str]:
        """さくらのクラウドで利用可能なリージョン一覧を取得します

        Returns:
            dict: リージョン一覧のJSONレスポンス
                - Regions: リージョン情報のリスト
                    - ID: リージョンID
                    - Name: リージョン名
                    - Description: リージョンの説明
        """
        # 認証情報チェック
        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error

        # すべてのゾーンで同じ結果が返されるため、最初のゾーンを使用
        first_zone_url = next(iter(self.zone_urls.values()), None)
        url = f"{first_zone_url}region"

        return await self.handle_api_request(ctx, HttpMethod.GET, url)
