import httpx
import logging
from mcp.server.fastmcp import Context
from core.auth import SacloudApiKey


class DatabaseHandler: 

    def __init__(
        self,
        mcp,
        zone_urls,
        api_key: SacloudApiKey
    ):
        """データベースハンドラーの初期化
        MCPサーバーのインスタンスを受け取り、データベース操作用のツールを登録。
        Args:
            mcp: MCPサーバーインスタンス
            zone_urls: ゾーンとAPIベースURLのマッピング辞書
        """
        self.mcp = mcp
        self.zone_urls = zone_urls
        self.api_key = api_key
        
        self.mcp.tool(name = 'get_detabases')(self.get_databases)
        
    
    async def get_databases(self, zone: str, ctx: Context) -> any:
        """さくらのクラウドAPIからデータベース一覧を取得します

        Args:
            zone (str): 取得対象のゾーン。

        Returns:
            dict: データベース一覧のJSONレスポンス
        """

         # ゾーンが有効かチェック
        if zone not in self.zone_urls:
            return f"無効なゾーンです。利用可能なゾーン: {', '.join(self.zone_urls.keys())}"
        
        url = f"{self.zone_urls[zone]}appliance"


        try:
            filtered_db = []
            with httpx.Client() as client:
                response = client.get(url, auth=self.api_key)
                data = response.json()
                #アプライアンス一覧からDBのデータのみ取得
                for Appliance in data.get("Appliances", []) :
                    if Appliance.get("Class") == "database":
                        maskd_dbs = self.mask_user_password(Appliance)
                        filtered_db.append( maskd_dbs )
                return filtered_db
            
        except httpx.RequestError as e:
            await ctx.error(f"http Request Error:{e}")
            return f"さくらのクラウドAPIへのリクエストに失敗しました: {e}"
        except httpx.HTTPStatusError as e:
            await ctx.error(f"HTTP Status Error:{e}")
            return f"さくらのクラウドAPIからエラーが返されました: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            await ctx.error(f"Unexpected error:{e}")
            return f"データベース一覧の取得中に予期しないエラーが発生しました: {e}"

    def mask_user_password (self, databases: dict) -> dict:
        """
        Applianceオブジェクト内のUserPassword項目をすべてマスキングする。
        """
        dbs = databases

        try:
            dbs["Settings"]["DBConf"]["Common"]["UserPassword"] = "******"
        except (KeyError, TypeError) as e:
            logging.warning(f"[mask_user_password] Settings側のUserPasswordマスキングに失敗: {e}")

        try:
            dbs["Remark"]["DBConf"]["Common"]["UserPassword"] = "******"
        except (KeyError, TypeError) as e:
            logging.warning(f"[mask_user_password] Remark側のUserPasswordマスキングに失敗: {e}")

        return dbs