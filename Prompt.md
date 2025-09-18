請用 python 寫一個發送 slack 訊息的機器人，規則如下：

1. 使用 .env 存取環境變數與機密資訊
2. 程式啟動時，先抓取以下網址的內容 json

https://pretalx.com/jcconf-2025/schedule/widgets/schedule.json

該 json 格式如下

```
{
  "talks": [
    {
      "code": "U8DEVV",
      "id": 1337568,
      "title": "Opening",
      "abstract": "Opening",
      "speakers": [],
      "track": 5775,
      "start": "2025-09-19T09:25:00+08:00",
      "end": "2025-09-19T09:35:00+08:00",
      "room": 4459,
      "duration": 45,
      "updated": "2025-09-15T01:49:54.783764+00:00",
      "state": null,
      "do_not_record": null
    },
    {
      "code": "KRNWHV",
      "id": 1337569,
      "title": "宣傳議程 - LINE",
      "abstract": "",
      "speakers": [],
      "track": 5773,
      "start": "2025-09-19T09:35:00+08:00",
      "end": "2025-09-19T09:40:00+08:00",
      "room": 4459,
      "duration": 5,
      "updated": "2025-09-15T01:49:54.783802+00:00",
      "state": null,
      "do_not_record": null
    },
    {
      "code": "8PBNXM",
      "id": 1337570,
      "title": "From the JDK 21 25: Langage, API, JVM (EN)",
      "abstract": "",
      "speakers": [
        "JZRPNT"
      ],
      "track": 5775,
      "start": "2025-09-19T09:40:00+08:00",
      "end": "2025-09-19T10:25:00+08:00",
      "room": 4459,
      "duration": 45,
      "updated": "2025-09-15T01:49:54.783849+00:00",
      "state": null,
      "do_not_record": null
    },
    {
      "code": "XBXDYR",
      "id": 1337571,
      "title": "Break",
      "abstract": "Break",
      "speakers": [],
      "track": null,
      "start": "2025-09-19T10:25:00+08:00",
      "end": "2025-09-19T10:35:00+08:00",
      "room": 4459,
      "duration": 15,
      "updated": "2025-09-15T01:49:54.783871+00:00",
      "state": null,
      "do_not_record": null
    },
    {
      "code": "XEQMGG",
      "id": 1337572,
      "title": "宣傳議程 - 宏庭科技",
      "abstract": "",
      "speakers": [],
      "track": 5773,
      "start": "2025-09-19T10:35:00+08:00",
      "end": "2025-09-19T10:40:00+08:00",
      "room": 4459,
      "duration": 5,
      "updated": "2025-09-15T01:49:54.783892+00:00",
      "state": null,
      "do_not_record": null
    }
  ],
  "version": "0.24",
  "timezone": "Asia/Taipei",
  "event_start": "2025-09-19",
  "event_end": "2025-09-19",
  "tracks": [
    {
      "id": 5773,
      "name": {
        "en": "Promotion"
      },
      "description": {},
      "color": "#C19D0C"
    },
    {
      "id": 5774,
      "name": {
        "en": "402AB",
        "zh-tw": "402AB"
      },
      "description": {},
      "color": "#268785"
    },
    {
      "id": 5775,
      "name": {
        "en": "401",
        "zh-tw": "401"
      },
      "description": {},
      "color": "#D0104C"
    },
    {
      "id": 5776,
      "name": {
        "en": "402CD",
        "zh-tw": "402CD"
      },
      "description": {},
      "color": "#1B813E"
    },
    {
      "id": 5777,
      "name": {
        "zh-tw": "203"
      },
      "description": {},
      "color": "#954A45"
    },
    {
      "id": 5778,
      "name": {
        "en": "403",
        "zh-tw": "403"
      },
      "description": {},
      "color": "#574C57"
    }
  ],
  "rooms": [
    {
      "id": 4459,
      "name": {
        "en": "401",
        "zh-hant": "401"
      },
      "description": {}
    },
    {
      "id": 4460,
      "name": {
        "en": "402AB",
        "zh-hant": "402AB"
      },
      "description": {}
    },
    {
      "id": 4461,
      "name": {
        "en": "402CD",
        "zh-hant": "402CD"
      },
      "description": {}
    },
    {
      "id": 4462,
      "name": {
        "en": "203",
        "zh-hant": "203"
      },
      "description": {}
    },
    {
      "id": 4463,
      "name": {
        "en": "403",
        "zh-hant": "403"
      },
      "description": {}
    }
  ],
  "speakers": [
    {
      "code": "YP9HWC",
      "name": "許子謙",
      "avatar": "",
      "avatar_thumbnail_default": "",
      "avatar_thumbnail_tiny": ""
    },
    {
      "code": "7KG87A",
      "name": "陳冠緯",
      "avatar": "https://pretalx.com/media/avatars/7KG87A_6jQuab7.jpg",
      "avatar_thumbnail_default": "https://pretalx.com/media/avatars/7KG87A_6jQuab7_thumbnail.jpg",
      "avatar_thumbnail_tiny": "https://pretalx.com/media/avatars/7KG87A_6jQuab7_thumbnail_tiny.jpg"
    },
    {
      "code": "UB7VAB",
      "name": "Rijo Sam",
      "avatar": "https://pretalx.com/media/avatars/UB7VAB_oKSmZAp.jpg",
      "avatar_thumbnail_default": "https://pretalx.com/media/avatars/UB7VAB_oKSmZAp_thumbnail_default.jpg",
      "avatar_thumbnail_tiny": "https://pretalx.com/media/avatars/UB7VAB_oKSmZAp_thumbnail_tiny.jpg"
    }
  ]
}
```

根據議程的時間的前 5 分鐘在指定的頻道，發送訊息

```
下一場演講：`From the JDK 21 25: Langage, API, JVM` 即將開始，過程中如果有想要需要的問題，歡迎在留言處詢問
Next talk: `From the JDK 21–25: Language, API, JVM is about to begin.`
If you have any questions during the session, feel free to ask in the comments section.
```

用以下方式發訊息即可
POST 到指定網址

https://hooks.slack.com/services/xxxxxxxxx/xxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxx

格式為 json

內容為

```
{"text": "下一場演講： `title` 即將開始，過程中如果有想要需要的問題，歡迎在留言處詢問
Next talk: `title` is about to begin. If you have any questions during the session, feel free to ask in the comments section."}
```