from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, PrivateMessageEvent, MessageSegment, Bot
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

from .notice_monitor import start_notice_monitor, stop_notice_monitor, get_monitor_status
import os
import asyncio
from .scoreboard_image_generator import ScoreboardImageGenerator

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


# --- 积分榜图片群聊触发 ---
scoreboard_trigger = on_message(priority=10, block=False)

@scoreboard_trigger.handle()
async def handle_scoreboard(event: GroupMessageEvent, bot: Bot):
    # 只处理群聊消息
    if not isinstance(event, GroupMessageEvent):
        return
    text = str(event.get_message()).strip()
    if text != "排行榜":
        return

    await scoreboard_trigger.send("正在生成积分榜图片，请稍候……")

    # 生成图片
    try:
        # 这里可根据实际情况调整参数
        generator = ScoreboardImageGenerator(
            base_url="http://ctf.zypc.online:28888",  # 可根据实际API地址调整
            token=None
        )
        game_id = 1  # 可根据实际比赛ID调整，或从配置读取
        result = generator.generate_combined_image(game_id, output_dir="./images", theme="light")
        if not result or not os.path.exists(result['table_image']):
            await scoreboard_trigger.finish("生成积分榜图片失败，请稍后重试。")
            return

        # 发送图片
        img_path = result['table_image']
        await bot.send_group_msg(
            group_id=event.group_id,
            message=Message([MessageSegment.image(f"file:///{os.path.abspath(img_path)}")])
        )
    except Exception as e:
        await scoreboard_trigger.finish(f"生成或发送积分榜图片时出错: {e}")
