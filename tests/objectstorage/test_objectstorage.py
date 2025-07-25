import json
import pytest
from src.core.auth import SacloudApiKey,ObjectStorageApiKey
from fastmcp import FastMCP, Client
from objectstorage.consts import OBJDCTSTORAGE_ZONE_URLS
from objectstorage.handlers.objectstorage import ObjectStorageHandler


class TestObjectStorageHandler:
    """ObjectStorageHandlerのテスト"""

    @pytest.mark.asyncio
    async def test_init(self, mock_mcp: FastMCP, objectstorage_zone_urls: dict[str,str],api_key: SacloudApiKey,objectstorage_api_key: ObjectStorageApiKey):
        """ObjectStorageHandlerの初期化テスト"""
        handler = ObjectStorageHandler(mock_mcp, objectstorage_zone_urls,api_key,objectstorage_api_key)

        # ハンドラの各要素が正しいか検証
        assert handler.mcp == mock_mcp
        assert handler.objectstorage_zone_urls == OBJDCTSTORAGE_ZONE_URLS

        # ツールの配列取得
        tool_list = await mock_mcp.list_tools()

        # ツールの要素数が正しいか検証
        assert len(tool_list) == 3

        tool_names = [tool.name for tool in tool_list]     

        # ツールが正しく設定されているか検証
        assert 'get_objectstorage_site_list' in tool_names

    @pytest.mark.asyncio
    async def test_get_objectstorage_site_list_success(self, mock_mcp: FastMCP, objectstorage_zone_urls: dict[str,str],api_key: SacloudApiKey,objectstorage_api_key: ObjectStorageApiKey):
        """
        オブジェクトストレージのサイト一覧取得の成功時のテスト
        """
        _handler = ObjectStorageHandler(mock_mcp, objectstorage_zone_urls,api_key,objectstorage_api_key)

        async with Client(mock_mcp) as client:
            res = await client.call_tool("get_objectstorage_site_list")
            data = json.loads(res[0].text)

            assert isinstance(data,dict)
            assert data["data"] is not None

    @pytest.mark.asyncio
    async def test_get_objectstorage_site_invalid_api_key(self, mock_mcp: FastMCP, objectstorage_zone_urls: dict[str,str],objectstorage_api_key: ObjectStorageApiKey):
        """オブジェクトストレージのサイト一覧の取得の無効なAPIキーのエラーテスト"""
        invalid_api_key = ("", "")
        _handler = ObjectStorageHandler(mock_mcp, objectstorage_zone_urls,invalid_api_key,objectstorage_api_key)

        async with Client(mock_mcp) as client:
            res = await client.call_tool("get_objectstorage_site_list")
            data = res[0].text

            assert data.startswith("認証情報が設定されていません。")

    @pytest.mark.asyncio
    async def test_get_objectstorage_accesskey_list_success(self, mock_mcp: FastMCP, objectstorage_zone_urls: dict[str,str],api_key: SacloudApiKey,objectstorage_api_key: ObjectStorageApiKey):
        """オブジェクトストレージのアクセスキー一覧の取得の成功時のテスト"""
        _handler = ObjectStorageHandler(mock_mcp, objectstorage_zone_urls,api_key,objectstorage_api_key)

        async with Client(mock_mcp) as client:
            res = await client.call_tool("get_objectstorage_accesskey_list",{"site_id":"isk01"})
            data = json.loads(res[0].text)

            assert isinstance(data,dict)
            assert data["data"] is not None

    @pytest.mark.asyncio
    async def test_get_objectstorage_accesskey_list_invalid_site(self, mock_mcp: FastMCP, objectstorage_zone_urls: dict[str,str],api_key: SacloudApiKey,objectstorage_api_key: ObjectStorageApiKey):
        """オブジェクトストレージのアクセスキー一覧の無効なゾーン取得時のエラーテスト"""
        _handler = ObjectStorageHandler(mock_mcp, objectstorage_zone_urls,api_key,objectstorage_api_key)

        async with Client(mock_mcp) as client:
            res = await client.call_tool("get_objectstorage_accesskey_list",{"site_id":""})
            data = res[0].text

            assert data.startswith("さくらのクラウドAPIからエラーが返されました: ")

    @pytest.mark.asyncio
    async def test_get_objectstorage_accesskey_list_invalid_api_key(self, mock_mcp: FastMCP, objectstorage_zone_urls: dict[str,str],objectstorage_api_key: ObjectStorageApiKey):
        """オブジェクトストレージのアクセスキー一覧の無効なAPIキーのエラーテスト"""
        invalid_api_key = ("", "")
        _handler = ObjectStorageHandler(mock_mcp, objectstorage_zone_urls,invalid_api_key,objectstorage_api_key)

        async with Client(mock_mcp) as client:
            res = await client.call_tool("get_objectstorage_accesskey_list",{"site_id":"isk01"})
            data = res[0].text

            assert data.startswith("認証情報が設定されていません。")

    @pytest.mark.asyncio
    async def test_get_objectstorage_bucket_success(self, mock_mcp: FastMCP, objectstorage_zone_urls: dict[str,str],api_key: SacloudApiKey,objectstorage_api_key: ObjectStorageApiKey):
        """オブジェクトストレージのバケット一覧の取得成功時のテスト"""
        _handler = ObjectStorageHandler(mock_mcp, objectstorage_zone_urls,api_key,objectstorage_api_key)

        async with Client(mock_mcp) as client:
            res = await client.call_tool("get_objectstorage_bucket_list")
            data = json.loads(res[0].text)

            assert isinstance(data,dict)
            assert data["ResponseMetadata"]["HTTPStatusCode"] == 200

    @pytest.mark.asyncio
    async def test_get_objectstorage_bucket_invalid_api_key(self, mock_mcp: FastMCP, objectstorage_zone_urls: dict[str,str],api_key: SacloudApiKey):
        """オブジェクトストレージのバケット一覧の取得成功時のテスト"""
        invalid_objectstorage_api_key = ("", "")
        _handler = ObjectStorageHandler(mock_mcp, objectstorage_zone_urls,api_key,invalid_objectstorage_api_key)

        async with Client(mock_mcp) as client:
            res = await client.call_tool("get_objectstorage_bucket_list")
            data = res[0].text

            assert isinstance(data,str)
            assert data.startswith("オブジェクトストレージの認証情報")
