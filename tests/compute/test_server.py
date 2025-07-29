import json
import pytest
from src.core.auth import SacloudApiKey
from src.compute.handlers.server import ServerHandler
from fastmcp import FastMCP, Client
from core.consts import ZONE_URLS
from tests.error import INVALID_AUTH_ERROR, get_invalid_zone_message

class TestServerHandler:
    """ServerHandlerのテスト"""

    @pytest.mark.asyncio
    async def test_init(self, mock_mcp: FastMCP, zone_urls: dict[str, str], api_key: SacloudApiKey):
        """ServerHandlerの初期化テスト"""
        handler = ServerHandler(mock_mcp, zone_urls, api_key)

        # ハンドラの各要素が正しいか検証
        assert handler.mcp == mock_mcp
        assert handler.zone_urls == ZONE_URLS

        # ツールの配列取得
        tool_list = await mock_mcp.list_tools()

        # ツールの要素数が正しいか検証
        assert len(tool_list) == 6

        tool_names = [tool.name for tool in tool_list]        
        
        # ツールが正しく設定されているか検証
        assert 'get_server_list' in tool_names

    @pytest.mark.asyncio
    async def test_get_server_list_success(self, mock_mcp: FastMCP, zone_urls: dict[str, str], api_key: SacloudApiKey, test_zone: str):
        """
        サーバ一覧取得の成功時のテスト
        """

        _server_handler = ServerHandler(mock_mcp, zone_urls, api_key)

        #TODO: Terraformを用いたテスト自動化
        async with Client(mock_mcp) as client:
            res = await client.call_tool("get_server_list", {"zone": test_zone})
            data = json.loads(res[0].text)

            assert isinstance(data, dict)
            assert data["is_ok"]
            assert data["Servers"] is not None

    @pytest.mark.asyncio
    async def test_get_server_list_invalid_zone(self, mock_mcp: FastMCP, zone_urls: dict[str, str], api_key: SacloudApiKey):
        """
        サーバ一覧取得の無効なゾーン取得時のエラーテスト
        """

        _server_handler = ServerHandler(mock_mcp, zone_urls, api_key)

        async with Client(mock_mcp) as client:
            invalid_zone = ""
            res = await client.call_tool("get_server_list", {"zone": invalid_zone})
            result = res[0].text

            assert isinstance(result, str)
            assert get_invalid_zone_message(zone_urls) == result


    @pytest.mark.asyncio
    async def test_get_server_list_invalid_api_key(self, mock_mcp: FastMCP, zone_urls: dict[str, str], test_zone: str):
        """
        サーバ一覧取得の無効なAPIキーのエラーテスト
        """

        invalid_api_key = ("", "")
        _server_handler = ServerHandler(mock_mcp, zone_urls, invalid_api_key)

        async with Client(mock_mcp) as client:
            res = await client.call_tool("get_server_list", {"zone": test_zone})
            result = res[0].text

            assert isinstance(result, str)
            assert INVALID_AUTH_ERROR == result
