"""Discord通知モジュール

Discord Webhookを使用してメッセージを送信する。
"""

import logging
from typing import Dict, Any, Optional

import requests

from .base import BaseNotifier


logger = logging.getLogger(__name__)


class DiscordNotifier(BaseNotifier):
    """Discord Webhook通知クラス
    
    Discord WebhookのURLを使用してメッセージを送信する。
    """
    
    def __init__(self, webhook_url: str, channel_id: Optional[str] = None, message_template: Optional[str] = None):
        """Discord通知クラスを初期化
        
        Args:
            webhook_url: Discord Webhook URL
            channel_id: チャンネルID（オプション）
            message_template: メッセージテンプレート（オプション）
        """
        self.webhook_url = webhook_url
        self.channel_id = channel_id
        self.message_template = message_template or self._get_default_template()
    
    def send(self, message: Dict[str, Any]) -> bool:
        """Discord Webhookに通知を送信
        
        Args:
            message: 送信するメッセージ情報
                {
                    "subject": "メールの件名",
                    "date": "受信日時",
                    "from": "送信者" (オプション)
                }
        
        Returns:
            bool: 送信成功時はTrue、失敗時はFalse
        """
        try:
            # Discordメッセージを構築
            content = self._format_message(message)
            
            # Webhook送信
            response = requests.post(
                self.webhook_url,
                json={"content": content},
                timeout=10
            )
            
            # ステータスコードをチェック
            if response.status_code == 204:
                logger.info("Notification sent successfully")
                return True
            else:
                logger.error(
                    f"Failed to send notification: "
                    f"status_code={response.status_code}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    def _format_message(self, message: Dict[str, Any]) -> str:
        """メッセージをDiscord用にフォーマット
        
        Args:
            message: メッセージ情報
        
        Returns:
            str: フォーマットされたメッセージ
        """
        # テンプレートに値をフォーマット
        try:
            formatted = self.message_template.format(
                subject=message.get('subject', '(件名なし)'),
                date=message.get('date', '不明'),
                from_addr=message.get('from', '不明'),
                from_=message.get('from', '不明')  # 別のキー名でも対応
            )
            return formatted
        except KeyError as e:
            logger.warning(f"Template format error: {e}. Using default format.")
            return self._format_message_default(message)
    
    def _format_message_default(self, message: Dict[str, Any]) -> str:
        """デフォルトメッセージフォーマット
        
        Args:
            message: メッセージ情報
        
        Returns:
            str: フォーマットされたメッセージ
        """
        lines = [
            "📧 **新着メール通知**",
            f"**件名:** {message.get('subject', '(件名なし)')}",
            f"**受信日時:** {message.get('date', '不明')}",
        ]
        
        # 送信者情報がある場合は追加
        if "from" in message:
            lines.append(f"**送信者:** {message['from']}")
        
        return "\n".join(lines)
    
    def _get_default_template(self) -> str:
        """デフォルトテンプレートを取得
        
        Returns:
            str: デフォルトメッセージテンプレート
        """
        return "📧 **新着メール通知**\n**件名:** {subject}\n**受信日時:** {date}\n**送信者:** {from_}"
        if "from" in message:
            lines.append(f"**送信者:** {message['from']}")
        
        return "\n".join(lines)
