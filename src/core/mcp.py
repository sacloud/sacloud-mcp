from mcp.server.fastmcp import FastMCP

def create_mcp() -> FastMCP:
    return FastMCP(
        name="sacloud",
        instructions="""
            さくらのクラウドAPIを使用して、さくらのクラウドの操作を行うためのツールです。
            利用可能なゾーンを確認するにはget_zone_listを使用してください。

            重要: エラーメッセージでゾーン一覧を表示する際は、定義と完全に一致する名称のみを使用してください。
            推測や類推による名称変更は行わず、定義されている通りの名称を正確に表示してください。
        """,
    )
