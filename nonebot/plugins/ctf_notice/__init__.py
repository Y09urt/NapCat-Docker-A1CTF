"""
CTF通知插件
基于A1CTF源码重构的CTF比赛通知和积分榜插件

主要功能:
- 多组别积分榜支持
- 实时通知监控
- 题目状态跟踪
- 广告消息检测
- 完整的A1CTF API集成

使用说明:
- 发送 '积分榜' 查看比赛积分榜
- 发送 '组别' 查看比赛组别信息
- 发送 '题目' 查看题目列表
- 发送 '状态' 查看插件运行状态
- 发送 '帮助' 查看使用帮助

管理员命令:
- 发送 '开始监控' 启动通知监控
- 发送 '停止监控' 停止通知监控
- 发送 '重载配置' 重新加载配置

配置文件:
- config.py: 主配置文件
- credentials.py: 登录凭据（从credentials.example.py复制）

技术架构:
- a1ctf_core.py: 核心数据模型和认证客户端
- a1ctf_service.py: API服务层
- handlers.py: 消息处理器
- scoreboard.py: 积分榜生成器
- notice_monitor.py: 通知监控器
- ad_detector.py: 广告检测器

项目地址: https://github.com/Y09urt/A1CTF_
"""

import logging
from nonebot.plugin import PluginMetadata

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="CTF通知插件",
    description="基于A1CTF源码重构的CTF比赛通知和积分榜插件",
    usage="""
🤖 CTF通知插件使用帮助

📊 查询命令:
• 积分榜/排行榜 - 查看比赛积分榜
• 组别/分组 - 查看比赛组别信息  
• 题目/challenges - 查看题目列表
• 状态/status - 查看插件运行状态

🔧 管理命令 (仅管理员):
• 开始监控 - 启动通知监控
• 停止监控 - 停止通知监控
• 重载配置 - 重新加载配置

💡 功能特性:
✅ 多组别积分榜支持
✅ 自动通知监控
✅ 题目状态跟踪
✅ 广告消息检测

📞 问题反馈: https://github.com/Y09urt/A1CTF_
    """,
    type="application",
    homepage="https://github.com/Y09urt/A1CTF_",
    supported_adapters={"~onebot.v11"},
    config=None,
    extra={
        "author": "CTF Team",
        "version": "2.0.0",
        "license": "MIT"
    }
)

# 配置日志
logger = logging.getLogger(__name__)

# 导入处理器以注册事件处理
try:
    from . import handlers
    logger.info("CTF通知插件处理器加载成功")
except ImportError as e:
    logger.error(f"CTF通知插件处理器加载失败: {e}")

# 导入配置
try:
    from .config import A1CTF_CONFIG, MONITOR_CONFIG, FEATURES
    logger.info("CTF通知插件配置加载成功")
    
    # 显示配置概要
    logger.info(f"API地址: {A1CTF_CONFIG.get('base_url', 'Unknown')}")
    logger.info(f"比赛ID: {A1CTF_CONFIG.get('game_id', 'Unknown')}")
    logger.info(f"目标群组: {len(MONITOR_CONFIG.get('target_groups', []))}")
    
    enabled_features = [k for k, v in FEATURES.items() if v]
    logger.info(f"启用功能: {', '.join(enabled_features)}")
    
except ImportError as e:
    logger.error(f"CTF通知插件配置加载失败: {e}")

# 导入核心服务
try:
    from .a1ctf_service import A1CTFService
    from .scoreboard import ScoreboardGenerator
    from .notice_monitor import NoticeMonitor
    logger.info("CTF通知插件核心服务加载成功")
except ImportError as e:
    logger.error(f"CTF通知插件核心服务加载失败: {e}")

# 版本信息
__version__ = "2.0.0"
__author__ = "CTF Team"
__license__ = "MIT"

# 导出常用类和函数
__all__ = [
    "A1CTFService",
    "ScoreboardGenerator", 
    "NoticeMonitor",
    "__plugin_meta__",
    "__version__"
]

logger.info(f"CTF通知插件 v{__version__} 加载完成")
