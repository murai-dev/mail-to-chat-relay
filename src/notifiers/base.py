"""通知機能の基底クラス

各通知サービスの共通インターフェースを定義する。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseNotifier(ABC):
    """通知機能の抽象基底クラス
    
    各通知サービス（Discord、Slack、LINEなど）の共通インターフェース。
    新しい通知サービスを追加する場合は、このクラスを継承する。
    """
    
    @abstractmethod
    def send(self, message: Dict[str, Any]) -> bool:
        """通知を送信する
        
        Args:
            message: 送信するメッセージ情報
                {
                    "subject": "メールの件名",
                    "date": "受信日時",
                    "from": "送信者" (オプション)
                }
        
        Returns:
            bool: 送信成功時はTrue、失敗時はFalse
        
        Raises:
            NotImplementedError: サブクラスで実装が必要
        """
        raise NotImplementedError("send method must be implemented")
