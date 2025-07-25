import pytest
from src.core.auth import get_api_key,get_objectstorage_api_key
from src.core.mcp import create_mcp
from core.consts import ZONE_URLS
from objectstorage.consts import OBJDCTSTORAGE_ZONE_URLS

@pytest.fixture
def mock_mcp():
    """MCPサーバ作成"""
    return create_mcp()

@pytest.fixture
def api_key():
    """APIキー取得作成"""
    return get_api_key()

@pytest.fixture
def zone_urls():
    """ZONE_URL取得"""
    return ZONE_URLS

@pytest.fixture
def test_zone():
    """テスト用に用いるゾーン取得"""
    return "tk1v" 

@pytest.fixture
def objectstorage_zone_urls():
    """OBJDCTSTORAGE_ZONE_URLS取得"""
    return OBJDCTSTORAGE_ZONE_URLS

@pytest.fixture
def objectstorage_api_key():
    """オブジェクトストレージAPIキー取得作成"""
    return get_objectstorage_api_key()