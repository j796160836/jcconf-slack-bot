# JCConf Slack 議程提醒機器人

這是一個自動發送 JCConf 議程提醒的 Slack 機器人，會在每場演講開始前 5 分鐘發送通知訊息。

## 功能特色

- 自動從 JCConf API 獲取最新議程
- 在演講開始前 5 分鐘發送 Slack 提醒
- 支援中英文雙語通知訊息
- 自動過濾休息時間和宣傳議程
- 使用 Slack Webhook 簡化設定
- 使用 .env 檔案管理敏感資訊

## 安裝步驟

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

複製 `.env.example` 為 `.env` 並填入必要資訊：

```bash
cp .env.example .env
```

編輯 `.env` 檔案

### 3. 設定 Slack Webhook

1. 前往你的 Slack 工作區
2. 建立一個 Incoming Webhook：
   - 前往 [Slack Apps](https://api.slack.com/apps) 
   - 建立新的 App 或選擇現有的 App
   - 在 "Incoming Webhooks" 頁面啟用功能
   - 點擊 "Add New Webhook to Workspace"
   - 選擇要發送訊息的頻道
   - 複製產生的 Webhook URL 到 `.env` 檔案

### 4. 執行機器人

#### 方法一：直接執行 Python

```bash
python slack_bot.py
```

#### 方法二：使用 Docker (推薦)

```bash
# 使用部署腳本 (推薦)
./deploy.sh

# 或手動執行 Docker Compose
docker-compose up -d

# 查看日誌
docker-compose logs -f jcconf-slack-bot

# 停止服務
docker-compose down
```

## 訊息格式

機器人會發送以下格式的訊息：

```
下一場演講：`From the JDK 21 25: Langage, API, JVM` 即將在 `401` 開始，過程中如果有想要需要的問題，歡迎在留言處詢問
Next talk: `From the JDK 21–25: Language, API, JVM` is about to begin in `401`. If you have any questions during the session, feel free to ask in the comments section.
```

## 運作原理

1. 每 30 秒從 JCConf API 獲取最新議程
2. 解析演講時間並過濾掉休息時間
3. 檢查是否有演講即將在 5 分鐘內開始
4. 發送提醒訊息到指定的 Slack 頻道
5. 記錄已發送的通知避免重複發送

## 注意事項

- 確保 Slack Webhook URL 正確且有效
- 建議在正式活動前先測試機器人功能
- 機器人會持續運行直到手動停止 (Ctrl+C)
- 所有時間都以台北時區 (Asia/Taipei) 為準

## Docker 部署

### 檔案說明

- `Dockerfile` - Docker 映像檔建構設定
- `docker-compose.yml` - 容器編排設定
- `deploy.sh` - 一鍵部署腳本
- `.dockerignore` - Docker 建構忽略檔案

### Docker 功能特色

- **健康檢查**: 內建 HTTP 健康檢查端點 (port 8080)
- **優雅停止**: 支援 SIGTERM 信號優雅停止
- **資源限制**: 預設記憶體限制 256MB，CPU 限制 0.5 核心
- **日誌管理**: 自動輪轉日誌檔案
- **時區設定**: 自動設定為台北時區

### 常用 Docker 指令

```bash
# 查看容器狀態
docker-compose ps

# 查看即時日誌
docker-compose logs -f jcconf-slack-bot

# 重啟服務
docker-compose restart

# 更新並重新部署
docker-compose down && docker-compose up -d --build

# 進入容器除錯
docker-compose exec jcconf-slack-bot bash

# 檢查健康狀態
curl http://localhost:8080/health
```

## 疑難排解

### 常見錯誤

1. **Slack Webhook 錯誤**: 檢查 Webhook URL 是否正確且有效
2. **網路連線問題**: 檢查是否能正常存取 JCConf API 和 Slack Webhook
3. **Docker 權限問題**: 確保使用者有 Docker 執行權限
4. **時區問題**: 確保容器時區設定為 Asia/Taipei

### 日誌訊息

機器人會輸出詳細的日誌訊息，包括：

- 議程獲取狀態
- 演講解析結果
- 通知發送狀態
- 錯誤訊息

### 監控與除錯

```bash
# 查看容器資源使用情況
docker stats jcconf-slack-bot

# 檢查健康狀態
curl http://localhost:8080/health

# 查看詳細日誌
docker-compose logs --tail=100 jcconf-slack-bot
```

## 授權

MIT License