"""Configクラスの単体テスト"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from src.config import Config


@pytest.fixture
def temp_settings_file():
    """一時的な設定ファイルを作成"""
    settings = {
        "mail": {
            "host": "imap.example.com",
            "port": 993,
            "check_period_minutes": 30
        },
        "filters": [
            {"type": "subject", "condition": "prefix", "value": "[TEST]"}
        ],
        "notifiers": {
            "discord": {
                "enabled": True
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(settings, f)
        temp_path = f.name
    
    yield temp_path
    
    # クリーンアップ
    os.unlink(temp_path)


@pytest.fixture
def env_vars():
    """環境変数を設定"""
    with patch.dict(os.environ, {
        "MAIL_USER": "test@example.com",
        "MAIL_PASSWORD": "test-password",
        "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/test"
    }):
        yield


def test_config_load_yaml(temp_settings_file, env_vars):
    """YAML設定ファイルが正しく読み込まれるか"""
    config = Config(settings_path=temp_settings_file)
    
    assert config.mail_host == "imap.example.com"
    assert config.mail_port == 993
    assert config.check_period_minutes == 30
    assert config.discord_enabled is True


def test_config_load_env_vars(temp_settings_file, env_vars):
    """環境変数が正しく読み込まれるか"""
    config = Config(settings_path=temp_settings_file)
    
    assert config.mail_user == "test@example.com"
    assert config.mail_password == "test-password"
    assert config.discord_webhook_url == "https://discord.com/api/webhooks/test"


def test_config_missing_env_var(temp_settings_file):
    """環境変数が設定されていない場合にエラーを出すか"""
    with patch.dict(os.environ, {}, clear=True):
        config = Config(settings_path=temp_settings_file)
        
        with pytest.raises(ValueError, match="環境変数 MAIL_USER が設定されていません"):
            _ = config.mail_user


def test_config_file_not_found(env_vars):
    """設定ファイルが存在しない場合にエラーを出すか"""
    with pytest.raises(FileNotFoundError):
        Config(settings_path="/nonexistent/path/settings.yaml")


def test_config_default_path(env_vars):
    """デフォルトパスで設定ファイルを読み込むか"""
    # プロジェクトルートのconfig/settings.yamlが存在する場合のテスト
    # 実際のファイルが存在しない場合はスキップ
    project_root = Path(__file__).parent.parent.parent
    default_settings = project_root / "config" / "settings.yaml"
    
    if default_settings.exists():
        config = Config()
        assert config.mail_host is not None
        assert config.mail_port is not None
