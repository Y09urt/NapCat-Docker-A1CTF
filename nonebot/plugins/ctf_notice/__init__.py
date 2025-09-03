"""
CTF赛事通知插件
实时监控CTF比赛的FirstBlood、SecondBlood、ThirdBlood通知
"""

from nonebot import require, get_driver
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_apscheduler")

from .notice_monitor import start_notice_monitor, stop_notice_monitor
from .handlers import *
from .config import AUTO_START, A1CTF_BASE_URL, A1CTF_USERNAME, A1CTF_PASSWORD
from .a1ctf_client import initialize_a1ctf_client, close_a1ctf_client

__plugin_meta__ = PluginMetadata(
    name="CTF赛事通知",
    description="实时播报CTF比赛的FirstBlood、SecondBlood、ThirdBlood通知",
    usage="发送 '/ctf_start' 开始监控，'/ctf_stop' 停止监控",
    config=None,
)

driver = get_driver()

@driver.on_startup
async def _():
    """启动时初始化A1CTF客户端并开始监控"""
    await initialize_a1ctf_client(
        base_url=A1CTF_BASE_URL,
        username=A1CTF_USERNAME,
        password=A1CTF_PASSWORD
    )
    if AUTO_START:
        await start_notice_monitor()

@driver.on_shutdown
async def _():
    """关闭时停止监控并关闭客户端会话"""
    await stop_notice_monitor()
    await close_a1ctf_client()
