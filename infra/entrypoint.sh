#!/bin/bash
# Docker エントリーポイント
# crontab を自動生成し、cron デーモンを起動する

set -e

APP_DIR="/app"
CONFIG_FILE="${APP_DIR}/config/settings.yaml"
CRONTAB_FILE="/etc/cron.d/mail-relay"

echo "=== Mail-to-Chat Relay コンテナ起動 ==="

# crontab 行を生成
echo "[*] crontab を生成中..."
CRON_LINE=$(python3 "${APP_DIR}/infra/generate_crontab.py")

if [ -z "$CRON_LINE" ]; then
    echo "[!] エラー: crontab の生成に失敗しました"
    exit 1
fi

echo "[*] 生成された crontab:"
echo "    $CRON_LINE"

# crontab ファイルを作成（ヘッダー付き）
cat > "$CRONTAB_FILE" <<EOF
# Mail-to-Chat Relay crontab
# 自動生成ファイル（${CONFIG_FILE} から自動生成）

# タイムゾーン設定
TZ=Asia/Tokyo

# 環境設定
SHELL=/bin/sh
PATH=/usr/local/bin:/usr/bin:/bin
MAILTO=""

# Mail-to-Chat Relay 実行設定
${CRON_LINE}

# 空行が必要(cronの仕様)
EOF

echo "[✓] crontab を生成しました: $CRONTAB_FILE"

# cron デーモンを起動
echo "[*] cron デーモンを起動中..."
exec cron -f
