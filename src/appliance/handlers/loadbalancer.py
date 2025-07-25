import httpx
from mcp.server.fastmcp import Context
from core.auth import SacloudApiKey

from core.zone import validate_zone
from core.auth import SacloudApiKey, check_auth

class LoadbalancerHandler: 

    def __init__(
        self,
        mcp,
        zone_urls,
        api_key: SacloudApiKey
    ):
        """ロードバランサハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、ロードバランサ操作用のツールを登録。
        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
        """
        self.mcp = mcp
        self.zone_urls = zone_urls
        self.api_key = api_key
        
        self.mcp.tool(name = 'get_loadbalancer')(self.get_loadbalancer_list)
        self.mcp.tool(name = 'create_loadbalancer')(self.create_loadbalancer)
        self.mcp.tool(name = 'attach_servers')(self.attach_servers)

    
    async def get_loadbalancer_list(self, zone: str, ctx: Context) -> any:
        """さくらのクラウドAPIからロードバランサ一覧を取得します

        Args:
            zone (str): 取得対象のゾーン。

        Returns:
            dict: ロードバランサ一覧のJSONレスポンス
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
            filtered_lb = []
            with httpx.Client() as client:
                response = client.get(url, auth=self.api_key)
                data = response.json()
                #アプライアンス一覧からLBのデータのみ取得
                for appliance in data.get("Appliances", []) :
                    if appliance.get("Class") == "loadbalancer":
                        filtered_lb.append( appliance )
                return filtered_lb
            
        except httpx.RequestError as e:
            await ctx.error(f"http Request Error:{e}")
            return f"さくらのクラウドAPIへのリクエストに失敗しました: {e}"
        except httpx.HTTPStatusError as e:
            await ctx.error(f"HTTP Status Error:{e}")
            return f"さくらのクラウドAPIからエラーが返されました: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            await ctx.error(f"Unexpected error:{e}")
            return f"データベース一覧の取得中に予期しないエラーが発生しました: {e}"
        
        
    async def create_loadbalancer (self, zone, name, description, lb_ip, switch_id, vrid, netwrok_mask, default_router, ctx: Context) -> any:
        """さくらのクラウドAPIでロードバランサを作成します
        Args:
            zone (str): 作成対象のゾーン
            name (str): ロードバランサ名（1-64文字）
            description (str, optional): ルータの説明（最大512文字）
            lb_ip (str) ロードバランサに付与されるip address
            switch_id (str): 紐付けるスイッチのID
            vrid (str): (1から255)
            network_mask (str): プレフィックス長（8~29）
            default_router(str, optional) ゲートウェイ
            
            
            
        Returns:
            dict: 作成されたロードバランサのJSONレスポンス
                
        """

        # ゾーンが有効かチェック
        zone_error = validate_zone(zone)
        if zone_error:
            return zone_error
        
        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error
        
        url = f"{self.zone_urls[zone]}appliance"

        params = {
            "Appliance": {
                "Class": "loadbalancer",
                "Name": name,
                "Description": description,
                "Plan": {
                    "ID": "1"
                },
                "Settings": {
                    "LoadBalancer": []
                },
                "Remark": {
                    "Switch": {"ID": switch_id},
                    "VRRP": {"VRID": vrid},
                    "Network": {
                        "NetworkMaskLen": netwrok_mask,
                        "DefaultRoute": default_router
                    },
                    "Servers":[
                        {"IPAddress": lb_ip}
                    ]
                },
        
            }
        }

        try:
            with httpx.Client() as client:
                response = client.post(url, auth=self.api_key, json=params)
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
            return f"データベース一覧の取得中に予期しないエラーが発生しました: {e}"
    

    async def attach_servers ( self,
        zone: str,
        lb_id: str,
        vip: str,
        server_ips: list[str],
        ctx: Context
    ) -> any:
        """さくらのクラウドAPIでロードバランサを作成します
        Args:
            zone (str): 作成対象のゾーン
            lb_id (str): LBのID
            vip  (str): 仮想ipアドレス
            server_ips (list[str]): 関連づけるサーバのIP
            
        Returns:
            dict: 作成されたロードバランサのJSONレスポンス
                
        """

        # ゾーンが有効かチェック
        zone_error = validate_zone(zone)
        if zone_error:
            return zone_error
        
        #認証情報が有効かチェック
        auth_error = check_auth(self.api_key)
        if auth_error:
            return auth_error
        
        setting_url = f"{self.zone_urls[zone]}appliance/{lb_id}"
        update_url = f"{self.zone_urls[zone]}appliance/{lb_id}/config"

        servers = [
            {
                "IPAddress": ip,
                "Port": "80",
                "HealthCheck": {
                    "Protocol": "ping"
                },
                "Enabled": "True"
            }
            for ip in server_ips
        ]

        params = {
            "Appliance": {
                "Settings": {
                    "LoadBalancer": [
                        {
                            "VirtualIPAddress": vip,
                            "Port": "80",
                            "DelayLoop": "120",
                            "Servers": servers
                        }
                    ]
                },
            }
        }

        try:
            with httpx.Client() as client:
                response = client.put(setting_url, auth=self.api_key, json=params)
                response.raise_for_status()
                #設定の有効化
                response = client.put(update_url, auth=self.api_key)
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
            return f"データベース一覧の取得中に予期しないエラーが発生しました: {e}"
