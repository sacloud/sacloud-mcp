from typing import Dict, Any, Optional, Union
from mcp.server.fastmcp import Context
from core.auth import SacloudApiKey
from core.handlers.base import BaseHandler, HttpMethod


class BridgeHandler(BaseHandler):
    """ブリッジ操作用のハンドラークラス"""

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """ブリッジハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、ブリッジ操作用のツールを登録。

        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
        """
        super().__init__(mcp, zone_urls, api_key)

        # ツールを登録
        self.mcp.tool(name="get_bridge_list")(self.get_bridge_list)
        self.mcp.tool(name="create_bridge")(self.create_bridge)
        self.mcp.tool(name="delete_bridge")(self.delete_bridge)

    ### MCPツールメソッド

    async def get_bridge_list(
        self, ctx: Context, zone: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからブリッジ一覧を取得します

        Args:
            zone (str): 取得対象のゾーン

        Returns:
            dict: ブリッジ一覧のJSONレスポンス
                - Bridge: ブリッジのリスト
                    - ID: ブリッジID
                    - Name: ブリッジ名
                    - Description: 説明
                    - CreatedAt: 作成日時
                    - Region: リージョン情報
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        url = f"{self.zone_urls[zone]}bridge"
        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def create_bridge(
        self, ctx: Context, zone: str, name: str, description: Optional[str] = None
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIでブリッジを作成します

        Args:
            zone (str): 作成対象のゾーン
            name (str): ブリッジ名
            description (str, optional): ブリッジの説明

        Returns:
            dict: 作成されたブリッジのJSONレスポンス
                - Bridge: 作成されたブリッジ情報
                    - ID: ブリッジID
                    - Name: ブリッジ名
                    - Description: 説明
                    - CreatedAt: 作成日時
                    - Region: リージョン情報
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        # ブリッジ名の検証
        if not name:
            return "ブリッジ名は必須です。"

        url = f"{self.zone_urls[zone]}bridge"

        # リクエストボディを構築
        request_data = {"Bridge": {"Name": name}}
        if description:
            request_data["Bridge"]["Description"] = description

        return await self.handle_api_request(ctx, HttpMethod.POST, url, request_data)

    async def delete_bridge(
        self, ctx: Context, zone: str, bridge_id: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIでブリッジを削除します

        Args:
            zone (str): 削除対象のゾーン
            bridge_id (str): ブリッジID

        Returns:
            dict: 削除結果のJSONレスポンス
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        # ブリッジIDの検証
        if not bridge_id:
            return "ブリッジIDは必須です。"

        url = f"{self.zone_urls[zone]}bridge/{bridge_id}"
        return await self.handle_api_request(ctx, HttpMethod.DELETE, url)
