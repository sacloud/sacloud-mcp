import os
from typing import Optional, Tuple

import httpx

# (access_token, access_token_secret)
SacloudApiKey = Tuple[str, str]
ObjectStorageApiKey = Tuple[str, str]


def get_api_key() -> SacloudApiKey:
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    # FIX_ME:
    # ここでエラーハンドリングすると、ユーザがエラー内容に気づきにくい、
    # ドキュメント取得など認証情報が不要なツールを使えなくなる、等の不都合が生じる。
    # 一方で各ハンドラ内で都度エラーハンドリングすると冗長になるので、
    # 環境変数取得のエラーハンドリングは対策を考える

    return access_token, access_token_secret


def check_auth(api_key: SacloudApiKey) -> Optional[str]:
    """認証情報をチェックし、不正であればエラーメッセージを返す"""
    missing = []
    if not api_key[0]:
        missing.append("ACCESS_TOKEN")
    if not api_key[1]:
        missing.append("ACCESS_TOKEN_SECRET")
    if missing:
        return f"認証情報が設定されていません。{', '.join(missing)} の環境変数を設定してください。"
    return None

def get_objectstorage_api_key() -> ObjectStorageApiKey:
    objectstorage_access_token = os.getenv("OBJECTSTORAGE_ACCESS_KEY_ID")
    objectstorage_access_token_secret = os.getenv("OBJECTSTORAGE_SECRET_ACCESS_KEY")

    return objectstorage_access_token, objectstorage_access_token_secret

def check_objectstorage_auth(objectstorage_api_key:ObjectStorageApiKey):
    """オブジェクトストレージの認証情報をチェックし、不正であればエラーメッセージを返す"""
    missing = []
    if not objectstorage_api_key[0]:
        missing.append("OBJECTSTORAGE_ACCESS_KEY_ID")
    if not objectstorage_api_key[1]:
        missing.append("OBJECTSTORAGE_SECRET_ACCESS_KEY")
    if missing:
        return f"オブジェクトストレージの認証情報が設定されていません。{', '.join(missing)} の環境変数を設定してください。"
    return None


def get_http_client(api_key: SacloudApiKey) -> httpx.Client:
    """認証情報が設定されたHTTPクライアントを返す"""
    return httpx.Client(auth=(api_key))
