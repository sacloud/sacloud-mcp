from bs4 import BeautifulSoup
import asyncio
from mcp.server.fastmcp import Context
import httpx
from html_to_markdown import convert_to_markdown
import json

class DocumentsHandler:
    """ドキュメントのMCPサーバハンドラ"""
    def __init__(
        self,
        mcp,
    ):
        self.manual_outlines = None
        self.mcp = mcp

        # MCPサーバのツール登録
        self.mcp.tool(name='get_manual_outline')(self.get_manual_outline)
        self.mcp.tool(name='read_manual')(self.read_manual)
        self.mcp.tool(name='get_price')(self.get_price)

    # さくらのマニュアルのサイドバーのリンクを取得し、再帰的にアクセス
            

    async def get_manual_outline(self,ctx: Context):
        """
        さくらのクラウドの使い方のマニュアルの目次を項目名と対応するurlを辞書型で返します。
        Returns:
            dict:  さくらのクラウドのマニュアルの目次
                - 目次名(dict):
                    - url(str):
                    - 目次名(dict):
                        - url
                        ....     
        """
        try:
            with open("./docs/materials/outline.json") as f:
                contents = json.load(f)
            return contents
        except Exception as e:
            ctx.error(f"can't open file: {e}")
            return f"ファイルが開けませんでした。: {e}"
        
    # mainを抜き出して、htmlからmarkdownに変更する
    def reformat_manual_page(self,html:str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        main_html =  soup.find(attrs={'role': 'main'})
        if not main_html:
            return None
        main_markdown = convert_to_markdown(main_html)
        return main_markdown
    
    async def read_manual(self,ctx:Context,url:str):
        """
            指定したさくらのクラウドのマニュアル(https://manual.sakura.ad.jp/cloud/~)のurlを受け取り、markdownに変換し、主要の内容を取得します。
            Args:
                url (str): さくらのクラウドのマニュアルのurl
            Returns:
                str: さくらのクラウドのマニュアルの内容
        """
        if not url.startswith('https://manual.sakura.ad.jp/cloud/'):
            return 'さくらのクラウドのマニュアルのurlではないので、有効なurlを指定してください'
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
            content = self.reformat_manual_page(response.text)
            if not content:
                await ctx.error(f"Failed Get Http Contents")
                return 'error:urlをフォーマットできなかった'
            return content
        except httpx.RequestError as e:
            await ctx.error(f"HTTP Request Error:{e}")
            return f"さくらのクラウドのマニュアルへのリクエストに失敗しました: {e}"
        except httpx.HTTPStatusError as e:
            await ctx.error(f"HTTP Status Error: {e.response.status_code} - {e.response.text}")
            return f"さくらのクラウドのマニュアルからエラーが返されました: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            await ctx.error(f"Unexpected error:{e}")
            return  f"さくらのクラウドのマニュアルの内容取得で予期しないエラーが発生しました: {e}" 
    async def get_price(self,ctx:Context):
        """
        さくらのクラウドの利用料金を取得します。
        Returns:
            dict: さくらのクラウドの利用料金情報
                - Count (int): 取得したサービスクラスの総数
                - ResponsedAt (str): レスポンス生成日時（ISO 8601 形式）
                - ServiceClasses (dict):
                    - <キー> (dict): 各サービスクラスの詳細情報
                        - DisplayName (str): プランの表示名
                        - IsPublic (bool): 公開フラグ
                        - Price (dict):
                            - Daily (int): 日額（円）
                            - Hourly (int): 時額（円）
                            - Monthly (int): 月額（円）
                            - Zone (str): ゾーン名
                        - ServiceCharge (str): 課金種別
                        - ServiceClassID (int): サービスクラス ID
                        - ServiceClassName (str): サービスクラス名（内部名称）
                        - ServiceClassPath (str): サービスクラスのパス
        """
        try:
            async with httpx.AsyncClient(timeout=10.0,headers={'X-Requested-With': 'XMLHttpRequest'}) as client:
                response = await client.get("https://secure.sakura.ad.jp/cloud/zone/is1a/api/cloud/1.1/public/price.json")
                response.raise_for_status()
            content = response.text
            if not content:
                await ctx.error(f"Failed Get Http Contents")
                return "さくらのクラウドの利用料金取得に失敗しました"
            return content
        except httpx.RequestError as e:
            await ctx.error(f"HTTP Request Error:{e}")
            return f"さくらのクラウドAPIへのリクエストに失敗しました: {e}"
        except httpx.HTTPStatusError as e:
            await ctx.error(f"HTTP Status Error: {e.response.status_code} - {e.response.text}")
            return f"さくらのクラウドAPIからエラーが返されました: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            await ctx.error(f"Unexpected error:{e}")
            return  f"さくらのクラウドAPIの内容取得で予期しないエラーが発生しました: {e}"