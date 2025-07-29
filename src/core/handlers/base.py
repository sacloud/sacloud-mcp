import httpx
from enum import Enum
from typing import Dict, Any, Union, Optional
from mcp.server.fastmcp import Context

from core.auth import SacloudApiKey, check_auth, get_http_client
from core.zone import validate_zone


class HttpMethod(Enum):
    """HTTPメソッドの定数定義"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class BaseHandler:
    """全ハンドラーの基底クラス - 共通処理を提供"""

    def __init__(self, mcp, zone_urls, api_key: SacloudApiKey):
        """基底ハンドラーの初期化

        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
            api_key: さくらのクラウドAPIキー
        """
        self.mcp = mcp
        self.zone_urls = zone_urls
        self.api_key = api_key

    def validate_request_context(self, zone: str) -> Optional[str]:
        """リクエストの前処理（ゾーン検証 + 認証チェック）

        Args:
            zone (str): 対象ゾーン

        Returns:
            Optional[str]: エラーメッセージ（成功時はNone）
        """
        # ゾーンが有効かチェック
        zone_error = validate_zone(zone)
        if zone_error:
            return zone_error

        # 認証情報チェック
        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error

        return None

    async def handle_api_request(
        self,
        ctx: Context,
        method: HttpMethod,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], str]:
        """API リクエストの統一処理

        Args:
            ctx: MCPコンテキスト
            method: HTTPメソッド (HttpMethod enum)
            url: リクエストURL
            json_data: JSONリクエストボディ（POSTやPUT時）
            params: クエリパラメータ

        Returns:
            Union[Dict[str, Any], str]: APIレスポンスまたはエラーメッセージ
        """
        try:
            with get_http_client(self.api_key) as client:
                if method == HttpMethod.GET:
                    response = client.get(url, params=params)
                elif method == HttpMethod.POST:
                    response = client.post(url, json=json_data, params=params)
                elif method == HttpMethod.PUT:
                    response = client.put(url, json=json_data, params=params)
                elif method == HttpMethod.DELETE:
                    if json_data:
                        # 例外的にDELETEメソッドでJSONボディを送信する場合がある
                        response = client.request(
                            "DELETE", url, json=json_data, params=params
                        )
                    else:
                        response = client.delete(url, params=params)
                else:
                    return f"サポートされていないHTTPメソッドです: {method.value}"

                response.raise_for_status()
                return response.json()

        except httpx.RequestError as e:
            await ctx.error(f"http Request Error:{e}")
            return f"さくらのクラウドAPIへのリクエストに失敗しました: {e}"
        except httpx.HTTPStatusError as e:
            await ctx.error(f"HTTP Status Error:{e}")
            return f"さくらのクラウドAPIからエラーが返されました: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            await ctx.error(f"Unexpected error:{e}")
            return f"API リクエスト中に予期しないエラーが発生しました: {e}"
