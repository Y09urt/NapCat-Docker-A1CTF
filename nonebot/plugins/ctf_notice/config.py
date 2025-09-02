# CTF Notice Plugin Configuration

# API配置
NOTICES_API = "https://ctf.zypc.online/api/game/3/notices"
CHECK_INTERVAL = 30  # 检查间隔（秒）

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
