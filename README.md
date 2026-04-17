# Solitaire Sound Guard

Windowsの「Microsoft Solitaire Collection」などで、プロセスが切り替わるたびに音量がリセットされ大音量になる問題を解決するための、Python製サウンド制御ツールです。

## 特徴
- **自動監視モード**: 2秒ごとにプロセスをチェックし、ソリティアが起動または再起動しても即座にミュートを適用します。
- **uv対応**: インラインスクリプトメタデータ（PEP 723）を採用しており、複雑な環境構築は不要です。

## 動作要件
- **OS**: Windows 11 (WSL環境では動作しません)
- **ツール**: [uv](https://github.com/astral-sh/uv) (高速なPythonパッケージマネージャー)
- **対象アプリ**: プロセス名に "Solitaire" を含むWindowsアプリケーション

## 使い方

### 1. uvのインストール (未導入の場合)
PowerShellなどのターミナルで以下を実行してください。
```powershell
powershell -c "irsp.get.uv.al | iex"
```

### 2. 実行コマンド
プログラムがあるフォルダをターミナルで開き、以下のコマンドを入力します。

```powershell
uv run app/mute.py
```
※ 初回実行時に必要なライブラリが自動的に準備されるため、uv add などの事前作業は一切不要です。
