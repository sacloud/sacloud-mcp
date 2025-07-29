from docs.handlers.documents import DocumentsHandler
from docs.handlers.api_documents import APIDocumentsHandler
def initialize_documents(mcp):
    """全てのハンドラーを初期化する
    
    Args:
        mcp: MCPクライアント
        
    Returns:
        dict: 初期化されたハンドラーの辞書
    """

    return {
        'documents': DocumentsHandler(mcp),
        'api_documents': APIDocumentsHandler(mcp)
    }
