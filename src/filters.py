"""メールフィルタリングモジュール

メール条件に基づいてメールをフィルタリングする。
"""

import logging
from typing import List, Dict, Any, Callable


logger = logging.getLogger(__name__)


class EmailFilter:
    """メールフィルタリングクラス
    
    複数のフィルター条件を組み合わせてメールをフィルタリングする。
    """
    
    def __init__(self, filters: List[Dict[str, Any]]):
        """メールフィルターを初期化
        
        Args:
            filters: フィルター設定のリスト
                [
                    {
                        "type": "subject" | "from",
                        "condition": "prefix" | "partial"（typeが"subject"の場合）,
                        "value": "フィルタリング値"
                    },
                    ...
                ]
        """
        self.filters = filters
    
    def filter_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """メールをフィルタリング
        
        複数のフィルター条件が指定されている場合、
        いずれかの条件にマッチしたメールを返す（OR条件）
        
        Args:
            emails: メールのリスト
        
        Returns:
            list: フィルタリングされたメールのリスト
        """
        if not self.filters:
            return []
        
        filtered = []
        for email in emails:
            for filter_config in self.filters:
                if self._matches_filter(email, filter_config):
                    filtered.append(email)
                    break  # 1つのフィルターにマッチしたら次のメールへ
        
        if filtered:
            logger.info(f"{len(filtered)} emails matched the filter condition")
        
        return filtered
    
    def _matches_filter(self, email: Dict[str, Any], filter_config: Dict[str, Any]) -> bool:
        """メールがフィルター条件にマッチするかチェック
        
        Args:
            email: メール情報
            filter_config: フィルター設定
        
        Returns:
            bool: マッチしたらTrue
        """
        filter_type = filter_config.get("type")
        
        if filter_type == "subject":
            return self._matches_subject_filter(email, filter_config)
        elif filter_type == "from":
            return self._matches_from_filter(email, filter_config)
        else:
            logger.warning(f"Unknown filter type: {filter_type}")
            return False
    
    def _matches_subject_filter(self, email: Dict[str, Any], filter_config: Dict[str, Any]) -> bool:
        """件名フィルターをチェック
        
        Args:
            email: メール情報
            filter_config: フィルター設定
        
        Returns:
            bool: マッチしたらTrue
        """
        condition = filter_config.get("condition", "prefix")
        value = filter_config.get("value", "")
        subject = email.get("subject", "")
        
        if condition == "prefix":
            return subject.startswith(value)
        elif condition == "partial":
            return value in subject
        else:
            logger.warning(f"Unknown subject condition: {condition}")
            return False
    
    def _matches_from_filter(self, email: Dict[str, Any], filter_config: Dict[str, Any]) -> bool:
        """送信元フィルターをチェック
        
        Args:
            email: メール情報
            filter_config: フィルター設定
        
        Returns:
            bool: マッチしたらTrue
        """
        value = filter_config.get("value", "")
        from_addr = email.get("from", "")
        
        # 送信元フィルターは完全一致で対応
        return value.lower() in from_addr.lower()
