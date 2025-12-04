"""IMAPClientクラスの単体テスト"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.mail.imap_client import IMAPClient


@pytest.fixture
def imap_client():
    """IMAPClientインスタンスを作成"""
    return IMAPClient(
        host="imap.example.com",
        port=993,
        user="test@example.com",
        password="password"
    )


def test_connect_success(imap_client):
    """IMAP接続が成功するか"""
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        mock_connection = Mock()
        mock_imap.return_value = mock_connection
        mock_connection.login.return_value = ("OK", [])
        mock_connection.select.return_value = ("OK", [])
        
        result = imap_client.connect()
        
        assert result is True
        mock_imap.assert_called_once_with("imap.example.com", 993)
        mock_connection.login.assert_called_once_with("test@example.com", "password")
        mock_connection.select.assert_called_once_with("INBOX")


def test_connect_failure(imap_client):
    """IMAP接続失敗時にFalseを返すか"""
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        mock_imap.side_effect = Exception("Connection failed")
        
        result = imap_client.connect()
        
        assert result is False


def test_disconnect(imap_client):
    """切断処理が正常に実行されるか"""
    mock_connection = Mock()
    imap_client.connection = mock_connection
    
    imap_client.disconnect()
    
    mock_connection.close.assert_called_once()
    mock_connection.logout.assert_called_once()
    assert imap_client.connection is None


def test_get_recent_emails_not_connected(imap_client):
    """未接続時に空リストを返すか"""
    result = imap_client.get_recent_emails(60)
    
    assert result == []


def test_get_recent_emails_success(imap_client):
    """最近のメールを正しく取得できるか"""
    with patch('imaplib.IMAP4_SSL'):
        mock_connection = Mock()
        imap_client.connection = mock_connection
        
        # search結果をモック
        mock_connection.search.return_value = ("OK", [b"1 2 3"])
        
        # fetch結果をモック
        def mock_fetch(email_id, command):
            email_data = b"""From: sender@example.com
Subject: Test Subject
Date: """ + datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000").encode()
            return ("OK", [(b"", email_data)])
        
        mock_connection.fetch = mock_fetch
        
        with patch.object(imap_client, '_is_within_period', return_value=True):
            result = imap_client.get_recent_emails(60)
            
            assert len(result) == 3


def test_mark_as_read_success(imap_client):
    """メールを既読にできるか"""
    mock_connection = Mock()
    imap_client.connection = mock_connection
    
    result = imap_client.mark_as_read("123")
    
    assert result is True
    mock_connection.store.assert_called_once_with(b"123", '+FLAGS', '\\Seen')


def test_mark_as_read_not_connected(imap_client):
    """未接続時に既読マークがFalseを返すか"""
    result = imap_client.mark_as_read("123")
    
    assert result is False


def test_decode_mime_header(imap_client):
    """MIMEヘッダーが正しくデコードされるか"""
    # UTF-8エンコードされた日本語件名
    header = "=?UTF-8?B?44OG44K544OI?="  # "テスト"
    
    result = imap_client._decode_mime_header(header)
    
    assert result == "テスト"


def test_decode_mime_header_plain(imap_client):
    """プレーンテキストヘッダーがそのまま返されるか"""
    header = "Plain Text"
    
    result = imap_client._decode_mime_header(header)
    
    assert result == "Plain Text"


def test_is_within_period_true(imap_client):
    """期間内のメールが正しく判定されるか"""
    # 30分前の日時
    email_date = (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    
    result = imap_client._is_within_period(email_date, 60)
    
    assert result is True


def test_is_within_period_false(imap_client):
    """期間外のメールが正しく判定されるか"""
    # 90分前の日時
    email_date = (datetime.now() - timedelta(minutes=90)).strftime("%Y-%m-%d %H:%M:%S")
    
    result = imap_client._is_within_period(email_date, 60)
    
    assert result is False
