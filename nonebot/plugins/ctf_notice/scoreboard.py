import os
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
import matplotlib.font_manager as fm

from .a1ctf_client import get_a1ctf_client
from .config import API_CONFIG, SCOREBOARD_IMAGE_CONFIG
from nonebot import logger

def setup_chinese_font():
    """设置中文字体"""
    # 常见的中文字体列表
    chinese_fonts = [
        'WenQuanYi Zen Hei',  # 文泉驿正黑
        'WenQuanYi Micro Hei',  # 文泉驿微米黑
        'SimHei',  # 黑体
        'Microsoft YaHei',  # 微软雅黑
        'PingFang SC',  # 苹果苹方
        'Noto Sans CJK SC',  # Google Noto
        'Source Han Sans CN',  # 思源黑体
    ]
    
    # 尝试设置中文字体
    for font in chinese_fonts:
        try:
            plt.rcParams['font.sans-serif'] = [font, 'DejaVu Sans']
            logger.info(f"✅ 使用中文字体: {font}")
            return True
        except:
            continue
    
    # 如果没有找到中文字体，使用默认字体
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    logger.warning("⚠️ 未找到中文字体，部分中文可能显示为方框")
    return False

def check_font_display():
    """检查字体显示效果"""
    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 初始化字体设置
setup_chinese_font()
check_font_display()
sns.set_style("whitegrid")  # 设置seaborn风格

async def fetch_scoreboard(group_id: Optional[int] = None) -> Dict:
    """
    异步获取积分榜数据，支持指定组别ID
    
    基于A1CTF API响应格式:
    {
        "code": 200,
        "data": {
            "game_id": 3,
            "name": "Newstar",
            "teams": [
                {
                    "team_id": 1,
                    "team_name": "队伍名称",
                    "team_avatar": null,
                    "team_slogan": null,
                    "team_members": [...],
                    "team_description": null,
                    "rank": 1,
                    "score": 1000.0,
                    "penalty": 0,
                    "group_id": 1,
                    "group_name": "新手组",
                    "solved_challenges": [...],
                    "score_adjustments": [...],
                    "last_solve_time": 1693737600000
                }
            ],
            "top10_timelines": [
                {
                    "team_id": 1,
                    "team_name": "队伍名称",
                    "scores": [
                        {"record_time": 1693737600000, "score": 100.0},
                        {"record_time": 1693741200000, "score": 200.0}
                    ]
                }
            ],
            "groups": [
                {
                    "group_id": 1,
                    "group_name": "新手组",
                    "team_count": 25
                }
            ],
            "current_group": {
                "group_id": 1,
                "group_name": "新手组",
                "team_count": 25
            },
            "pagination": {
                "current_page": 1,
                "page_size": 100,
                "total_count": 25,
                "total_pages": 1
            }
        }
    }
    """
    client = get_a1ctf_client()
    if not client:
        logger.error("A1CTF client not initialized.")
        return {}

    try:
        headers = API_CONFIG["headers"]
        base_url = API_CONFIG["scoreboard"]["url"].split('?')[0]  # 获取基础URL
        
        # 构建请求参数
        params = {"page": 1, "size": 100}
        if group_id is not None:
            params["group_id"] = group_id
            logger.info(f"📡 正在获取组别 {group_id} 的积分榜数据...")
        else:
            logger.info("📡 正在获取所有组别的基础数据...")
        
        # 构建完整URL
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{base_url}?{param_str}"
        timeout = API_CONFIG["scoreboard"]["timeout"]
        
        logger.debug(f"请求URL: {url}")
        logger.debug(f"请求参数: {params}")
        
        data = await client.request("GET", url, headers=headers, timeout=timeout)
        
        # 处理API响应
        if data.get('code') != 200:
            logger.error(f"API返回错误: {data.get('code')} - {data.get('message', 'Unknown error')}")
            return {}
        
        result = data.get('data', {})
        
        if group_id is not None:
            teams = result.get('teams', [])
            teams_count = len(teams)
            logger.info(f"✅ 成功获取组别 {group_id} 数据，包含 {teams_count} 支队伍")
            
            # 验证数据是否正确过滤到指定组别
            if teams:
                sample_team = teams[0]
                logger.debug(f"示例队伍: {sample_team.get('team_name', 'Unknown')} - 组别: {sample_team.get('group_id')} - 分数: {sample_team.get('score', 0)}")
                
                # 检查是否所有队伍都属于指定组别
                group_ids = {team.get('group_id') for team in teams}
                if len(group_ids) > 1 or (len(group_ids) == 1 and group_id not in group_ids):
                    logger.warning(f"⚠️ 数据可能未正确过滤，期望组别{group_id}但发现组别: {group_ids}")
        else:
            groups = result.get('groups', [])
            teams = result.get('teams', [])
            groups_count = len(groups)
            teams_count = len(teams)
            logger.info(f"✅ 成功获取基础数据，发现 {groups_count} 个组别，{teams_count} 支队伍")
            
        return result
        
    except aiohttp.ClientResponseError as e:
        logger.warning(f"API request failed with status: {e.status}, message: {e.message}")
    except asyncio.TimeoutError:
        logger.error("API request timed out.")
    except Exception as e:
        logger.error(f"获取积分榜数据失败: {e}")
    
    return {}

