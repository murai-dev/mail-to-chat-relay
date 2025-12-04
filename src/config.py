"""設定管理モジュール

環境変数とYAML設定ファイルを読み込んで統合管理する。
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from dotenv import load_dotenv


class Config:
    """アプリケーション設定を管理するクラス
    
    環境変数(.env)から機密情報を読み込み、
    設定ファイル(settings.yaml)から動作設定を読み込む。
    """
    
    def __init__(self, settings_path: Optional[str] = None):
        """設定を初期化
        
        Args:
            settings_path: settings.yamlのパス。Noneの場合はデフォルトパスを使用
        """
        # 環境変数を読み込み
        load_dotenv()
        
        # 設定ファイルのパスを決定
        if settings_path is None:
            # プロジェクトルートのconfigディレクトリから読み込み
            project_root = Path(__file__).parent.parent
            settings_path = project_root / "config" / "settings.yaml"
        
        # YAML設定ファイルを読み込み
        self._settings = self._load_yaml(settings_path)
        
    def _load_yaml(self, path: Union[Path, str]) -> Dict[str, Any]:
        """YAML設定ファイルを読み込む
        
        Args:
            path: YAMLファイルのパス
            
        Returns:
            読み込んだ設定の辞書
            
        Raises:
            FileNotFoundError: ファイルが存在しない場合
            yaml.YAMLError: YAML解析エラーの場合
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    # メール設定
    @property
    def mail_host(self) -> str:
        """IMAPサーバーのホスト名"""
        return self._settings["mail"]["host"]
    
    @property
    def mail_port(self) -> int:
        """IMAPサーバーのポート番号"""
        return self._settings["mail"]["port"]
    
    @property
    def mail_user(self) -> str:
        """メールアカウントのユーザー名（環境変数から取得）"""
        user = os.getenv("MAIL_USER")
        if not user:
            raise ValueError("環境変数 MAIL_USER が設定されていません")
        return user
    
    @property
    def mail_password(self) -> str:
        """メールアカウントのパスワード（環境変数から取得）"""
        password = os.getenv("MAIL_PASSWORD")
        if not password:
            raise ValueError("環境変数 MAIL_PASSWORD が設定されていません")
        return password
    
    
    @property
    def check_interval_minutes(self) -> int:
        """cron実行間隔（分）"""
        return self._settings["mail"].get("check_interval_minutes", 30)
    
    # フィルター設定
    @property
    def filters(self) -> list:
        """フィルター設定リスト
        
        Returns:
            list: フィルター条件のリスト
                [
                    {
                        "type": "subject" | "from",
                        "condition": "prefix" | "partial"（typeが"subject"の場合）,
                        "value": "フィルタリング値"
                    },
                    ...
                ]
        """
        return self._settings.get("filters", [])
    
    # 通知設定
    @property
    def discord_enabled(self) -> bool:
        """Discord通知が有効かどうか"""
        return self._settings["notifiers"]["discord"]["enabled"]
    
    @property
    def discord_webhook_url(self) -> str:
        """Discord Webhook URL（環境変数から取得）"""
        url = os.getenv("DISCORD_WEBHOOK_URL")
        if not url:
            raise ValueError("環境変数 DISCORD_WEBHOOK_URL が設定されていません")
        return url
    
    @property
    def discord_channel_id(self) -> str:
        """Discord チャンネルID"""
        return self._settings["notifiers"]["discord"].get("channel_id")
    
    @property
    def discord_message_template(self) -> str:
        """Discord 通知メッセージテンプレート"""
        return self._settings["notifiers"]["discord"].get(
            "message_template",
            "📧 **新着メール通知**\n**件名:** {subject}\n**受信日時:** {date}\n**送信者:** {from}"
        )
