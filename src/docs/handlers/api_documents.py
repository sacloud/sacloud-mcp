from bs4 import BeautifulSoup
from mcp.server.fastmcp import Context
import httpx
from html_to_markdown import convert_to_markdown

class APIDocumentsHandler:
    """ドキュメントのMCPサーバハンドラ"""
    def __init__(
        self,
        mcp,
    ):
        self.manual_outlines = None
        self.mcp = mcp

        # MCPサーバのツール登録
        self.mcp.tool(name='get_api_manual_outline')(self.get_api_manual_outline)
        self.mcp.tool(name='read_api_manual')(self.read_api_manual)
        self.mcp.tool(name='read_object_storage_api_manual')(self.read_object_storage_api_manual)

    async def get_api_manual_outline(self,ctx: Context):
        """
        さくらのクラウドのAPIマニュアルの目次を項目名と対応するurlを辞書型で返します。
        Returns:
            dict:  さくらのクラウドのマニュアルの目次
                - 目次名(str): url(str)
        """
        links = {}
        url = 'https://manual.sakura.ad.jp/cloud-api/1.1/index.html'
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            a_tags = soup.find_all("a",class_="js-toggle-guides")
            for a in a_tags:
                href = f"https://manual.sakura.ad.jp/cloud-api/1.1/{a['href']}"
                text = a.get_text(strip=True)
                links[text] = href
            return  links
        except httpx.RequestError as e:
            await ctx.error(f"http Request Error:{e}")
            return f"さくらのクラウドのAPIマニュアルへのリクエストに失敗しました: {e}"
        except httpx.HTTPStatusError as e:
            await ctx.error(f"HTTP Status Error:{e}")
            return f"さくらのクラウドのAPIマニュアルからエラーが返されました: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            await ctx.error(f"Unexpected error:{e}")
            return  f"APIドキュメント目次取得で予期しないエラーが発生しました。: {e}"
        
    # mainを抜き出して、htmlからmarkdownに変更する
    def reformat_manual_page(self,html:str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        main_html = soup.find(id="content")
        if not main_html:
            return None
        main_markdown = convert_to_markdown(main_html)
        return main_markdown
    
    async def read_api_manual(self,ctx:Context,url:str):
        """
            指定したさくらのクラウドのAPIマニュアル(https://manual.sakura.ad.jp/cloud-api/~)のurlを受け取り、markdownに変換し、主要の内容を取得します。
            Args:
                url (str): さくらのクラウドのAPIマニュアルのurl
            Returns:
                str: さくらのAPIクラウドのマニュアルの内容
        """
        if not url.startswith('https://manual.sakura.ad.jp/cloud-api/'):
            return 'さくらのクラウドのAPIマニュアルのurlではないので、有効なurlを指定してください'
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
            content = self.reformat_manual_page(response.text)
            if not content:
                await ctx.error(f"format failed")
                return 'error:urlをフォーマットできなかった'
            return content
        except httpx.RequestError as e:
            await ctx.error(f"HTTP Request Error:{e}")
            return f"さくらのクラウドのAPIマニュアルへのリクエストに失敗しました: {e}"
        except httpx.HTTPStatusError as e:
            await ctx.error(f"HTTP Status Error:{e.response.status_code} - {e.response.text}")
            return f"さくらのクラウドのAPIマニュアルからエラーが返されました: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            await ctx.error(f"Unexpected error:{e}")
            return  f"さくらのクラウドのAPIマニュアルの内容取得で予期しないエラーが発生しました: {e}" 
    async def read_object_storage_api_manual(self,ctx:Context):
        """
            指定したさくらのクラウドのオブジェクトストレージAPIマニュアル(https://manual.sakura.ad.jp/cloud-api/~)のurlを受け取り、markdownに変換し、主要の内容を取得します。
            Returns:
                str: さくらのAPIクラウドのオブジェクトストレージのAPIマニュアルの内容
        """
        url = "https://manual.sakura.ad.jp/api/cloud/objectstorage/"
        try:
            async with httpx.AsyncClient(timeout=10.0,) as client:
                response = await client.get(url)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.find_all("div",class_="api-content")
            if not content:
                await ctx.error(f"Failed Get Http Contents")
                return 'error:urlをフォーマットできなかった'
            return content
        except httpx.RequestError as e:
            await ctx.error(f"HTTP Request Error:{e}")
            return f"さくらのクラウドのオブジェクトストレージAPIマニュアルへのリクエストに失敗しました: {e}"
        except httpx.RequestError as e:
            await ctx.error(f"HTTP Status Error:{e.response.status_code} - {e.response.text}")
            return f"さくらのクラウドのオブジェクトストレージのAPIマニュアルからエラーが返されました: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            await ctx.error(f"Unexpected error:{e}")
            return f"さくらのクラウドのオブジェクトストレージのAPIマニュアルの内容取得で予期しないエラーが発生しました: {e}"


