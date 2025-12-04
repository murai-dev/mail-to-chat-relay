FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY src/ /app/src/
COPY config/ /app/config/
COPY infra/ /app/infra/

# cronをインストール
RUN apt-get update && \
    apt-get install -y cron dos2unix tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# JPタイムゾーン設定
ENV TZ=Asia/Tokyo
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# ログディレクトリを作成
RUN mkdir -p /var/log

# エントリーポイントスクリプトにパーミッションを設定
RUN chmod +x /app/infra/entrypoint.sh && \
    dos2unix /app/infra/entrypoint.sh

# PAM設定の修正（Dockerコンテナ内でcronを動かすために必要）
RUN sed -i 's/^\s*session\s\+required\s\+pam_loginuid.so/# &/' /etc/pam.d/cron

# cronログファイルを作成
RUN touch /var/log/mail-relay.log

# エントリーポイントを実行
ENTRYPOINT ["/app/infra/entrypoint.sh"]
