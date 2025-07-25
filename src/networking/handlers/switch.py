from typing import Dict, Any, Union, Optional
from mcp.server.fastmcp import Context

from core.auth import SacloudApiKey
from core.handlers.base import BaseHandler, HttpMethod


class SwitchHandler(BaseHandler):
    """スイッチ操作用のハンドラークラス"""

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """スイッチハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、スイッチ操作用のツールを登録。

        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
        """
        super().__init__(mcp, zone_urls, api_key)

        # ツールを登録
        self.mcp.tool(name="get_switch_list")(self.get_switch_list)
        self.mcp.tool(name="create_switch")(self.create_switch)

    async def get_switch_list(
        self, ctx: Context, zone: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからスイッチ一覧を取得します

        Args:
            zone (str): 取得対象のゾーン。

        Returns:
            dict: スイッチ一覧のJSONレスポンス
                - Switches: スイッチのリスト
                    - ID: スイッチID
                    - Name: スイッチ名
                    - Description: 説明
                    - Tags: タグのリスト
                    - Icon: アイコン情報
                    - CreatedAt: 作成日時
                    - ModifiedAt: 更新日時
                    - Scope: スコープ
                    - ServiceClass: サービスクラス
                    - Zone: ゾーン情報
                        - ID: ゾーンID
                        - Name: ゾーン名
                        - Description: ゾーンの説明
                        - Region: リージョン情報
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        url = f"{self.zone_urls[zone]}switch"
        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def create_switch(
        self, ctx: Context, zone: str, name: str, description: Optional[str] = None
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIでスイッチを作成します

        Args:
            zone (str): 作成対象のゾーン
            name (str): スイッチ名（1-64文字）
            description (str, optional): スイッチの説明（最大512文字）

        Returns:
            dict: 作成されたスイッチのJSONレスポンス
                - Switch: 作成されたスイッチ情報
                    - ID: スイッチID
                    - Name: スイッチ名
                    - Description: 説明
                    - Tags: タグのリスト
                    - Icon: アイコン情報
                    - CreatedAt: 作成日時
                    - ModifiedAt: 更新日時
                    - Scope: スコープ
                    - ServiceClass: サービスクラス
                    - Zone: ゾーン情報
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        # スイッチ名の検証
        if not name or len(name) > 64:
            return "スイッチ名は1-64文字で指定する必要があります。"

        # 説明の検証
        if description and len(description) > 512:
            return "説明は最大512文字まで指定できます。"

        url = f"{self.zone_urls[zone]}switch"

        # リクエストボディを構築
        request_data = {"Switch": {"Name": name}}
        if description:
            request_data["Switch"]["Description"] = description

        return await self.handle_api_request(ctx, HttpMethod.POST, url, request_data)
