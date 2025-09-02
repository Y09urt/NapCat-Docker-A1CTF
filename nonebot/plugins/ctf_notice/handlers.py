from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, PrivateMessageEvent, MessageSegment, Bot
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

from .notice_monitor import start_notice_monitor, stop_notice_monitor, get_monitor_status
from .config import SCOREBOARD_KEYWORDS
from .scoreboard import generate_scoreboard
import os
import asyncio
import base64

# 开始监控命令
ctf_start = on_command("ctf_start", aliases={"ctf开始", "开始监控"}, priority=5)

@ctf_start.handle()
async def handle_start_monitor():
    await start_notice_monitor()
    await ctf_start.finish("✅ CTF通知监控已开始")

# 停止监控命令  
ctf_stop = on_command("ctf_stop", aliases={"ctf停止", "停止监控"}, priority=5)

@ctf_stop.handle()
async def handle_stop_monitor():
    await stop_notice_monitor()
    await ctf_stop.finish("❌ CTF通知监控已停止")

# 查看状态命令
ctf_status = on_command("ctf_status", aliases={"ctf状态", "监控状态"}, priority=5)

@ctf_status.handle()
async def handle_status():
    status = get_monitor_status()
    
    status_text = "运行中 ✅" if status["is_monitoring"] else "已停止 ❌"
    
    message = f"""📊 CTF监控状态

状态: {status_text}
已处理通知: {status["processed_count"]} 条
检查间隔: {status["check_interval"]} 秒
API地址: {status["api_url"]}"""
    
    await ctf_status.finish(message)

# 手动检查命令
ctf_check = on_command("ctf_check", aliases={"ctf检查", "手动检查"}, priority=5)

@ctf_check.handle()
async def handle_manual_check():
    from .notice_monitor import check_new_notices
    
    await ctf_check.send("🔍 正在手动检查新通知...")
    await check_new_notices()
    await ctf_check.finish("✅ 手动检查完成")

# 帮助命令
# 帮助命令
ctf_help = on_command("ctf_help", aliases={"ctf帮助"}, priority=5)

@ctf_help.handle()
async def handle_help():
    help_text = """🎮 CTF通知插件帮助

📋 可用命令:
• /ctf_start - 开始监控
• /ctf_stop - 停止监控  
• /ctf_status - 查看状态
• /ctf_check - 手动检查
• /ctf_help - 显示帮助

🔧 功能说明:
• 自动监控CTF比赛通知
• 推送所有类型的通知（血条、公告、题目更新等）
• 实时推送到群组
• 30秒检查间隔

✅ 所有群成员都可以使用这些命令"""
    
    await ctf_help.finish(help_text)

# --- 积分榜功能 ---
scoreboard_trigger = on_message(priority=10, block=False)

@scoreboard_trigger.handle()
async def handle_scoreboard_request(event: GroupMessageEvent, bot: Bot):
    """处理积分榜请求"""
    # 只处理群聊消息
    if not isinstance(event, GroupMessageEvent):
        return
    
    # 获取消息文本
    message_text = str(event.get_message()).strip()
    
    # 检查是否为积分榜关键词
    if message_text not in SCOREBOARD_KEYWORDS:
        return
    
    # 发送生成提示
    #await scoreboard_trigger.send("正在生成积分榜图片，请稍候……")
    
    try:
        # 生成积分榜
        image_path, ranking_info = await generate_scoreboard()
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            await scoreboard_trigger.finish("❌ 积分榜图片生成失败，请稍后重试")
            return
        
        # 读取图片并转换为 base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode()
        
        # 发送图片消息（使用 base64）
        await scoreboard_trigger.send(MessageSegment.image(f"base64://{image_b64}"))
        
        # 发送排名信息
        await scoreboard_trigger.send(ranking_info)
        
    except Exception as e:
        await scoreboard_trigger.finish(f"❌ 生成积分榜时出错: {str(e)}")

