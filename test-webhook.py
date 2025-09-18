#!/usr/bin/env python3
"""
測試 Slack Webhook 連線的簡單腳本
"""

import os
import json
import requests
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def test_slack_webhook():
    """測試 Slack Webhook"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ 請在 .env 檔案中設定 SLACK_WEBHOOK_URL")
        return False
    
    # 測試訊息
    test_payload = {
        "text": "🧪 測試訊息：JCConf 2025 Slack 機器人連線測試成功！\n\n下一場演講： `測試演講` 即將在 `測試教室` 開始，過程中如果有想要需要的問題，歡迎在留言處詢問\n\nNext talk: `Test Talk` is about to begin in `Test Room`. If you have any questions during the session, feel free to ask in the comments section.\n\n🧪 Test message: JCConf 2025 Slack bot connection test successful!"
    }
    
    try:
        print("🚀 正在發送測試訊息到 Slack...")
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 測試訊息發送成功！")
            print("請檢查你的 Slack 頻道是否收到測試訊息")
            return True
        else:
            print(f"❌ 發送失敗: HTTP {response.status_code}")
            print(f"回應內容: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ 網路錯誤: {e}")
        return False

if __name__ == "__main__":
    print("🔧 JCConf 2025 Slack Webhook 測試工具")
    print("=" * 50)
    
    success = test_slack_webhook()
    
    if success:
        print("\n🎉 測試完成！Webhook 設定正確")
        print("現在可以執行主程式: python slack_bot.py")
    else:
        print("\n❌ 測試失敗，請檢查 Webhook URL 設定")
        print("確認步驟：")
        print("1. 檢查 .env 檔案中的 SLACK_WEBHOOK_URL")
        print("2. 確認 Webhook URL 格式正確")
        print("3. 確認網路連線正常")