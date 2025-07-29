import httpx
from core.auth import SacloudApiKey,ObjectStorageApiKey,check_auth,check_objectstorage_auth
from mcp.server.fastmcp import Context
import os
import boto3
from botocore.config import Config

class ObjectStorageHandler:
        """オブジェクトストレージ操作用のハンドラークラス"""

        def __init__(
            self,
            mcp,
            objectstorage_zone_urls,
            api_key: SacloudApiKey,
            objectstorage_api_key: ObjectStorageApiKey
        ):
            """オブジェクトストレージハンドラーの初期化
            MCPサーバのインスタンスを受け取り、スイッチ操作用のツールを登録。

            Args:
                mcp: MCPサーバインスタンス
            """
            self.mcp = mcp
            self.objectstorage_zone_urls = objectstorage_zone_urls
            self.api_key = api_key
            self.objectstorage_api_key = objectstorage_api_key


            # ツールを登録
            self.mcp.tool(name='get_objectstorage_site_list')(self.get_objectstorage_site_list)
            self.mcp.tool(name='get_objectstorage_accesskey_list')(self.get_objectstorage_accesskey_list)
            self.mcp.tool(name='get_objectstorage_bucket_list')(self.get_objectstorage_bucket_list)

        async def get_objectstorage_site_list(self,ctx:Context):
            """さくらのクラウドAPIからオブジェクトストレージのサイト一覧を取得します。

            Returns:
            dict: サイト一覧のJSONレスポンス
                - data: サイトのリスト
                    - api_zone: APIゾーンのリスト
                    - control_panel_url: コントロールパネルURL
                    - display_name_en_us: 英語表示名
                    - display_name_ja: 日本語表示名  
                    - display_name: 表示名
                    - display_order: 表示順序
                    - endpoint_base: エンドポイントベース
                    - iam_endpoint: IAMエンドポイント
                    - iam_endpoint_for_control_panel: コントロールパネル用IAMエンドポイント
                    - id: サイトID
                    - region: リージョン
                    - s3_endpoint: S3エンドポイント
                    - s3_endpoint_for_control_panel: コントロールパネル用S3エンドポイント
                    - storage_zone: ストレージゾーンのリスト
            """
            # ゾーンが有効かチェック
            # 現在オブジェクトストレージはis1aにしか存在しない
            zone = "is1a"

            url = f"{self.objectstorage_zone_urls[zone]}fed/v1/clusters"

            auth_error = check_auth(self.api_key)
            if auth_error:
                return auth_error
  
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url,auth=self.api_key)
                    response.raise_for_status()
                    return response.json()
                
            except httpx.RequestError as e:
                await ctx.error(f"HTTP Request Error:{e}")
                return f"さくらのクラウドAPIへのリクエストに失敗しました: {e}"
            except httpx.HTTPStatusError as e:
                await ctx.error(f"HTTP Status Error:{e.response.status_code} - {e.response.text}")
                return f"さくらのクラウドAPIからエラーが返されました: {e.response.status_code} - {e.response.text}"
            except Exception as e:
                await ctx.error(f"Unexpected error:{e}")
                return f"オブジェクトストレージのサイト一覧の取得中に予期しないエラーが発生しました: {e}"

        async def get_objectstorage_accesskey_list(self,ctx:Context,site_id:str):
            """さくらのクラウドAPIからオブジェクトストレージのアクセスキー一覧を取得します。

            Returns:
                dict: アクセスキー一覧のJSONレスポンス
                    - data: アクセスキーのリスト
                        - id: アクセスキーID（文字列、例："abcdefABCDEF0123456789"）
                        - secret: シークレットアクセスキー（文字列、作成時のみ返却される）
                        - created_at: 作成日時（ISO8601形式、例："2020-01-11T01:11:23.123456+09:00"）
            """
            # 現在オブジェクトストレージはis1aにしか存在しない
            zone = "is1a"
            
            url = f"{self.objectstorage_zone_urls[zone]}{site_id}/v2/account/keys"

            auth_error = check_auth(self.api_key)
            if auth_error:
                return auth_error
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url,auth=self.api_key)
                    response.raise_for_status()
                    return response.json()
                
            except httpx.RequestError as e:
                await ctx.error(f"HTTP Request Error:{e}")
                return f"さくらのクラウドAPIへのリクエストに失敗しました: {e}"
            except httpx.HTTPStatusError as e:
                await ctx.error(f"HTTP Status Error:{e.response.status_code} - {e.response.text}")
                return f"さくらのクラウドAPIからエラーが返されました: {e.response.status_code} - {e.response.text}"
            except Exception as e:
                await ctx.error(f"Unexpected error:{e}")
                return f"オブジェクトストレージのアクセスキー一覧の取得中に予期しないエラーが発生しました: {e}"
            
        async def get_objectstorage_bucket_list(self,ctx:Context):
            """さくらのクラウドAPIからオブジェクトストレージのバケット一覧を取得します。

            Returns:
                - Name: バケット名
                  CreationDate: 作成日時
            """
            zone = "s3is1a"
            auth_error = check_objectstorage_auth(self.objectstorage_api_key)
            if auth_error:
                return auth_error
            
            endpoint = f"{self.objectstorage_zone_urls[zone]}"
            config = Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'}
            )
            
            s3 = boto3.client(
                's3',
                endpoint_url=endpoint,
                aws_access_key_id=self.objectstorage_api_key[0],
                aws_secret_access_key=self.objectstorage_api_key[1],
                config=config,
                region_name='jp-north-1'
            )
            try:
                resp = s3.list_buckets()
                return resp

            except Exception as e:
                await ctx.error(f"get objectstorage failed:{e}")
                return f"オブジェクトストレージのバケット一覧取得に失敗しました。{e}"