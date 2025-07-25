from typing import Dict, Any, Union
from mcp.server.fastmcp import Context
from core.auth import SacloudApiKey
from core.handlers.base import BaseHandler, HttpMethod


class ArchiveHandler(BaseHandler):
    """アーカイブ操作用のハンドラークラス"""

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """アーカイブハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、アーカイブ操作用のツールを登録。

        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
        """
        super().__init__(mcp, zone_urls, api_key)

        # ツールを登録
        self.mcp.tool(name="get_archive_list")(self.get_archive_list)

    async def get_archive_list(
        self, ctx: Context, zone: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIからアーカイブ一覧を取得します

        Args:
            zone (str): 取得対象のゾーン

        Returns:
            dict: アーカイブ一覧のJSONレスポンス
        """
        # 前処理（ゾーン検証 + 認証チェック）
        error = self.validate_request_context(zone)
        if error:
            return error

        url = f"{self.zone_urls[zone]}archive"

        response = await self.handle_api_request(ctx, HttpMethod.GET, url)
        # レスポンスが文字列の場合はそのまま返す（エラーメッセージなど）
        if isinstance(response, str):
            return response

        filtered_archives = []
        for item in response["Archives"]:
            filtered_archives.append({"Name": item["Name"], "ID": item["ID"]})
        return filtered_archives
