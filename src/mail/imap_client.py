"""IMAPクライアントモジュール

IMAPサーバーに接続してメールを取得する。
"""

import imaplib
import email
import logging
from datetime import datetime, timedelta
from email.header import decode_header
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)


class IMAPClient:
    """IMAPクライアントクラス
    
    IMAPサーバーに接続してメールを取得する。
    """
    
    def __init__(self, host: str, port: int, user: str, password: str):
        """IMAPクライアントを初期化
        
        Args:
            host: IMAPサーバーのホスト名
            port: IMAPサーバーのポート番号
            user: メールアカウントのユーザー名
            password: メールアカウントのパスワード
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection: Optional[imaplib.IMAP4_SSL] = None
    
    def connect(self) -> bool:
        """IMAPサーバーに接続
        
        Returns:
            bool: 接続成功時はTrue、失敗時はFalse
        """
        try:
            self.connection = imaplib.IMAP4_SSL(self.host, self.port)
            self.connection.login(self.user, self.password)
            self.connection.select("INBOX")
            logger.info(f"Connected to {self.host}:{self.port}")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def disconnect(self) -> None:
        """IMAPサーバーから切断"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("Disconnected")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.connection = None
    
    def get_recent_emails(self, period_minutes: int) -> List[Dict[str, Any]]:
        """指定期間内に受信したメールを取得
        
        Args:
            period_minutes: 過去何分間のメールを取得するか
        
        Returns:
            List[Dict[str, Any]]: メール情報のリスト
                [
                    {
                        "id": "メールID",
                        "subject": "件名",
                        "from": "送信者",
                        "date": "受信日時"
                    },
                    ...
                ]
        """
        if not self.connection:
            logger.error("Not connected to IMAP server")
            return []
        
        try:
            # 検索日時を計算（UTC）
            since_date = datetime.utcnow() - timedelta(minutes=period_minutes)
            since_str = since_date.strftime("%d-%b-%Y")
            
            # 指定日以降のメールを検索
            status, messages = self.connection.search(None, f'SINCE {since_str}')
            
            if status != "OK":
                logger.error("Failed to search emails")
                return []
            
            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} emails since {since_str}")
            
            # メール詳細を取得
            emails = []
            for email_id in email_ids:
                email_data = self._fetch_email(email_id)
                if email_data:
                    # 時刻の厳密なチェック（分単位でフィルタ）
                    if self._is_within_period(email_data["date"], period_minutes):
                        emails.append(email_data)
            
            logger.info(f"Found {len(emails)} emails in the last {period_minutes} minutes")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def _fetch_email(self, email_id: bytes) -> Optional[Dict[str, Any]]:
        """メールの詳細情報を取得
        
        Args:
            email_id: メールID
        
        Returns:
            Dict[str, Any]: メール情報、取得失敗時はNone
        """
        try:
            status, msg_data = self.connection.fetch(email_id, "(RFC822)")
            
            if status != "OK":
                return None
            
            # メールメッセージを解析
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # 件名をデコード
            subject = self._decode_mime_header(email_message.get("Subject", ""))
            
            # 送信者をデコード
            from_header = self._decode_mime_header(email_message.get("From", ""))
            
            # 受信日時を取得
            date_str = email_message.get("Date", "")
            date_obj = email.utils.parsedate_to_datetime(date_str)
            
            return {
                "id": email_id.decode(),
                "subject": subject,
                "from": from_header,
                "date": date_obj.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error fetching email {email_id}: {e}")
            return None
    
    def _decode_mime_header(self, header: str) -> str:
        """MIMEヘッダーをデコード
        
        Args:
            header: MIMEヘッダー文字列
        
        Returns:
            str: デコードされた文字列
        """
        if not header:
            return ""
        
        decoded_parts = decode_header(header)
        decoded_str = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(encoding or "utf-8", errors="ignore")
            else:
                decoded_str += part
        
        return decoded_str
    
    def _is_within_period(self, date_str: str, period_minutes: int) -> bool:
        """メールが指定期間内に受信されたかチェック
        
        Args:
            date_str: メールの受信日時文字列
            period_minutes: チェック期間（分）
        
        Returns:
            bool: 期間内ならTrue
        """
        try:
            email_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            threshold = datetime.now() - timedelta(minutes=period_minutes)
            return email_date >= threshold
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {e}")
            return False
    
    def mark_as_read(self, email_id: str) -> bool:
        """メールを既読にする
        
        Args:
            email_id: メールID
        
        Returns:
            bool: 成功時はTrue、失敗時はFalse
        """
        if not self.connection:
            logger.error("Not connected to IMAP server")
            return False
        
        try:
            self.connection.store(email_id.encode(), '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False
