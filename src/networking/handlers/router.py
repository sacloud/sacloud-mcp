from typing import Dict, Any, Optional, Union
from mcp.server.fastmcp import Context

from core.auth import SacloudApiKey
from core.handlers.base import BaseHandler, HttpMethod


class RouterHandler(BaseHandler):
    """ルータ操作用のハンドラークラス"""

    # 定数定義
    MAX_NAME_LENGTH = 64
    MAX_DESCRIPTION_LENGTH = 512
    VALID_NETWORK_MASK_LENGTHS = [27, 28]
    VALID_BANDWIDTH_MBPS = [100, 500, 1000]

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """ルータハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、ルータ操作用のツールを登録。

        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
        """
        super().__init__(mcp, zone_urls, api_key)

        # ツールを登録
        self.mcp.tool(name="get_router_list")(self.get_router_list)
        self.mcp.tool(name="get_router_monitor")(self.get_router_monitor)
        self.mcp.tool(name="create_router")(self.create_router)
        self.mcp.tool(name="delete_router")(self.delete_router)

    ### MCPツールメソッド

    async def get_router_list(
        self, ctx: Context, zone: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからルータ一覧を取得します

        Args:
            zone (str): 取得対象のゾーン

        Returns:
            dict: ルータ一覧のJSONレスポンス
                - Internet: ルータのリスト
                    - ID: ルータID
                    - Name: ルータ名
                    - Description: 説明
                    - BandWidthMbps: 帯域幅
                    - NetworkMaskLen: プレフィックス長
                    - Scope: スコープ
                    - ServiceClass: サービスクラス
                    - CreatedAt: 作成日時
                    - Zone: ゾーン情報
                    - Subnets: サブネット情報
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        url = f"{self.zone_urls[zone]}internet"
        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def create_router(
        self,
        ctx: Context,
        zone: str,
        name: str,
        network_mask_len: int,
        bandwidth_mbps: int,
        description: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIでルータを作成します

        Args:
            zone (str): 作成対象のゾーン
            name (str): ルータ名（1-64文字）
            network_mask_len (int): プレフィックス長（28または27）
            bandwidth_mbps (int): 帯域幅（100、500、または1000 Mbps）
            description (str, optional): ルータの説明（最大512文字）

        Returns:
            dict: 作成されたルータのJSONレスポンス
                - Internet: 作成されたルータ情報
                    - ID: ルータID
                    - Name: ルータ名
                    - Description: 説明
                    - BandWidthMbps: 帯域幅
                    - NetworkMaskLen: プレフィックス長
                    - Scope: スコープ
                    - ServiceClass: サービスクラス
                    - CreatedAt: 作成日時
                    - Zone: ゾーン情報
                    - Subnets: サブネット情報
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        # ルータ名の検証
        if not name or len(name) > self.MAX_NAME_LENGTH:
            return f"ルータ名は1-{self.MAX_NAME_LENGTH}文字で指定する必要があります。"

        # プレフィックス長の検証
        if network_mask_len not in self.VALID_NETWORK_MASK_LENGTHS:
            return f"プレフィックス長は{' または '.join(map(str, self.VALID_NETWORK_MASK_LENGTHS))}を指定する必要があります。"

        # 帯域幅の検証
        if bandwidth_mbps not in self.VALID_BANDWIDTH_MBPS:
            return f"帯域幅は{' または '.join(map(str, self.VALID_BANDWIDTH_MBPS))} Mbpsを指定する必要があります。"

        # 説明の検証
        if description and len(description) > self.MAX_DESCRIPTION_LENGTH:
            return f"説明は最大{self.MAX_DESCRIPTION_LENGTH}文字まで指定できます。"

        url = f"{self.zone_urls[zone]}internet"

        # リクエストボディを構築
        request_data = {
            "Internet": {
                "Name": name,
                "NetworkMaskLen": network_mask_len,
                "BandWidthMbps": bandwidth_mbps,
            }
        }
        if description:
            request_data["Internet"]["Description"] = description

        return await self.handle_api_request(ctx, HttpMethod.POST, url, request_data)

    async def get_router_monitor(
        self,
        ctx: Context,
        zone: str,
        internet_id: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからルータのネットワーク流量のリソースモニタ情報を取得します

        Args:
            zone (str): 取得対象のゾーン
            internet_id (str): ルータID
            start (str, optional): 開始時刻（ISO形式、デフォルトは終了時刻の24時間前）
            end (str, optional): 終了時刻（ISO形式、デフォルトは開始時刻の24時間後）

        Returns:
            dict: ルータの監視データのJSONレスポンス
                - 監視データの詳細構造はAPIから返される形式に依存
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        # ルータIDの検証
        if not internet_id:
            return "ルータIDは必須です。"

        url = f"{self.zone_urls[zone]}internet/{internet_id}/monitor"

        # クエリパラメータを構築
        params = {}
        if start:
            params["Start"] = start
        if end:
            params["End"] = end

        return await self.handle_api_request(ctx, HttpMethod.GET, url, params=params)

    async def delete_router(
        self, ctx: Context, zone: str, internet_id: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIでルータを削除します

        Args:
            zone (str): 削除対象のゾーン
            internet_id (str): ルータID

        Returns:
            Union[Dict[str, Any], str]: 削除結果のJSONレスポンスまたはエラーメッセージ
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        # ルータIDの検証
        if not internet_id:
            return "ルータIDは必須です。"

        url = f"{self.zone_urls[zone]}internet/{internet_id}"
        return await self.handle_api_request(ctx, HttpMethod.DELETE, url)
