from typing import Dict, Any, Union
from mcp.server.fastmcp import Context

from core.auth import SacloudApiKey
from core.handlers.base import BaseHandler, HttpMethod


class ServerHandler(BaseHandler):
    """サーバ操作用のハンドラークラス"""

    MAX_NAME_LENGTH = 61
    MAX_DESCRIPTION_LENGTH = 512
    VALID_GENERATION = [100, 200]

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """サーバハンドラーの初期化
        MCPサーバのインスタンスを受け取り、サーバ操作用のツールを登録

        Args:
            mcp: MCPインスタンスの生成
        """
        super().__init__(mcp, zone_urls, api_key)

        self.mcp.tool(name="get_server_list")(self.get_server_list)
        self.mcp.tool(name="get_server_plan")(self.get_server_plan)
        self.mcp.tool(name="create_server")(self.create_server)
        self.mcp.tool(name="get_server_power_status")(self.get_server_power_status)
        self.mcp.tool(name="stop_server")(self.stop_server)
        self.mcp.tool(name="start_server")(self.start_server)

    async def create_server(
        self,
        zone: str,
        name: str,
        description: str,
        cpu: int,
        mem: int,
        gen: int,
        ctx: Context,
    ) -> any:
        """さくらのクラウドAPIからサーバを作成します
            作成時は、サーバープラン一覧を取得し、CPU,メモリ数を参照しユーザに使用プランを選択させてください
            サーバ作成後、ディスクも作成してください

        Args:
            zone (str): 作成対象ゾーン
            name (str): VM名(1-61文字)
            description (str): VMの説明（最大512文字）
            cpu (int): CPU数
            mem (int): メモリ容量
            gen (int): サーバの世代

        Returns:
            dict: サーバ一覧のJSONレスポンス
        """

        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        # サーバ名の検証
        if not name or len(name) > self.MAX_NAME_LENGTH:
            return f"サーバ名は1-{self.MAX_NAME_LENGTH}文字で指定する必要があります。"

        # 説明の検証
        if description and len(description) > self.MAX_DESCRIPTION_LENGTH:
            return f"説明は最大{self.MAX_DESCRIPTION_LENGTH}文字まで指定できます。"

        # 世代の検証
        if gen not in self.VALID_GENERATION:
            return f"サーバの世代は{' または '.join(map(str, self.VALID_GENERATION))} を指定する必要があります。"

        url = f"{self.zone_urls[zone]}server"

        params = {
            "Server": {
                "Name": name,
                "Description": description,
                "ServerPlan": {
                    "CPU": cpu,
                    "MemoryMB": mem,
                    "Commitment": "standard",
                    "CPUModel": "uncategorized",
                    "Generation": gen,
                },
                "Icon": {},
                "Tags": [],
                "ConnectedSwitches": [{"Scope": "shared"}],
                "InterfaceDriver": "virtio",
            },
            "Count": 0,
        }

        return await self.handle_api_request(ctx, HttpMethod.POST, url, params)

    async def get_server_plan(self, zone: str, ctx: Context) -> any:
        """さくらのクラウドAPIからサーバプラン一覧を取得します"""
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        url = f"{self.zone_urls[zone]}product/server"
        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def get_server_list(
        self, ctx: Context, zone: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからサーバ一覧を取得します

        Args:
            zone (str): 取得対象のゾーン

        Returns:
            dict: サーバ一覧のJSONレスポンス
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        url = f"{self.zone_urls[zone]}server"
        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def get_server_power_status(
        self, ctx: Context, zone: str, server_id: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからサーバーの電源状態を取得します

        Args:
            zone (str): 対象ゾーン
            server_id (str): サーバーID

        Returns:
            dict: 電源状態のJSONレスポンス
                - Instance: 電源状態情報
                    - Server: サーバー情報
                        - ID: サーバーID
                    - Status: 現在の電源状態 ("up" または "down")
                    - BeforeStatus: 以前の電源状態
                    - StatusChangedAt: 状態変更日時
                - is_ok: 処理結果
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        # サーバーIDの検証
        if not server_id:
            return "サーバーIDは必須です。"

        url = f"{self.zone_urls[zone]}server/{server_id}/power"
        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def stop_server(
        self, ctx: Context, zone: str, server_id: str, force: bool = False
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIでサーバーを停止します

        Args:
            zone (str): 対象ゾーン
            server_id (str): サーバーID
            force (bool, optional): 強制停止フラグ（デフォルト: False）

        Returns:
            dict: 停止処理のJSONレスポンス
                - Instance: 電源状態情報
                    - Server: サーバー情報
                        - ID: サーバーID
                    - Status: 処理後の電源状態
                    - BeforeStatus: 処理前の電源状態
                    - StatusChangedAt: 状態変更日時
                - is_ok: 処理結果
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        # サーバーIDの検証
        if not server_id:
            return "サーバーIDは必須です。"

        url = f"{self.zone_urls[zone]}server/{server_id}/power"

        # リクエストボディを構築
        request_data = {}
        if force:
            request_data["Force"] = True

        return await self.handle_api_request(
            ctx, HttpMethod.DELETE, url, request_data if request_data else None
        )

    async def start_server(
        self, ctx: Context, zone: str, server_id: str
    ) -> Union[Dict[str, Any], str]:
        """
        さくらのクラウドAPIでサーバーを起動します
        サーバの起動には時間がかかるため、リクエストがタイムアウトする場合があります

        Args:
            zone (str): 対象ゾーン
            server_id (str): サーバーID

        Returns:
            dict: 起動処理のJSONレスポンス
                - Instance: 電源状態情報
                    - Server: サーバー情報
                        - ID: サーバーID
                    - Status: 処理後の電源状態
                    - BeforeStatus: 処理前の電源状態
                    - StatusChangedAt: 状態変更日時
                - is_ok: 処理結果
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        # サーバーIDの検証
        if not server_id:
            return "サーバーIDは必須です。"

        url = f"{self.zone_urls[zone]}server/{server_id}/power"
        return await self.handle_api_request(ctx, HttpMethod.PUT, url)
