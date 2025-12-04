#!/usr/bin/env python3
"""crontab設定を自動生成するスクリプト

settings.yamlのcheck_interval_minutesに基づいて、
crontab実行パターンを自動生成する。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import Config


def generate_cron_pattern(interval_minutes: int) -> str:
    """実行間隔に基づいてcronパターンを生成
    
    Args:
        interval_minutes: 実行間隔（分）
    
    Returns:
        str: cron形式のパターン
    """
    if interval_minutes <= 0:
        raise ValueError(f"実行間隔は1以上である必要があります: {interval_minutes}")
    
    if interval_minutes == 1:
        return "*"
    elif interval_minutes <= 59:
        return f"*/{interval_minutes}"
    elif interval_minutes % 60 == 0:
        # 60分の倍数の場合は毎時実行
        return "0"
    else:
        # 60分以上で60の倍数ではない場合は、分単位で指定
        # (例: 90分 = 毎時0分と毎時30分に実行)
        divisor = 60
        raise ValueError(
            f"60の倍数か60分以内の値を指定してください（指定値: {interval_minutes}分）"
        )


def generate_crontab_line(interval_minutes: int) -> str:
    """crontab実行行を生成
    
    Args:
        interval_minutes: 実行間隔（分）
    
    Returns:
        str: crontab実行行
    """
    cron_pattern = generate_cron_pattern(interval_minutes)
    
    # crontab行を生成
    # 形式: <分> <時> <日> <月> <曜日> <ユーザー> <コマンド>
    crontab_line = f"{cron_pattern} * * * * root cd /app && python3 src/main.py >> /var/log/mail-relay.log 2>&1"
    
    return crontab_line


def main():
    """メイン処理"""
    try:
        # 設定を読み込み
        config = Config(settings_path=str(project_root / "config" / "settings.yaml"))
        interval = config.check_interval_minutes
        
        # crontab行を生成
        crontab_line = generate_crontab_line(interval)
        
        # 標準出力に出力
        print(crontab_line)
        
        return 0
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
