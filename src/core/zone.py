from typing import Optional

from core.consts import ZONE_URLS


def validate_zone(zone: str) -> Optional[str]:
    """ゾーンを検証し、不正であればエラーメッセージを返す"""
    if zone not in ZONE_URLS:
        return f"無効なゾーンです。利用可能なゾーン: {', '.join(ZONE_URLS.keys())}"
    return None
