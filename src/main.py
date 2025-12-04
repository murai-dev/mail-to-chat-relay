"""Mail-to-Chat Relay メインスクリプト

メールを検知してチャットサービスに通知する。
"""

import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.mail.imap_client import IMAPClient
from src.notifiers.discord_notifier import DiscordNotifier
from src.filters import EmailFilter


# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    """メイン処理"""
    logger.info("Processing started")
    
    try:
        # 設定を読み込み
        config = Config()
        logger.info("Configuration loaded")
        
        # IMAPクライアントを初期化
        imap_client = IMAPClient(
            host=config.mail_host,
            port=config.mail_port,
            user=config.mail_user,
            password=config.mail_password
        )
        
        # IMAPサーバーに接続
        if not imap_client.connect():
            logger.error("Failed to connect to IMAP server")
            return 1
        
        try:
            # 最近のメールを取得（実行間隔×1.5分）
            period_minutes = int(config.check_interval_minutes * 1.5)
            emails = imap_client.get_recent_emails(period_minutes)
            
            # フィルタリング
            email_filter = EmailFilter(config.filters)
            filtered_emails = email_filter.filter_emails(emails)
            
            # 通知が有効な場合
            if config.discord_enabled and filtered_emails:
                # Discord通知クライアントを初期化
                notifier = DiscordNotifier(
                    webhook_url=config.discord_webhook_url,
                    channel_id=config.discord_channel_id,
                    message_template=config.discord_message_template
                )
                
                # 各メールについて通知を送信
                success_count = 0
                for i, email_data in enumerate(filtered_emails, 1):
                    message = {
                        "subject": email_data["subject"],
                        "date": email_data["date"],
                        "from": email_data["from"]
                    }
                    
                    if notifier.send(message):
                        success_count += 1
                        # 通知成功したメールを既読にする
                        imap_client.mark_as_read(email_data["id"])
                    else:
                        logger.error(f"Failed to send notification ({i}/{len(filtered_emails)})")
                
                logger.info(f"Sent {success_count}/{len(filtered_emails)} notifications successfully")
            
            elif not config.discord_enabled:
                logger.info("Discord notification is disabled")
            
        finally:
            # IMAP接続を切断
            imap_client.disconnect()
        
        logger.info("Processing completed")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
