# CTF Notice Plugin Configuration

# API配置
NOTICES_API = "https://ctf.zypc.online/api/game/3/notices"
SCOREBOARD_API = "https://ctf.zypc.online:28888/api/game/3/scoreboard?page=1&size=20"
CHECK_INTERVAL = 30  # 检查间隔（秒）

# 统一的API请求配置
API_CONFIG = {
    # 共享的请求配置
    "headers": {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7',
        'Referer': 'https://ctf.zypc.online:28888/',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
    },
    "cookies": {
        'i18next': 'en',
        'a1token': 'eyJhbGciOiJSUzM4NCIsInR5cCI6IkpXVCJ9.eyJKV1RWZXJzaW9uIjoiWlJmbElZWU1EYzgoV1E4TyIsIlJvbGUiOiJBRE1JTiIsIlVzZXJJRCI6IjhlYWI3N2M0LTViYWMtNDg1Yi1iOGJiLTg0ZTc0MjNlYjZiYyIsIlVzZXJOYW1lIjoiWW9ndXJ0IiwiZXhwIjoxNzU2ODI4ODE5LCJvcmlnX2lhdCI6MTc1NjY1NjAxOX0.wDkQJdaSlMM5D1VLF6s2UP50YIB6TY8iBqsKwHdq0FPppVgKx4Y2eLwpwN6H0pnygOXR8gsRev538hQp-rKQFVcE6PTrk104Wo0UAHR5wPTvrJ4FrpZ_ERZBlJeDsBEjXER945z_D6O88NSwXCacngybPQfGxFDb8uYGJXAR5Tqs22ksW-8eWK5r3hdv9JmdOi4wIoMNV49Y7WiXTVMKCPzAgrTBbWfSR5kEMrg0Kj4ymFsETMk4wwJtg8PxKO0ffWh67jCmbIPqkz7bjbRIqxsnaFORuCoH2cNZH1_2L_-43y5ZruldVrCOvoz0v-N96K0jdOE2bY6DKZuXEkAIbw'
    },
    # 不同API的特定配置
    "notices": {
        "url": NOTICES_API,
        "timeout": 10
    },
    "scoreboard": {
        "url": SCOREBOARD_API,
        "timeout": 30
    }
}

# 积分榜图片保存配置
SCOREBOARD_IMAGE_CONFIG = {
    "save_dir": "/app/nonebot/scoreboard",
    "filename": "scoreboard.png"
}

# 群组配置 - 需要接收通知的群组ID列表
# 留空则发送到所有群组
TARGET_GROUPS = [
    313901893,  # 你的群组ID
    # 123456789,  # 示例群组ID
    # 987654321,  # 示例群组ID
]

# 通知过滤配置 - 设置为空列表表示推送所有类型的通知
NOTICE_CATEGORIES = [
    # "FirstBlood",
    # "SecondBlood", 
    # "ThirdBlood",
    # "NewHint",
    # 留空表示推送所有类型的通知
]

# 消息模板配置
MESSAGE_TEMPLATES = {
    "FirstBlood": "🥇 First Blood!",
    "SecondBlood": "🥈 Second Blood!",
    "ThirdBlood": "🥉 Third Blood!",
    "NewHint": "💡 Challenge [{challenge_name}] added a new hint"
}

# 是否在启动时自动开始监控
AUTO_START = True

# 积分榜触发关键词
SCOREBOARD_KEYWORDS = ["排行榜", "积分榜", "scoreboard"]
