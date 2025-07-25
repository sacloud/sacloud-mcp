from typing import Dict, Any, Union
from mcp.server.fastmcp import Context

from core.auth import SacloudApiKey, check_auth
from core.handlers.base import BaseHandler, HttpMethod


class IconHandler(BaseHandler):
    """アイコン操作用のハンドラークラス"""

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """アイコンハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、アイコン操作用のツールを登録。

        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
            api_key: さくらのクラウドAPIキー
        """
        super().__init__(mcp, zone_urls, api_key)

        # ツールを登録
        self.mcp.tool(name="get_icon_list")(self.get_icon_list)
        self.mcp.tool(name="get_icon_tag_list")(self.get_icon_tag_list)

    ### MCPツールメソッド

    async def get_icon_list(self, ctx: Context) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからアイコン一覧を取得します（全ゾーン共通）

        Returns:
            dict: アイコン一覧のJSONレスポンス
                - Icons: アイコン情報のリスト
                    - ID: アイコンID
                    - Name: アイコン名
                    - Scope: スコープ
                    - Image: 画像データ
                    - CreatedAt: 作成日時
                    - ModifiedAt: 更新日時
        """
        # 認証情報チェック
        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error

        # アイコンは全ゾーン共通のため、最初のゾーンを使用
        first_zone_url = next(iter(self.zone_urls.values()), None)
        url = f"{first_zone_url}icon"

        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def get_icon_tag_list(self, ctx: Context) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからアイコンタグ一覧を取得します（全ゾーン共通）

        Returns:
            dict: アイコンタグ一覧のJSONレスポンス
                - Tags: タグ情報のリスト
                    - Name: タグ名
                    - Count: 該当するアイコン数
        """
        # 認証情報チェック
        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error

        # アイコンは全ゾーン共通のため、最初のゾーンを使用
        first_zone_url = next(iter(self.zone_urls.values()), None)
        url = f"{first_zone_url}icon/tag"

        return await self.handle_api_request(ctx, HttpMethod.GET, url)
