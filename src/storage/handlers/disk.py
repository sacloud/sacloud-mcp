from typing import Dict, Any, Union
from mcp.server.fastmcp import Context

from core.auth import SacloudApiKey
from core.handlers.base import BaseHandler, HttpMethod


class DiskHandler(BaseHandler):
    """ディスク操作用のハンドラークラス"""

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """ディスクハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、ディスク操作用のツールを登録。
        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
        """
        super().__init__(mcp, zone_urls, api_key)

        self.mcp.tool(name="get_disk")(self.get_disk)
        self.mcp.tool(name="create_disk")(self.create_disk)
        self.mcp.tool(name="get_disk_plan")(self.get_disk_plan)

    async def get_disk(
        self, ctx: Context, zone: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからディスク一覧を取得します。

        Args:
            zone (str): 取得対象のゾーン。

        Returns:
            dict: ディスク一覧のJSONレスポンス
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        url = f"{self.zone_urls[zone]}disk"

        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def get_disk_plan(self, zone: str, ctx: Context) -> any:
        """さくらのクラウドAPIからディスクプラン一覧を取得します"""
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        url = f"{self.zone_urls[zone]}product/disk"

        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def create_disk(
        self,
        zone: str,
        name: str,
        description: str,
        plan: str,
        size_mb: int,
        source_archive_id: int,
        server_id: str,
        ctx: Context,
    ) -> any:
        """さくらのクラウドAPIでディスクを作成して、サーバーに接続します。
        作成時は、ディスクプラン一覧を取得し、使用可能なプランとディスク容量を参照しユーザに選択させてください
        アーカイブIDはアーカイブ一覧から取得してください

        Args:
            zone (str): 作成対象のゾーン
            name (str): ディスク名（1-64文字）
            description (str, optional): ルータの説明（最大512文字）
            plan (int): 標準プランは4、SSDプランは2
            size_mb (int): ディスクに割り当てる容量(例:20480(20GB))
            source_archive_id (str): アーカイブのID
            server_id (str): 紐付けるサーバ
            bandwidth_mbps (int): 帯域幅（100、500、または1000 Mbps）


        Returns:
            dict: 作成されたディスクのJSONレスポンス

        """

        url = f"{self.zone_urls[zone]}disk"

        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        params = {
            "Disk": {
                "Name": name,
                "Description": description,
                "Plan": {"ID": plan},
                "SizeMB": size_mb,
                "Connection": "virtio",
                "SourceArchive": {"ID": source_archive_id},
                "Server": {"ID": server_id},
            }
        }
        return await self.handle_api_request(ctx, HttpMethod.POST, url, params)