async def fetch_all_groups_info() -> List[Dict]:
    """获取所有组别信息"""
    logger.info("📡 正在获取所有组别信息...")
    
    # 获取不带group_id的数据来获取所有组别列表
    all_data = await fetch_scoreboard()
    groups = all_data.get('groups', [])
    
    logger.info(f"发现 {len(groups)} 个组别:")
    for group in groups:
        logger.info(f"  - 组别 {group['group_id']}: {group['group_name']} ({group.get('team_count', 0)} 支队伍)")
    
    return groups

def plot_group_scoreboard(group_info: Dict, teams: List[Dict], timelines: List[Dict], save_path: str) -> None:
    """
    为指定组别生成积分榜图表，只显示该组别的队伍
    
    Args:
        group_info: 组别信息 {"group_id": 1, "group_name": "新手组", "team_count": 25}
        teams: 该组别的队伍列表，已经过滤
        timelines: 时间线数据（top10_timelines）
        save_path: 保存路径
    """
    try:
        # 重新确保中文字体设置
        setup_chinese_font()
        check_font_display()
        
        group_id = group_info['group_id']
        group_name = group_info['group_name']
        team_count = group_info.get('team_count', len(teams))
        
        logger.info(f"🎨 正在为组别 {group_name} (ID: {group_id}) 生成图表...")
        
        # 验证队伍数据是否属于当前组别
        group_teams = [team for team in teams if team.get('group_id') == group_id]
        if len(group_teams) != len(teams):
            logger.warning(f"⚠️ 队伍数据过滤不完整，期望{len(teams)}支队伍，实际{len(group_teams)}支属于组别{group_id}")
            teams = group_teams
        
        # 根据组别过滤时间线数据
        group_timelines = []
        if timelines:
            team_names_in_group = {team['team_name'] for team in teams}
            group_timelines = [tl for tl in timelines if tl.get('team_name') in team_names_in_group]
        
        logger.info(f"📊 组别 {group_name} 共有 {len(teams)} 支队伍，{len(group_timelines)} 条时间线")
        
        # 验证数据：打印前3支队伍的信息
        if teams:
            logger.info(f"前3支队伍:")
            for i, team in enumerate(teams[:3], 1):
                logger.info(f"  {i}. {team.get('team_name', 'Unknown')} - 分数: {team.get('score', 0)} - 排名: {team.get('rank', 'N/A')}")
        
        # 创建图形，使用更大的尺寸以适应中文标题
        fig, ax = plt.subplots(figsize=(16, 12))
        
        # 定义专业的颜色调色板
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', 
                  '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
                  '#6C5CE7', '#A29BFE', '#FD79A8', '#E17055', '#00B894']
        
        if not teams:
            logger.warning(f"⚠️ 组别 {group_name} 没有队伍数据")
            # 创建一个空的图表
            ax.text(0.5, 0.5, f'组别 {group_name}\n暂无队伍数据', 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=20, fontweight='bold')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        
        elif not group_timelines:
            logger.info(f"组别 {group_name} 没有时间线数据，使用静态柱状图")
            # 取前15名队伍（或所有队伍如果少于15支）
            top_teams = teams[:15]
            team_names = [team['team_name'] for team in top_teams]
            team_scores = [team['score'] for team in top_teams]
            
            logger.info(f"绘制前 {len(top_teams)} 名队伍的柱状图")
            
            bars = ax.bar(range(len(team_names)), team_scores, 
                        color=colors[:len(team_names)], alpha=0.8)
            
            ax.set_xlabel('队伍', fontsize=14, fontweight='bold')
            ax.set_ylabel('分数', fontsize=14, fontweight='bold')
            ax.set_xticks(range(len(team_names)))
            ax.set_xticklabels(team_names, rotation=45, ha='right')
            
            # 添加数值标签
            max_score = max(team_scores) if team_scores else 1
            for bar, score in zip(bars, team_scores):
                height = bar.get_height()
                if height > 0:  # 只在有分数时显示标签
                    ax.text(bar.get_x() + bar.get_width()/2., height + max_score*0.01,
                           f'{int(score)}', ha='center', va='bottom', fontweight='bold')
        
        else:
            logger.info(f"组别 {group_name} 使用时间线数据绘制动态图表")
            # 使用时间线数据绘制动态图表
            for i, timeline in enumerate(group_timelines[:10]):  # 最多显示前10名
                team_name = timeline.get('team_name', f'Team{i+1}')
                scores_data = timeline.get('scores', [])
                
                if not scores_data:
                    continue
                
                # 提取时间和分数数据
                times = []
                scores = []
                for score_point in scores_data:
                    if isinstance(score_point, dict):
                        record_time = score_point.get('record_time')
                        score = score_point.get('score', 0)
                        if record_time:
                            # 处理时间戳（毫秒转秒）
                            if record_time > 1e12:  # 毫秒时间戳
                                record_time = record_time / 1000
                            times.append(datetime.fromtimestamp(record_time))
                            scores.append(score)
                
                if times and scores:
                    ax.plot(times, scores, marker='o', linewidth=2.5, 
                           label=team_name, color=colors[i % len(colors)])
            
            ax.set_xlabel('时间', fontsize=14, fontweight='bold')
            ax.set_ylabel('分数', fontsize=14, fontweight='bold')
            
            # 格式化时间轴
            if len(group_timelines) > 0:
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
                date_formatter = DateFormatter("%m-%d %H:%M")
                ax.xaxis.set_major_formatter(date_formatter)
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 设置标题，明确显示当前组别
        title = f'{group_name} 积分榜'
        ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
        
        # 添加组别标识
        fig.text(0.02, 0.98, f'组别ID: {group_id}', fontsize=12, 
                ha='left', va='top', fontweight='bold', 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))
        
        # 添加队伍数量信息
        fig.text(0.02, 0.94, f'队伍数量: {len(teams)}', fontsize=10, 
                ha='left', va='top', 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
        
        # 美化图表
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        # 验证文件是否成功保存
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            logger.info(f"✅ 组别 {group_name} 积分榜图片已保存: {save_path} (大小: {file_size} bytes)")
        else:
            logger.error(f"❌ 组别 {group_name} 积分榜图片保存失败")
            
    except Exception as e:
        logger.error(f"生成组别 {group_info.get('group_name', 'Unknown')} 积分榜图片时出错: {e}")
        # 创建一个错误提示图片
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f'生成积分榜时出错\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=16, color='red')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        except:
            pass

async def generate_scoreboard() -> Tuple[List[str], str]:
    """
    生成所有组别的积分榜图片
    
    Returns:
        Tuple[List[str], str]: (图片路径列表, 排名信息文本)
    """
    try:
        logger.info("🚀 开始生成所有组别的积分榜...")
        
        # 获取所有组别信息
        groups = await fetch_all_groups_info()
        if not groups:
            raise ValueError("无法获取组别信息")
        
        logger.info(f"发现 {len(groups)} 个组别，开始逐个生成积分榜...")
        
        # 确保保存目录存在
        save_dir = SCOREBOARD_IMAGE_CONFIG["save_dir"]
        os.makedirs(save_dir, exist_ok=True)
        
        image_paths = []
        ranking_info = "🏆 Newstar 积分榜汇总\n\n"
        
        # 为每个组别生成图片
        for group_info in groups:
            try:
                group_id = group_info['group_id']
                group_name = group_info['group_name']
                
                logger.info(f"📊 正在处理组别: {group_name} (ID: {group_id})")
                
                # 获取组别数据
                scoreboard_data = await fetch_scoreboard(group_id)
                
                if not scoreboard_data:
                    logger.warning(f"跳过组别 {group_name}：无法获取数据")
                    continue
                
                teams = scoreboard_data.get('teams', [])
                timelines = scoreboard_data.get('top10_timelines', [])
                
                # 生成文件路径
                safe_group_name = group_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
                filename = f"scoreboard_group_{group_id}_{safe_group_name}.png"
                save_path = os.path.join(save_dir, filename)
                
                # 生成图表
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: plot_group_scoreboard(group_info, teams, timelines, save_path)
                )
                
                # 验证文件
                if os.path.exists(save_path):
                    image_paths.append(save_path)
                    logger.info(f"✅ 组别 {group_name} 图片生成成功")
                else:
                    logger.error(f"❌ 组别 {group_name} 图片生成失败")
                    continue
                
                # 生成排名信息
                ranking_info += f"📊 {group_name}:\n"
                
                if len(teams) >= 3:
                    medals = ["🥇", "🥈", "🥉"]
                    for i in range(3):
                        team = teams[i]
                        ranking_info += f"   {medals[i]} {team['team_name']} - {team['score']}分\n"
                elif len(teams) > 0:
                    medals = ["🥇", "🥈", "🥉"]
                    for i in range(len(teams)):
                        team = teams[i]
                        medal = medals[i] if i < 3 else f"#{i+1}"
                        ranking_info += f"   {medal} {team['team_name']} - {team['score']}分\n"
                else:
                    ranking_info += "   暂无队伍数据\n"
                
                ranking_info += "\n"
                
            except Exception as group_error:
                logger.error(f"处理组别 {group_info.get('group_name', 'Unknown')} 时出错: {group_error}")
                continue
        
        if not image_paths:
            raise FileNotFoundError("所有组别的图片都生成失败")
        
        logger.info(f"🎉 成功生成 {len(image_paths)} 个组别的积分榜图片")
        return image_paths, ranking_info
        
    except Exception as e:
        logger.error(f"❌ 生成积分榜完全失败: {e}")
        raise

