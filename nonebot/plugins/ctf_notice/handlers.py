from nonebot import on_command, on_message, logger
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, PrivateMessageEvent, MessageSegment, Bot
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

from .notice_monitor import start_notice_monitor, stop_notice_monitor, get_monitor_status
from .config import SCOREBOARD_KEYWORDS
from .scoreboard import generate_scoreboard
from .ad_detector import detect_advertisement, log_ad_detection, get_ad_detection_summary
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
• /ad_detect <消息> - 检测广告
• /ad_config - 查看广告检测配置

🔧 功能说明:
• 自动监控CTF比赛通知
• 推送所有类型的通知（血条、公告、题目更新等）
• 实时推送到群组
• 30秒检查间隔
• 智能广告检测

✅ 所有群成员都可以使用这些命令"""
    
    await ctf_help.finish(help_text)

# --- 广告检测管理命令 ---
ad_control = on_command("ad_control", aliases={"广告控制", "广告管理"}, priority=5, permission=SUPERUSER)

@ad_control.handle()
async def handle_ad_control(args: Message = CommandArg()):
    """广告检测控制命令"""
    from .config import AD_DETECTION_CONFIG
    
    arg_text = str(args).strip()
    
    if not arg_text:
        # 显示当前状态
        status_text = f"""📊 广告检测状态

🔧 自动撤回: {'✅ 已启用' if AD_DETECTION_CONFIG.get('auto_delete', True) else '❌ 已禁用'}
⚠️ 撤回阈值: {AD_DETECTION_CONFIG.get('delete_threshold', 0.7)}
📢 警告阈值: {AD_DETECTION_CONFIG.get('warning_threshold', 0.5)}

📋 可用命令:
• /ad_control on - 启用自动撤回
• /ad_control off - 禁用自动撤回
• /ad_control threshold 0.8 - 设置撤回阈值
• /ad_control status - 查看检测统计"""
        
        await ad_control.finish(status_text)
    
    elif arg_text == "on":
        AD_DETECTION_CONFIG["auto_delete"] = True
        await ad_control.finish("✅ 已启用广告自动撤回功能")
    
    elif arg_text == "off":
        AD_DETECTION_CONFIG["auto_delete"] = False
        await ad_control.finish("❌ 已禁用广告自动撤回功能")
    
    elif arg_text.startswith("threshold"):
        try:
            parts = arg_text.split()
            if len(parts) >= 2:
                new_threshold = float(parts[1])
                if 0.0 <= new_threshold <= 1.0:
                    AD_DETECTION_CONFIG["delete_threshold"] = new_threshold
                    await ad_control.finish(f"✅ 已设置撤回阈值为: {new_threshold}")
                else:
                    await ad_control.finish("❌ 阈值必须在 0.0 到 1.0 之间")
            else:
                await ad_control.finish("❌ 请提供阈值数值，例如: /ad_control threshold 0.8")
        except ValueError:
            await ad_control.finish("❌ 无效的阈值数值")
    
    elif arg_text == "status":
        summary = get_ad_detection_summary()
        await ad_control.finish(summary)
    
    else:
        await ad_control.finish("❌ 未知命令，使用 /ad_control 查看帮助")

# 广告检测命令
ad_detect = on_command("ad_detect", aliases={"广告检测", "检测广告"}, priority=5)

@ad_detect.handle()
async def handle_ad_detect(args: Message = CommandArg()):
    message_text = args.extract_plain_text().strip()
    
    if not message_text:
        await ad_detect.finish("请输入要检测的消息内容，例如：/ad_detect 这是一条测试消息")
        return
    
    # 执行广告检测
    is_ad, detection_result = detect_advertisement(message_text)
    
    # 构建结果消息
    result_text = f"""🛡️ 广告检测结果


🎯 检测结果: {'🚨 疑似广告' if is_ad else '✅ 正常消息'}
📊 置信度: {detection_result['confidence']:.2f}

