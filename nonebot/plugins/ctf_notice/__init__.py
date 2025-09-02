"""
CTF赛事通知插件
实时监控CTF比赛的FirstBlood、SecondBlood、ThirdBlood通知
"""

from nonebot import require, get_driver
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_apscheduler")

from .notice_monitor import start_notice_monitor, stop_notice_monitor
from .handlers import *
from .config import AUTO_START

__plugin_meta__ = PluginMetadata(
    name="CTF赛事通知",
    description="实时播报CTF比赛的FirstBlood、SecondBlood、ThirdBlood通知",
    usage="发送 '/ctf_start' 开始监控，'/ctf_stop' 停止监控",
    config=None,
)

driver = get_driver()

@driver.on_startup
async def _():
    """启动时自动开始监控"""
    if AUTO_START:
        await start_notice_monitor()

@driver.on_shutdown
async def _():
    """关闭时停止监控"""
    await stop_notice_monitor()
