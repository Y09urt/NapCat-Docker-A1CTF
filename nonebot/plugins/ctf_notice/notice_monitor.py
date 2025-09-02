import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Set
from nonebot import get_bot, logger
from nonebot_plugin_apscheduler import scheduler

from .config import (
    NOTICES_API, CHECK_INTERVAL, TARGET_GROUPS, 
    NOTICE_CATEGORIES, MESSAGE_TEMPLATES
)

# 存储已处理的通知ID
processed_notices: Set[int] = set()
is_monitoring = False

async def fetch_notices() -> List[Dict]:
    """获取最新的通知列表"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'http://ctf.zypc.xupt.edu.cn/',
            'Connection': 'keep-alive'
        }
        
        cookies = {
            'a1token': 'eyJhbGciOiJSUzM4NCIsInR5cCI6IkpXVCJ9.eyJKV1RWZXJzaW9uIjoiWlJmbElZWU1EYzhoV1E4TyIsIlJvbGUiOiJBRE1JTiIsIlVzZXJJRCI6IjhlYWI3N2M0LTViYWMtNDg1Yi1iOGJiLTg0ZTc0MjNlYjZiYyIsIlVzZXJOYW1lIjoiWW9ndXJ0IiwiZXhwIjoxNzU2ODAwNDIxLCJvcmlnX2lhdCI6MTc1NjYyNzYyMX0.M3yc5qCBtjtWgvcBx7F3e3t--zfP6jA1FquICYYIhoDpBl8mkilBLeuScuwiDpLtPfLfc6UKZCHGYKMXCLVePKYK3wiMYiK3aCxxM6hwsbIw45BWdbPPlgyzRsOgyfmRDeTsh6s3x0WTX9n_Ku9PLpQznA6sIklhRZY7llW6kojt-e2otIjf2yO8dmQaweAsBog2oqvzXCilkPJiv0HIWk_UJ7fdQ8hFa9mLfLmaRBxcMRpFeY8eWykkPw05Jx-lifL-KO4fzerizdLHD9YXNC84bREljC_G8iKttvpwXcnl42qFDpDFFbBDl3RSvANm-Uaj_n5mrzJk4uJGnNk2LQ',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(NOTICES_API, headers=headers, cookies=cookies, timeout=10) as response:
                logger.info(f"API请求状态: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 200:
                        return data.get("data", [])
                    else:
                        logger.warning(f"API返回错误代码: {data.get('code')}")
                elif response.status == 401:
                    logger.error("API认证失败，可能需要登录或特殊权限")
                elif response.status == 403:
                    logger.error("API访问被拒绝，可能被反爬虫机制阻止")
                else:
                    logger.warning(f"API请求失败，状态码: {response.status}")
                    
    except asyncio.TimeoutError:
        logger.error("API请求超时")
    except Exception as e:
        logger.error(f"获取通知失败: {e}")
    return []

def format_notice_message(notice: Dict) -> str:
    """格式化通知消息"""
    notice_id = notice.get("notice_id")
    category = notice.get("notice_category")
    data = notice.get("data", [])
    create_time = notice.get("create_time")
    
    # 解析时间
    try:
        dt = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
        time_str = dt.strftime("%m-%d %H:%M")
    except:
        time_str = create_time
    
    # 根据类型设置emoji和颜色
    emoji_map = {
        "FirstBlood": "🥇",
        "SecondBlood": "🥈", 
        "ThirdBlood": "🥉",
        "NewChallenge": "🆕",
        "ChallengeUpdate": "🔄",
        "GameStart": "🎯",
        "GameEnd": "🏁",
        "Announcement": "📢",
        "Hint": "💡",
        "NewHint": "💡",  # 新提示
        "TeamUpdate": "👥",
        "ScoreUpdate": "📊",
        "SystemNotice": "⚙️"
    }
    
    emoji = emoji_map.get(category, "🎯")  # 默认使用🎯表示未知类型
    
    # 根据通知类型解析数据格式
    if category in ["FirstBlood", "SecondBlood", "ThirdBlood"]:
        # 血条通知：[队伍名, 题目名]
        team_name = data[0] if len(data) > 0 else "未知队伍"
        challenge_name = data[1] if len(data) > 1 else "未知题目"
        
        # 根据血条类型设置描述
        blood_desc = {
            "FirstBlood": "first blood",
            "SecondBlood": "second blood", 
            "ThirdBlood": "third blood"
        }
        desc = blood_desc.get(category, "blood")
        
        message = f"""🎮 CTF赛事通知 🎮

