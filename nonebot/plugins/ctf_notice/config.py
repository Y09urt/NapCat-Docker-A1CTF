# CTF Notice Plugin Configuration

# 导入登录凭据配置
try:
    from .credentials import A1CTF_BASE_URL, A1CTF_USERNAME, A1CTF_PASSWORD
except ImportError:
    print("❌ 未找到 credentials.py 文件！")
    print("请复制 credentials.example.py 为 credentials.py 并填入正确的登录信息")
    A1CTF_BASE_URL = "https://ctf.zypc.online:28888"
    A1CTF_USERNAME = "your_username"
    A1CTF_PASSWORD = "your_password"

# API配置
NOTICES_API = f"{A1CTF_BASE_URL}/api/game/3/notices"
SCOREBOARD_API = f"{A1CTF_BASE_URL}/api/game/3/scoreboard?page=1&size=20"
CHECK_INTERVAL = 30  # 检查间隔（秒）

# 统一的API请求配置
API_CONFIG = {
    # 共享的请求配置
    "headers": {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7',
        'Referer': f'{A1CTF_BASE_URL}/',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
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
    1049849561,  # 你的群组ID
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

# 广告检测配置
AD_DETECTION_CONFIG = {
    # 是否启用自动撤回
    "auto_delete": True,
    
    # 撤回阈值（风险评分超过此值将自动撤回）
    "delete_threshold": 0.7,
    
    # 警告阈值（风险评分超过此值将发送警告）
    "warning_threshold": 0.5,
    
    # 高风险关键词 - 单独出现即认定为广告
    "high_risk_keywords": [
        "广告泛滥", "即将解散", "作废", "紧急通知！！！", 
        "务必进群", "后果自负", "最后一次提醒", "抓紧进群",
        "已报备，管理勿撤回", "导员让转发", "错过重要通知后果自负"
    ],
    
    # 群号模式 - 匹配纯数字群号（8-12位）
    "group_number_pattern": r"\b\d{8,12}\b",
    
    # 中风险关键词 - 多个同时出现才认定
    "medium_risk_keywords": [
        "转移", "新群", "官方群", "通知群", "新生群",
        "军训通知", "新生宿舍", "开学时间", "转换专业",
        "十点前", "抓紧时间", "统计人数", "签到信息"
    ],
    
    # 时间紧迫性词汇
    "urgency_keywords": [
        "紧急", "立即", "马上", "抓紧", "务必", 
        "最后", "截止", "过期", "后果自负"
    ],
    
    # 检测阈值
    "detection_threshold": {
        "high_risk_count": 1,      # 高风险词汇出现1个即判定
        "medium_risk_count": 3,    # 中风险词汇出现3个以上判定
        "urgency_count": 2,        # 紧迫性词汇出现2个以上判定
        "has_group_number": True   # 包含群号模式
    },
    
    # 群卡片检测配置
    "group_card_detection": {
        # 支持的群卡片应用类型
        "card_app_identifiers": [
            "com.tencent.contact.lua",
            "com.tencent.structmsg"
        ],
        
        # 群卡片提示词匹配模式
        "card_prompt_patterns": [
            r"推荐群聊[：:]\s*(.+)",
            r"邀请你加入群聊[：:]\s*(.+)",
            r"群聊推荐[：:]\s*(.+)",
            r"加入群聊[：:]\s*(.+)"
        ],
        
        # 群卡片高风险关键词
        "card_high_risk_keywords": [
            "新生", "大一", "新生群", "新生通知群", "通知群", "答疑群",
            "班级群", "学院群", "校群", "军训通知", "开学通知", "转专业群",
            "2025级", "大一新生", "新生宿舍", "新生军训"
        ],
        
        # 即时广告模式 - 匹配到立即判定为广告
        "card_instant_ad_patterns": [
            r"2025级.*新生.*群",
            r"新生.*通知.*群", 
            r"军训.*通知.*群",
            r"大一.*新生.*群",
            r"新生.*答疑.*群"
        ],
        
        # 群卡片检测阈值
        "card_detection_threshold": 0.6,  # 群卡片检测的置信度阈值（低于普通文本）
        "card_delete_threshold": 0.6      # 群卡片撤回的置信度阈值
    }
}
