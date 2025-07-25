import httpx
from mcp.server.fastmcp import Context
from core.auth import SacloudApiKey
from typing import Optional

from core.zone import validate_zone
from core.auth import SacloudApiKey, check_auth, get_http_client


class VpnRouterHandler: 

    def __init__(
        self,
        mcp,
        zone_urls,
        api_key: SacloudApiKey
    ):
        """VPNルーターハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、VPNルータ操作用のツールを登録。
        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
        """
        self.mcp = mcp
        self.zone_urls = zone_urls
        self.api_key = api_key
        
        self.mcp.tool(name = 'get_vpn_router_list')(self.get_vpn_router_list)
        self.mcp.tool(name = 'get_vpn_monitor')(self.get_vpn_monitor)
    
    async def get_vpn_router_list(
        self, 
        zone: str, 
        ctx: Context
    ) -> any:
        """さくらのクラウドAPIからVPNルータ一覧を取得します

        Args:
            zone (str): 取得対象のゾーン。

        Returns:
            dict: VPNルータ一覧のJSONレスポンス
        """

         # ゾーンが有効かチェック
        zone_error = validate_zone(zone)
        if zone_error:
            return zone_error
        
        url = f"{self.zone_urls[zone]}appliance"

        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error
        try:
            filtered_vpn_router = []
            with get_http_client(self.api_key) as client:
                response = client.get(url)
                data = response.json()
                #アプライアンス一覧からVPNルータのデータのみ取得
                for appliance in data.get("Appliances", []) :
                    if appliance.get("Class") in ("vpcrouter", "vpnrouter"):
                        filtered_vpn_router.append( appliance )
                return filtered_vpn_router
            
        except httpx.RequestError as e:
            await ctx.error(f"http Request Error:{e}")
            return f"さくらのクラウドAPIへのリクエストに失敗しました: {e}"
        except httpx.HTTPStatusError as e:
            await ctx.error(f"HTTP Status Error:{e}")
            return f"さくらのクラウドAPIからエラーが返されました: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            await ctx.error(f"Unexpected error:{e}")
            return f"データベース一覧の取得中に予期しないエラーが発生しました: {e}"


    async def get_vpn_monitor(
        self, 
        zone: str, 
        vpn_id: str,
        ctx: Context,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> any:

        """さくらのクラウドAPIからVPNルータ一のネットワーク流量のリソースモニタ情報を取得します

        Args:
            zone (str): 取得対象のゾーン。
            vpn_id (str): vpnルータのリソースID
            start (str, optional): 開始時刻（ISO形式、デフォルトは終了時刻の24時間前）
            end (str, optional): 終了時刻（ISO形式、デフォルトは開始時刻の24時間後）


        Returns:
            dict: VPNルータ一覧のJSONレスポンス
        """

        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error
        
         # ゾーンが有効かチェック
        zone_error = validate_zone(zone)
        if zone_error:
            return zone_error
        
        url = f"{self.zone_urls[zone]}appliance/{vpn_id}/interface/monitor"

        params = {}
        if start:
            params["Start"] = start
        if end:
            params["End"] = end

        
        try:
            with get_http_client(self.api_key) as client:
                response = client.get(url, params=params)
                return response.json()
            
        except httpx.RequestError as e:
            await ctx.error(f"http Request Error:{e}")
            return f"さくらのクラウドAPIへのリクエストに失敗しました: {e}"
        except httpx.HTTPStatusError as e:
            await ctx.error(f"HTTP Status Error:{e}")
            return f"さくらのクラウドAPIからエラーが返されました: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            await ctx.error(f"Unexpected error:{e}")
            return f"データベース一覧の取得中に予期しないエラーが発生しました: {e}"
        