# sacloud/py-template

さくらのクラウド向けOSSプロダクトでのプロジェクトテンプレート(Python)

## 概要

さくらのクラウド向けOSSプロダクトでPythonを用いるプロジェクトのためのテンプレート

さくらのクラウドでのPythonプロダクトでは以下のツール群を中心に開発します。

- uv: パッケージ & 仮想環境マネージャ
- ruff: linter & formatter
- pytest: テスト
- lefthook: githook manager

## 使い方

GitHubでリポジトリを作成する際にテンプレートとしてsacloud/py-templateを選択して作成します。 

次に`py-template`という文字列を自身のプロジェクトのものに置き換えてください。

例: exampleという名前のプロジェクトを作成する場合

```bash
# 作成したプロジェクトのディレクトリに移動
cd example
# 置き換え
find . -type f | xargs sed -i '' -e "s/ts-template/example/g"
```

## TODO

- パッケージのPublish周りをチェックする

## License

`py-template` Copyright (C) 2025- The sacloud/py-template authors.
This project is published under [Apache 2.0 License](LICENSE).