🔍 检测详情:"""
    
    if detection_result['reasons']:
        result_text += f"\n• {chr(10).join(detection_result['reasons'])}"
    else:
        result_text += "\n• 未发现广告特征"
    
    # 显示匹配的关键词
    matches = detection_result['keyword_matches']
    if any(matches.values()):
        result_text += "\n\n🔑 关键词匹配:"
        if matches['high_risk']:
            result_text += f"\n• 高风险: {', '.join(matches['high_risk'])}"
        if matches['medium_risk']:
            result_text += f"\n• 中风险: {', '.join(matches['medium_risk'])}"
        if matches['urgency']:
            result_text += f"\n• 紧迫性: {', '.join(matches['urgency'])}"
        if matches['group_numbers']:
            result_text += f"\n• 群号: {', '.join(matches['group_numbers'])}"
    
    await ad_detect.finish(result_text)

# 广告检测配置查看命令
ad_config = on_command("ad_config", aliases={"广告配置", "检测配置"}, priority=5)

@ad_config.handle()
async def handle_ad_config():
    config_summary = get_ad_detection_summary()
    await ad_config.finish(config_summary)

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
        # 发送生成提示
        # await scoreboard_trigger.send("⏳ 正在生成积分榜图片，请稍候...")
        
        # 生成积分榜
        image_path, ranking_info = await generate_scoreboard()
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            await scoreboard_trigger.finish("❌ 积分榜图片生成失败，请稍后重试")
            return
        
        # 检查文件大小
        file_size = os.path.getsize(image_path)
        if file_size > 5 * 1024 * 1024:  # 5MB限制
            await scoreboard_trigger.finish("❌ 图片文件过大，无法发送")
            return
        
        logger.info(f"📊 积分榜图片已生成: {image_path}, 文件大小: {file_size} bytes")
        
        try:
            # 读取图片并转换为 base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
                image_b64 = base64.b64encode(image_data).decode()
            
            # 发送图片消息（使用 base64）
            await scoreboard_trigger.send(MessageSegment.image(f"base64://{image_b64}"))
            logger.info("📊 积分榜图片发送成功")
            
        except Exception as img_error:
            logger.error(f"Base64图片发送失败: {img_error}")
            
            # 尝试使用文件路径发送
            try:
                logger.info("尝试使用文件路径发送图片...")
                await scoreboard_trigger.send(MessageSegment.image(f"file:///{image_path}"))
                logger.info("📊 使用文件路径发送图片成功")
            except Exception as file_error:
                logger.error(f"文件路径发送也失败: {file_error}")
                # 如果图片发送完全失败，至少发送文字信息
                await scoreboard_trigger.send("❌ 图片发送失败，但这里是积分榜信息：")
        
        # 发送排名信息
        await scoreboard_trigger.send(ranking_info)
        
    except Exception as e:
        logger.error(f"生成积分榜时出错: {e}")
        await scoreboard_trigger.finish(f"❌ 生成积分榜时出错: {str(e)}")

# --- y爹检测功能 ---
y_dad_trigger = on_message(priority=15, block=False)

@y_dad_trigger.handle()
async def handle_y_dad_request(event: GroupMessageEvent, bot: Bot):
    """检测到y爹时发送特定内容"""
    # 只处理群聊消息
    if not isinstance(event, GroupMessageEvent):
        return
    
    # 获取消息文本
    message_text = str(event.get_message()).strip()
    
    # 检查是否包含"y爹"
    if "y爹" not in message_text and "y 爹" not in message_text:
        return
    
    # 发送特定内容
    y_dad_response = """🖐️   🖐️      🖐️   🖐️      🖐️   🖐️
\\😭/            \\😭/          \\😭/
👕                👕               👕
👖                👖               👖
👞👞           👞👞         👞👞"""
    
    await y_dad_trigger.send(y_dad_response)

# --- 广告检测功能 ---
ad_monitor = on_message(priority=20, block=False)

@ad_monitor.handle()
async def handle_ad_detection(event: GroupMessageEvent, bot: Bot):
    """自动检测并处理广告消息"""
    # 只处理群聊消息
    if not isinstance(event, GroupMessageEvent):
        return
    
    # 获取消息文本
    message_text = str(event.get_message()).strip()
    
    # 跳过空消息或纯图片消息
    if not message_text or len(message_text) < 10:
        return
    
    # 跳过机器人自己的消息
    if event.user_id == int(bot.self_id):
        return
    
    # 执行广告检测
    is_ad, detection_result = detect_advertisement(message_text)
    
    # 记录检测结果
    log_ad_detection(message_text, detection_result, str(event.user_id))
    
    # 如果检测到广告，自动撤回并发送通知
    # 从配置获取阈值设置
    from .config import AD_DETECTION_CONFIG
    auto_delete = AD_DETECTION_CONFIG.get("auto_delete", True)
    delete_threshold = AD_DETECTION_CONFIG.get("delete_threshold", 0.7)
    warning_threshold = AD_DETECTION_CONFIG.get("warning_threshold", 0.5)
    
    if is_ad and auto_delete and detection_result['confidence'] >= delete_threshold:
        try:
            # 尝试撤回消息
            await bot.delete_msg(message_id=event.message_id)
            logger.warning(f"🚨 已自动撤回广告消息: {message_text[:50]}...")
            
            # 发送撤回通知（私聊给管理员或群内通知）
            warning_message = f"""� 已自动撤回疑似广告消息

�👤 发送者: {event.sender.nickname or event.user_id}
🔍 检测原因: {', '.join(detection_result['reasons'][:3])}

⚠️ 如误判请联系管理员"""
            
            # 发送通知到群内
            await ad_monitor.send(warning_message)
            
        except Exception as e:
            # 如果撤回失败（可能权限不足），则发送警告
            logger.error(f"撤回消息失败: {e}")
            warning_message = f"""🚨 检测到疑似广告但撤回失败

👤 发送者: {event.sender.nickname or event.user_id}
🔍 检测原因: {', '.join(detection_result['reasons'][:2])}
⚠️ 权限不足，请管理员手动处理

消息内容: {message_text[:100]}{'...' if len(message_text) > 100 else ''}"""
            
            await ad_monitor.send(warning_message)
    
    elif is_ad and detection_result['confidence'] >= warning_threshold:
        # 中等风险的消息只发送警告，不撤回
        warning_message = f"""⚠️ 疑似广告消息警告
        
👤 发送者: {event.sender.nickname or event.user_id}
🔍 检测原因: {', '.join(detection_result['reasons'][:2])}

请注意识别和防范广告信息！"""
        
        logger.info(f"⚠️ 中等风险广告检测: {message_text[:50]}...")
        # await ad_monitor.send(warning_message)  # 可选择是否发送中等风险警告

