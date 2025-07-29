from typing import Dict, Any, Union, Optional
from mcp.server.fastmcp import Context

from core.auth import SacloudApiKey
from core.handlers.base import BaseHandler, HttpMethod


class InterfaceHandler(BaseHandler):
    """ネットワークインターフェース操作用のハンドラークラス"""

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """インターフェースハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、インターフェース操作用のツールを登録。

        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
            api_key: さくらのクラウドAPIキー
        """
        super().__init__(mcp, zone_urls, api_key)

        # ツールを登録
        self.mcp.tool(name="get_interface_list")(self.get_interface_list)
        self.mcp.tool(name="get_packet_filter_list")(self.get_packet_filter_list)

    ### MCPツールメソッド

    async def get_interface_list(
        self, ctx: Context, zone: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからネットワークインターフェース一覧を取得します

        Args:
            zone (str): 取得対象のゾーン

        Returns:
            dict: インターフェース一覧のJSONレスポンス
                - Interfaces: インターフェース情報のリスト
                    - ID: インターフェースID
                    - MACAddress: MACアドレス
                    - IPAddress: IPアドレス
                    - UserIPAddress: ユーザーIPアドレス
                    - HostName: ホスト名
                    - Switch: 接続されているスイッチ情報
                        - ID: スイッチID
                        - Name: スイッチ名
                        - Scope: スコープ
                    - Server: 所属サーバー情報
                        - ID: サーバーID
                        - Name: サーバー名
                    - PacketFilter: パケットフィルタ情報
                        - ID: パケットフィルタID
                        - Name: パケットフィルタ名
                    - CreatedAt: 作成日時
                    - ModifiedAt: 更新日時
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        url = f"{self.zone_urls[zone]}interface"
        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def get_packet_filter_list(
        self, ctx: Context, zone: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからパケットフィルタ一覧を取得します

        Args:
            zone (str): 取得対象のゾーン

        Returns:
            dict: パケットフィルタ一覧のJSONレスポンス
                - PacketFilters: パケットフィルタ情報のリスト
                    - ID: パケットフィルタID
                    - Name: パケットフィルタ名
                    - Description: 説明
                    - RequiredHostVersion: 必要ホストバージョン
                    - Expression: フィルタ式
                    - CreatedAt: 作成日時
                    - ModifiedAt: 更新日時
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        url = f"{self.zone_urls[zone]}packetfilter"
        return await self.handle_api_request(ctx, HttpMethod.GET, url)
