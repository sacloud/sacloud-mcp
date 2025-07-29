from typing import Dict, Any, Union, Optional
from mcp.server.fastmcp import Context

from core.auth import SacloudApiKey, check_auth
from core.handlers.base import BaseHandler, HttpMethod


class BillHandler(BaseHandler):
    """請求書操作用のハンドラークラス"""

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """請求書ハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、請求書操作用のツールを登録。

        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
            api_key: さくらのクラウドAPIキー
        """
        super().__init__(mcp, zone_urls, api_key)

        # ツールを登録
        self.mcp.tool(name="get_bill_list")(self.get_bill_list)
        self.mcp.tool(name="get_bill_list_by_month")(self.get_bill_list_by_month)
        self.mcp.tool(name="get_coupon_list")(self.get_coupon_list)

    ### MCPツールメソッド

    async def get_bill_list(
        self, ctx: Context, account_id: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIから指定プロジェクトIDの請求一覧を取得します

        Args:
            account_id (str): プロジェクトID（アカウントID）

        Returns:
            dict: 請求一覧のJSONレスポンス
                - is_ok: 処理結果
                - Count: 件数
                - ResponsedAt: レスポンス時刻
                - Bills: 請求書情報のリスト
        """
        # アカウントIDの検証
        if not account_id:
            return "アカウントIDは必須です。"

        # 認証情報チェック
        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error

        # 請求書APIは特定のゾーンに依存しないため、最初のゾーンを使用
        first_zone_url = next(iter(self.zone_urls.values()), None)
        # システムAPIのエンドポイントに変更
        base_url = first_zone_url.replace("/api/cloud/1.1/", "/api/system/1.0/")
        url = f"{base_url}bill/by-contract/{account_id}"

        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def get_bill_list_by_month(
        self, ctx: Context, account_id: str, year: str, month: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIから指定プロジェクトIDの特定年月の請求一覧を取得します

        Args:
            account_id (str): プロジェクトID（アカウントID）
            year (str): 年（YYYY形式）
            month (str): 月（MM形式）

        Returns:
            dict: 特定年月の請求一覧のJSONレスポンス
                - is_ok: 処理結果
                - Count: 件数
                - ResponsedAt: レスポンス時刻
                - Bills: 請求書情報のリスト
        """
        # パラメータの検証
        if not account_id:
            return "アカウントIDは必須です。"

        if not year:
            return "年は必須です。"

        if not month:
            return "月は必須です。"

        # 年の形式チェック（YYYY形式）
        if not year.isdigit() or len(year) != 4:
            return "年はYYYY形式（4桁の数字）で指定してください。"

        # 月の形式チェック（MM形式）
        if not month.isdigit() or len(month) != 2 or not (1 <= int(month) <= 12):
            return "月はMM形式（01-12）で指定してください。"

        # 認証情報チェック
        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error

        # 請求書APIは特定のゾーンに依存しないため、最初のゾーンを使用
        first_zone_url = next(iter(self.zone_urls.values()), None)
        # システムAPIのエンドポイントに変更
        base_url = first_zone_url.replace("/api/cloud/1.1/", "/api/system/1.0/")
        url = f"{base_url}bill/by-contract/{account_id}/{year}/{month}"

        return await self.handle_api_request(ctx, HttpMethod.GET, url)

    async def get_coupon_list(
        self, ctx: Context, account_id: str
    ) -> Union[Dict[str, Any], str]:
        """さくらのクラウドAPIから指定プロジェクトIDのクーポン一覧を取得します

        Args:
            account_id (str): プロジェクトID（アカウントID）

        Returns:
            dict: クーポン一覧のJSONレスポンス
                - is_ok: 処理結果
                - Count: 件数
                - ResponsedAt: レスポンス時刻
                - Coupons: クーポン情報のリスト
        """
        # アカウントIDの検証
        if not account_id:
            return "アカウントIDは必須です。"

        # 認証情報チェック
        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error

        # クーポンAPIは特定のゾーンに依存しないため、最初のゾーンを使用
        first_zone_url = next(iter(self.zone_urls.values()), None)
        # システムAPIのエンドポイントに変更
        base_url = first_zone_url.replace("/api/cloud/1.1/", "/api/system/1.0/")
        url = f"{base_url}coupon/{account_id}"

        return await self.handle_api_request(ctx, HttpMethod.GET, url)
