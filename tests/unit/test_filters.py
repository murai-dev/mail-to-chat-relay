"""新しいフィルター機能のテスト"""

# pytestは使用可能な場合のみインポート
try:
    import pytest
except ImportError:
    pytest = None

from src.filters import EmailFilter


class TestEmailFilter:
    """EmailFilterクラスのテスト"""
    
    def setup_method(self):
        """テストデータの初期化"""
        self.test_emails = [
            {
                'id': '1',
                'subject': '【重要】システム停止予定',
                'from': 'admin@example.com',
                'date': '2025-12-04 10:00:00'
            },
            {
                'id': '2',
                'subject': 'お知らせ【警告】',
                'from': 'info@example.com',
                'date': '2025-12-04 11:00:00'
            },
            {
                'id': '3',
                'subject': '通常のメール',
                'from': 'user@example.com',
                'date': '2025-12-04 12:00:00'
            },
            {
                'id': '4',
                'subject': 'アラート通知',
                'from': 'alert@system.com',
                'date': '2025-12-04 13:00:00'
            },
        ]
    
    def test_filter_by_subject_prefix(self):
        """件名の前方一致フィルター"""
        filters = [
            {'type': 'subject', 'condition': 'prefix', 'value': '【重要】'}
        ]
        email_filter = EmailFilter(filters)
        result = email_filter.filter_emails(self.test_emails)
        
        assert len(result) == 1
        assert result[0]['subject'] == '【重要】システム停止予定'
    
    def test_filter_by_subject_partial(self):
        """件名の部分一致フィルター"""
        filters = [
            {'type': 'subject', 'condition': 'partial', 'value': '【'}
        ]
        email_filter = EmailFilter(filters)
        result = email_filter.filter_emails(self.test_emails)
        
        assert len(result) == 2
        subjects = [e['subject'] for e in result]
        assert '【重要】システム停止予定' in subjects
        assert 'お知らせ【警告】' in subjects
    
    def test_filter_by_from(self):
        """送信元フィルター"""
        filters = [
            {'type': 'from', 'value': 'alert@system.com'}
        ]
        email_filter = EmailFilter(filters)
        result = email_filter.filter_emails(self.test_emails)
        
        assert len(result) == 1
        assert result[0]['from'] == 'alert@system.com'
    
    def test_filter_multiple_conditions_or(self):
        """複数条件フィルター（OR条件）"""
        filters = [
            {'type': 'subject', 'condition': 'prefix', 'value': '【重要】'},
            {'type': 'from', 'value': 'alert@system.com'}
        ]
        email_filter = EmailFilter(filters)
        result = email_filter.filter_emails(self.test_emails)
        
        assert len(result) == 2
        assert any(e['subject'] == '【重要】システム停止予定' for e in result)
        assert any(e['from'] == 'alert@system.com' for e in result)
    
    def test_filter_no_match(self):
        """マッチなしの場合"""
        filters = [
            {'type': 'subject', 'condition': 'prefix', 'value': 'notfound'}
        ]
        email_filter = EmailFilter(filters)
        result = email_filter.filter_emails(self.test_emails)
        
        assert len(result) == 0
    
    def test_filter_empty_filters(self):
        """フィルター条件なしの場合"""
        filters = []
        email_filter = EmailFilter(filters)
        result = email_filter.filter_emails(self.test_emails)
        
        assert len(result) == 0
    
    def test_from_filter_case_insensitive(self):
        """送信元フィルターは大文字小文字を区別しない"""
        filters = [
            {'type': 'from', 'value': 'ALERT@SYSTEM.COM'}
        ]
        email_filter = EmailFilter(filters)
        result = email_filter.filter_emails(self.test_emails)
        
        assert len(result) == 1
        assert result[0]['from'] == 'alert@system.com'


class TestDiscordNotifierTemplate:
    """DiscordNotifierテンプレート機能のテスト"""
    
    def test_template_formatting(self):
        """メッセージテンプレートの置換"""
        from src.notifiers.discord_notifier import DiscordNotifier
        
        template = "件名: {subject}, 送信者: {from_}"
        notifier = DiscordNotifier(
            webhook_url="https://discord.com/api/webhooks/test",
            message_template=template
        )
        
        message = {
            'subject': 'テスト件名',
            'date': '2025-12-04',
            'from': 'test@example.com'
        }
        
        result = notifier._format_message(message)
        assert result == "件名: テスト件名, 送信者: test@example.com"
    
    def test_template_with_newlines(self):
        """改行を含むテンプレート"""
        from src.notifiers.discord_notifier import DiscordNotifier
        
        template = """【メール通知】
件名: {subject}
送信者: {from_}"""
        notifier = DiscordNotifier(
            webhook_url="https://discord.com/api/webhooks/test",
            message_template=template
        )
        
        message = {
            'subject': 'テスト',
            'date': '2025-12-04',
            'from': 'test@example.com'
        }
        
        result = notifier._format_message(message)
        assert '【メール通知】' in result
        assert '件名: テスト' in result
        assert '送信者: test@example.com' in result
    
    def test_default_template(self):
        """デフォルトテンプレート"""
        from src.notifiers.discord_notifier import DiscordNotifier
        
        notifier = DiscordNotifier(
            webhook_url="https://discord.com/api/webhooks/test"
        )
        
        message = {
            'subject': 'テスト件名',
            'date': '2025-12-04',
            'from': 'test@example.com'
        }
        
        result = notifier._format_message(message)
        assert '📧' in result
        assert 'テスト件名' in result
        assert 'test@example.com' in result