{emoji} {team_name} has got {challenge_name}'s {desc}!
👥 队伍: {team_name}
📝 题目: {challenge_name}
⏰ 时间: {time_str}
"""
        
    elif category == "NewHint":
        # 新提示通知：[题目名]
        challenge_name = data[0] if len(data) > 0 else "未知题目"
        
        message = f"""🎮 CTF赛事通知 🎮

{emoji} Challenge [{challenge_name}] added a new hint
📝 题目: {challenge_name}
⏰ 时间: {time_str}
"""
        
    else:
        # 其他类型通知的通用格式
        content = ", ".join(data) if data else "无详细信息"
        
        message = f"""🎮 CTF赛事通知 🎮

{emoji} {category}
📄 内容: {content}
⏰ 时间: {time_str}
"""
    
    return message

async def check_new_notices():
    """检查新通知"""
    global processed_notices
    
    notices = await fetch_notices()
    if not notices:
        return
    
    # 按时间排序，确保按顺序处理
    notices.sort(key=lambda x: x.get("notice_id", 0))
    
    new_notices = []
    for notice in notices:
        notice_id = notice.get("notice_id")
        category = notice.get("notice_category")
        
        # 过滤通知类型 - 如果NOTICE_CATEGORIES为空，则推送所有类型
        if NOTICE_CATEGORIES and category not in NOTICE_CATEGORIES:
            if notice_id:
                processed_notices.add(notice_id)
            continue
            
        if notice_id and notice_id not in processed_notices:
            new_notices.append(notice)
            processed_notices.add(notice_id)
    
    # 发送新通知
    if new_notices:
        try:
            bot = get_bot()
            for notice in new_notices:
                message = format_notice_message(notice)
                
                await send_to_groups(bot, message)
                
                logger.info(f"发送通知: {notice.get('notice_id')} - {notice.get('notice_category')}")
                
                # 避免发送过快
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"发送通知失败: {e}")

async def send_to_groups(bot, message: str):
    """发送消息到指定群组"""
    try:
        # 如果配置了特定群组，只发送到这些群组
        if TARGET_GROUPS:
            for group_id in TARGET_GROUPS:
                try:
                    await bot.send_group_msg(group_id=group_id, message=message)
                    await asyncio.sleep(0.5)  # 避免发送过快
                except Exception as e:
                    logger.warning(f"向群组 {group_id} 发送消息失败: {e}")
        else:
            # 否则发送到所有群组
            group_list = await bot.get_group_list()
            for group in group_list:
                group_id = group.get("group_id")
                try:
                    await bot.send_group_msg(group_id=group_id, message=message)
                    await asyncio.sleep(0.5)  # 避免发送过快
                except Exception as e:
                    logger.warning(f"向群组 {group_id} 发送消息失败: {e}")
    except Exception as e:
        logger.error(f"发送消息失败: {e}")

async def start_notice_monitor():
    """开始监控"""
    global is_monitoring, processed_notices
    
    if is_monitoring:
        return
    
    is_monitoring = True
    logger.info("开始CTF通知监控")
    
    # 初始化时获取所有现有通知ID，避免重复发送
    notices = await fetch_notices()
    processed_notices = {notice.get("notice_id") for notice in notices if notice.get("notice_id")}
    
    # 添加定时任务
    scheduler.add_job(
        check_new_notices,
        "interval",
        seconds=CHECK_INTERVAL,
        id="ctf_notice_monitor",
        replace_existing=True
    )

async def stop_notice_monitor():
    """停止监控"""
    global is_monitoring
    
    if not is_monitoring:
        return
    
    is_monitoring = False
    logger.info("停止CTF通知监控")
    
    # 移除定时任务
    try:
        scheduler.remove_job("ctf_notice_monitor")
    except:
        pass

def get_monitor_status() -> Dict:
    """获取监控状态"""
    return {
        "is_monitoring": is_monitoring,
        "processed_count": len(processed_notices),
        "check_interval": CHECK_INTERVAL,
        "api_url": NOTICES_API
    }
