#!/usr/bin/env python3
"""
JCConf 2025 Slack 議程提醒機器人
在每場演講開始前 5 分鐘發送提醒訊息
"""

import os
import json
import time
import requests
import logging
import signal
import sys
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import pytz
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定日誌
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            'logs/bot.log') if os.path.exists('logs') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """簡單的健康檢查 HTTP 處理器"""

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'jcconf-slack-bot'
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # 抑制健康檢查的日誌輸出
        pass


class JCConfSlackBot:
    def __init__(self):
        """初始化 Slack 機器人"""
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.schedule_url = os.getenv('SCHEDULE_URL',
                                      'https://pretalx.com/jcconf-2025/schedule/widgets/schedule.json')

        if not self.slack_webhook_url:
            raise ValueError("請在 .env 檔案中設定 SLACK_WEBHOOK_URL")

        self.taipei_tz = pytz.timezone('Asia/Taipei')
        self.sent_notifications = set()  # 追蹤已發送的通知
        self.running = True  # 控制主迴圈
        self.health_server = None  # 健康檢查伺服器

        # 設定信號處理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """處理停止信號"""
        logger.info(f"收到信號 {signum}，正在優雅地停止機器人...")
        self.running = False
        if self.health_server:
            self.health_server.shutdown()

    def start_health_server(self):
        """啟動健康檢查伺服器"""
        try:
            self.health_server = HTTPServer(
                ('0.0.0.0', 8080), HealthCheckHandler)
            health_thread = threading.Thread(
                target=self.health_server.serve_forever, daemon=True)
            health_thread.start()
            logger.info("健康檢查伺服器已啟動在 port 8080")
        except Exception as e:
            logger.warning(f"無法啟動健康檢查伺服器: {e}")

    def fetch_schedule(self) -> Optional[Dict]:
        """從 API 獲取議程資料"""
        try:
            logger.info(f"正在獲取議程資料: {self.schedule_url}")
            response = requests.get(self.schedule_url, timeout=10)
            response.raise_for_status()

            schedule_data = response.json()
            logger.info(f"成功獲取 {len(schedule_data.get('talks', []))} 場演講資料")
            return schedule_data

        except requests.RequestException as e:
            logger.error(f"獲取議程資料失敗: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析 JSON 資料失敗: {e}")
            return None

    def get_room_name(self, room_id: int, rooms_data: List[Dict]) -> str:
        """根據房間 ID 獲取房間名稱"""
        if not room_id or not rooms_data:
            return "未知地點"

        for room in rooms_data:
            if room.get('id') == room_id:
                # 優先使用中文名稱，如果沒有則使用英文名稱
                name = room.get('name', {})
                if isinstance(name, dict):
                    return name.get('zh-hant', name.get('zh-tw', name.get('en', '未知地點')))
                else:
                    return str(name) if name else "未知地點"

        return f"教室 {room_id}"

    def parse_talks(self, schedule_data: Dict) -> List[Dict]:
        """解析演講資料，過濾掉休息時間和宣傳議程"""
        talks = []
        rooms_data = schedule_data.get('rooms', [])

        for talk in schedule_data.get('talks', []):
            # 跳過休息時間和宣傳議程
            if (talk.get('title', '').lower() in ['break', 'opening'] or
                '宣傳議程' in talk.get('title', '') or
                    not talk.get('speakers')):  # 沒有講者的通常是休息時間
                continue

            # 解析時間
            start_time_str = talk.get('start')
            if not start_time_str:
                continue

            try:
                start_time = datetime.fromisoformat(
                    start_time_str.replace('Z', '+00:00'))
                # 確保時間是台北時區
                if start_time.tzinfo is None:
                    start_time = self.taipei_tz.localize(start_time)
                else:
                    start_time = start_time.astimezone(self.taipei_tz)

                # 獲取房間名稱
                room_id = talk.get('room')
                room_name = self.get_room_name(room_id, rooms_data)

                talks.append({
                    'code': talk.get('code'),
                    'title': talk.get('title'),
                    'start_time': start_time,
                    'speakers': talk.get('speakers', []),
                    'room_id': room_id,
                    'room_name': room_name,
                    'abstract': talk.get('abstract', '')
                })

            except ValueError as e:
                logger.warning(f"無法解析時間 {start_time_str}: {e}")
                continue

        # 按時間排序
        talks.sort(key=lambda x: x['start_time'])
        return talks

    def format_notification_message(self, talk: Dict) -> Dict:
        """格式化通知訊息"""
        title = talk['title']
        room_name = talk['room_name']

        message = f"""下一場演講： `{title}` 即將在 `{room_name}` 開始，過程中如果有想要需要的問題，歡迎在留言處詢問
Next talk: `{title}` is about to begin in `{room_name}`. If you have any questions during the session, feel free to ask in the comments section."""

        return {"text": message}

    def send_slack_message(self, payload: Dict) -> bool:
        """發送 Slack 訊息"""
        try:
            response = requests.post(
                self.slack_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                logger.info("成功發送訊息到 Slack")
                return True
            else:
                logger.error(
                    f"發送訊息失敗: HTTP {response.status_code} - {response.text}")
                return False

        except requests.RequestException as e:
            logger.error(f"發送 Slack 訊息時發生網路錯誤: {e}")
            return False

    def check_and_send_notifications(self, talks: List[Dict]):
        """檢查是否需要發送通知"""
        now = datetime.now(self.taipei_tz)

        for talk in talks:
            talk_code = talk['code']
            start_time = talk['start_time']

            # 計算提醒時間（開始前 5 分鐘）
            notification_time = start_time - timedelta(minutes=5)

            # 檢查是否到了發送通知的時間
            if (now >= notification_time and
                now < start_time and
                    talk_code not in self.sent_notifications):

                logger.info(
                    f"準備發送通知: {talk['title']} (地點: {talk['room_name']}, 開始時間: {start_time})")

                payload = self.format_notification_message(talk)

                if self.send_slack_message(payload):
                    self.sent_notifications.add(talk_code)
                    logger.info(
                        f"已發送通知: {talk['title']} ({talk['room_name']})")
                else:
                    logger.error(
                        f"發送通知失敗: {talk['title']} ({talk['room_name']})")

    def run(self):
        """主要執行迴圈"""
        logger.info("JCConf 2025 Slack 機器人啟動")

        # 啟動健康檢查伺服器
        self.start_health_server()

        while self.running:
            try:
                # 獲取最新議程
                schedule_data = self.fetch_schedule()
                if not schedule_data:
                    logger.warning("無法獲取議程資料，等待 60 秒後重試")
                    self._sleep_with_interrupt_check(60)
                    continue

                # 解析演講資料
                talks = self.parse_talks(schedule_data)
                logger.info(f"找到 {len(talks)} 場演講")

                # 檢查並發送通知
                self.check_and_send_notifications(talks)

                # 等待 30 秒後再次檢查
                self._sleep_with_interrupt_check(30)

            except Exception as e:
                logger.error(f"執行過程中發生錯誤: {e}")
                self._sleep_with_interrupt_check(60)  # 發生錯誤時等待較長時間

        logger.info("機器人已停止")

    def _sleep_with_interrupt_check(self, seconds):
        """可中斷的睡眠函數"""
        for _ in range(seconds):
            if not self.running:
                break
            time.sleep(1)


def main():
    """主函數"""
    try:
        bot = JCConfSlackBot()
        bot.run()
    except Exception as e:
        logger.error(f"機器人啟動失敗: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
