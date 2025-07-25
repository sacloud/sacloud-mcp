# sacloud/mcp-sacloud

## 概要

sacloud/mcp-sacloudはさくらのクラウド向けMCPサーバです。

## 開発環境の構築

### 必要ツール

### プロジェクトのクローン

```
git clone https://github.com/sacloud/mcp-sacloud.git
```

### uvのインストール

より詳細なインストール方法・使用方法については、uvの[ドキュメント](https://docs.astral.sh/uv/)を参照してください。

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 環境構築同期

```
uv sync
```

## LLMへMCPをインストール

任意のLLMへMCPをインストールする。
一例としてclaude desktopでの設定を示す。

claude desktopの設定ファイルに以下を追記する。
なお、設定ファイルの位置はOS毎に以下の通りである。

- macOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```
{
  "mcpServers": {
    "sacloud": {
      "command": "${HOME}/.local/bin/uv",
      "args": [
        "--directory",
        "<<MCPサーバーのルートディレクトリ>>/src",
        "run",
        "main.py"
      ],
      "env": {
        "<<環境変数1>>": "<<値をコピーしてここへ貼り付ける>>",
        "<<環境変数2>>": "<<値をコピーしてここへ貼り付ける>>"
      }
    }
  }
}
```

<<>>で示された要素について、以下を参考に適宜置き換える。

- MCPサーバーのルートディレクトリ
  - 例: `/Users/user/Source/mcp-sacloud`
- 環境変数
  - 使用する機能に応じて環境変数を設定。
    - さくらのクラウドのリソースにアクセスする場合、[さくらのクラウドのAPIキー](https://manual.sakura.ad.jp/cloud/api/apikey.html)を参照して置き換える。
      - `"ACCESS_TOKEN": "<<値をコピーしてここへ貼り付ける>>"`
      - `"ACCESS_TOKEN_SECRET": "<<値をコピーしてここへ貼り付ける>>"`
    - さくらのオブジェクトストレージにアクセスする場合、[さくらのオブジェクトストレージのAPIキー](https://manual.sakura.ad.jp/api/cloud/objectstorage/#section/%E5%9F%BA%E6%9C%AC%E7%9A%84%E3%81%AA%E4%BD%BF%E3%81%84%E6%96%B9/API)を参照して置き換える。
      - `"OBJECTSTORAGE_ACCESS_KEY_ID": "<<値をコピーしてここへ貼り付ける>>"`
      - `"OBJECTSTORAGE_SECRET_ACCESS_KEY": "<<値をコピーしてここへ貼り付ける>>"`

## テスト
### 構成について
`tests/conftest.py`には、全テストファイルで利用可能なfixtureが定義されており、
すべてのテストファイルから明示的な`import`不要で利用できる。

### 準備
環境変数から認証情報を取得するため、テスト実行前に`ACCESS_TOKEN`と`ACCESS_TOKEN_SECRET`設定する

```
export ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxx
export ACCESS_TOKEN_SECRET=xxxxxxxxxxxxxxxxxxxx
export OBJECTSTORAGE_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxx
export OBJECTSTORAGE_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxx
```

### テスト実行
```
uv run pytest
```

## License

`mcp-sacloud` Copyright (C) 2025- The sacloud/mcp-sacloud authors.
This project is published under [Apache 2.0 License](LICENSE).