async def generate_single_group_scoreboard(group_id: int) -> Tuple[str, str]:
    """
    生成单个组别的积分榜图片
    
    Args:
        group_id: 组别ID
        
    Returns:
        Tuple[str, str]: (图片路径, 排名信息文本)
    """
    try:
        logger.info(f"🚀 开始生成组别 {group_id} 的积分榜...")
        
        # 获取组别信息
        groups = await fetch_all_groups_info()
        group_info = next((g for g in groups if g['group_id'] == group_id), None)
        
        if not group_info:
            logger.warning(f"⚠️ 未找到组别 {group_id} 的信息，使用默认信息")
            group_info = {'group_id': group_id, 'group_name': f'组别{group_id}', 'team_count': 0}
        
        # 获取组别数据
        scoreboard_data = await fetch_scoreboard(group_id)
        
        if not scoreboard_data:
            raise ValueError(f"无法获取组别 {group_id} 的数据")
        
        teams = scoreboard_data.get('teams', [])
        timelines = scoreboard_data.get('top10_timelines', [])
        
        # 确保保存目录存在
        save_dir = SCOREBOARD_IMAGE_CONFIG["save_dir"]
        os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件路径
        group_name = group_info['group_name']
        safe_group_name = group_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        filename = f"scoreboard_group_{group_id}_{safe_group_name}.png"
        save_path = os.path.join(save_dir, filename)
        
        # 生成图表
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: plot_group_scoreboard(group_info, teams, timelines, save_path)
        )
        
        # 验证文件
        if not os.path.exists(save_path):
            raise FileNotFoundError(f"图片文件未生成: {save_path}")
        
        # 生成排名信息
        game_name = scoreboard_data.get('name', '未知比赛')
        
        ranking_info = f"🏆 {game_name} - {group_name}\n\n🏅 前三名:\n"
        
        if len(teams) >= 3:
            medals = ["🥇", "🥈", "🥉"]
            for i in range(3):
                team = teams[i]
                ranking_info += f"   {medals[i]} {team['team_name']} - {team['score']}分\n"
        elif len(teams) > 0:
            medals = ["🥇", "🥈", "🥉"]
            for i in range(len(teams)):
                team = teams[i]
                medal = medals[i] if i < 3 else f"#{i+1}"
                ranking_info += f"   {medal} {team['team_name']} - {team['score']}分\n"
        else:
            ranking_info += "   暂无队伍数据\n"
        
        logger.info(f"✅ 组别 {group_name} 积分榜生成完成")
        return save_path, ranking_info
        
    except Exception as e:
        logger.error(f"❌ 生成组别 {group_id} 积分榜失败: {e}")
        raise
