"""DiscordNotifierクラスの単体テスト"""

from unittest.mock import Mock, patch

import pytest

from src.notifiers.discord_notifier import DiscordNotifier


@pytest.fixture
def notifier():
    """DiscordNotifierインスタンスを作成"""
    return DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test")


def test_send_success(notifier):
    """通知が正常に送信されるか"""
    message = {
        "subject": "テスト件名",
        "date": "2025-12-04 10:00:00",
        "from": "sender@example.com"
    }
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        result = notifier.send(message)
        
        assert result is True
        mock_post.assert_called_once()
        
        # 呼び出し引数を確認
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://discord.com/api/webhooks/test"
        assert "content" in call_args[1]["json"]


def test_send_failure_status_code(notifier):
    """HTTPステータスコードエラー時にFalseを返すか"""
    message = {
        "subject": "テスト件名",
        "date": "2025-12-04 10:00:00"
    }
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = notifier.send(message)
        
        assert result is False


def test_send_network_error(notifier):
    """ネットワークエラー時にFalseを返すか"""
    message = {
        "subject": "テスト件名",
        "date": "2025-12-04 10:00:00"
    }
    
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("Network error")
        
        result = notifier.send(message)
        
        assert result is False


def test_format_message_with_from(notifier):
    """送信者情報を含むメッセージが正しくフォーマットされるか"""
    message = {
        "subject": "テスト件名",
        "date": "2025-12-04 10:00:00",
        "from": "sender@example.com"
    }
    
    formatted = notifier._format_message(message)
    
    assert "テスト件名" in formatted
    assert "2025-12-04 10:00:00" in formatted
    assert "sender@example.com" in formatted


def test_format_message_without_from(notifier):
    """送信者情報がない場合のメッセージフォーマット"""
    message = {
        "subject": "テスト件名",
        "date": "2025-12-04 10:00:00"
    }
    
    formatted = notifier._format_message(message)
    
    assert "テスト件名" in formatted
    assert "2025-12-04 10:00:00" in formatted
    assert "送信者" not in formatted


def test_format_message_empty_subject(notifier):
    """件名が空の場合のメッセージフォーマット"""
    message = {
        "date": "2025-12-04 10:00:00"
    }
    
    formatted = notifier._format_message(message)
    
    assert "(件名なし)" in formatted
