# Mail-to-Chat Relay

メールを検知してチャットサービスに通知するプログラム。
特定の件名を持つメールを受信したら、Discordなどのチャットサービスに自動通知します。

（URL・デモ）

## 特徴・機能
- 特定条件のメールを検知（件名の前方一致など）
- チャットサービスに通知を送信
- 30分に1回メールボックスをチェック
- 過去一定時間内（デフォルト60分）に受信したメールのみを処理対象

## 必要要件
- Python 3.11以上
- Docker（本番環境での実行時）
- Gmailと連携する場合: Gmailアカウント（IMAPを有効化）
- Discordと連携する場合: Discord Webhook URL

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd mail-to-chat-relay
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`を作成し、必要な情報を設定します。

```bash
cp .env.example .env
```

`.env`ファイルを編集して以下を設定:
- `MAIL_USER`: メールアドレス
- `MAIL_PASSWORD`: Gmailのアプリパスワード
- `DISCORD_WEBHOOK_URL`: Discord Webhook URL

#### Gmailの設定

1. IMAPを有効化: https://support.google.com/mail/answer/7126229
2. アプリパスワードを作成: https://support.google.com/accounts/answer/185833

#### Discord Webhookの取得

1. Discordサーバーの設定を開く
2. 「連携サービス」→「Webhookを作成」
3. 生成されたURLを`.env`に設定

### 3. 設定ファイルの編集

`config/settings.yaml`を編集して、フィルタ条件などを設定します。

```yaml
mail:
  host: imap.gmail.com
  port: 993
  check_period_minutes: 60  # 過去何分間のメールをチェックするか
  check_interval_minutes: 30  # cron実行間隔（分）

filters:
  - type: "subject"  # 件名フィルター
    condition: "prefix"  # 前方一致
    value: "【重要】"

notifiers:
  discord:
    enabled: true
    message_template: |
      📧 **新着メール通知**
      **件名:** {subject}
      **受信日時:** {date}
      **送信者:** {from}
```

## 使い方

### ローカル実行（開発・テスト）

```bash
# 依存関係のインストール
pip install -r requirements.txt

# スクリプトの実行
python src/main.py
```

### Docker実行（本番環境）

```bash
# Dockerイメージのビルドと起動
docker-compose up -d

# ログの確認
docker-compose logs -f

# コンテナの停止
docker-compose down
```

### テストの実行

```bash
# すべてのテストを実行
pytest

# カバレッジを計測
pytest --cov=src tests/

# 単体テストのみ実行
pytest tests/unit/
```

## プロジェクト構造

```
mail-to-chat-relay/
├── src/
│   ├── mail/              # メール処理
│   ├── notifiers/         # 通知処理
│   ├── config.py          # 設定管理
│   └── main.py            # エントリーポイント
├── config/
│   └── settings.yaml      # 設定ファイル
├── tests/                 # テストコード
├── infra/                 # インフラ設定
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── crontab
└── docs/
    └── design.md          # 設計書
```

## トラブルシューティング

### メール接続エラー

- Gmailの場合、IMAPが有効になっているか確認
- アプリパスワードを使用しているか確認（通常のパスワードは使用不可）
- ネットワーク接続を確認

### 通知が届かない

- Discord Webhook URLが正しいか確認
- Webhook URLの権限が有効か確認
- ログでエラーメッセージを確認: `docker-compose logs -f`

### メールが重複通知される

- `check_period_minutes`の設定を確認（cron実行間隔より長く設定）
- メールが正しく既読になっているか確認

## ライセンス

MIT License

## 関連ドキュメント

- [設計書](docs/design.md)
