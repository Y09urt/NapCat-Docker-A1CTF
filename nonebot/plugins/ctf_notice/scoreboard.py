"""
积分榜功能模块
"""
import asyncio
import aiohttp
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.dates import DateFormatter
import seaborn as sns
from typing import Dict, List, Tuple, Optional
from nonebot import logger

from .config import API_CONFIG, SCOREBOARD_IMAGE_CONFIG
from .a1ctf_client import get_a1ctf_client

def setup_chinese_font() -> bool:
    """设置中文字体，尝试多种字体以确保兼容性"""
    # 优先考虑容器中安装的字体
    chinese_fonts = [
        'WenQuanYi Micro Hei',  # 文泉驿微米黑 (Linux容器中)
        'WenQuanYi Zen Hei',    # 文泉驿正黑 (Linux容器中)
        'SimHei',               # 黑体 (Windows)
        'Microsoft YaHei',      # 微软雅黑 (Windows)
        'SimSun',               # 宋体 (Windows)
        'KaiTi',                # 楷体 (Windows)
        'FangSong',             # 仿宋 (Windows)
        'PingFang SC',          # 苹方 (macOS)
        'Hiragino Sans GB',     # 冬青黑体 (macOS)
        'Noto Sans CJK SC',     # 思源黑体 (跨平台)
    ]
    
    # 检查可用字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    for font in chinese_fonts:
        if font in available_fonts:
            plt.rcParams['font.sans-serif'] = [font, 'DejaVu Sans']
            logger.info(f"✅ 使用中文字体: {font}")
            return True
    
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

async def fetch_scoreboard() -> Dict:
    """异步获取积分榜数据"""
    client = get_a1ctf_client()
    if not client:
        logger.error("A1CTF client not initialized.")
        return {}

    try:
        headers = API_CONFIG["headers"]
        url = API_CONFIG["scoreboard"]["url"]
        timeout = API_CONFIG["scoreboard"]["timeout"]
        
        data = await client.request("GET", url, headers=headers, timeout=timeout)
        
        return data.get('data', {})
    except aiohttp.ClientResponseError as e:
        logger.warning(f"API request failed with status: {e.status}, message: {e.message}")
    except asyncio.TimeoutError:
        logger.error("API request timed out.")
    except Exception as e:
        logger.error(f"获取积分榜数据失败: {e}")
    
    return {}

def plot_and_save(scoreboard_data: Dict, save_path: str) -> None:
    """生成并保存积分榜图表"""
    try:
        # 重新确保中文字体设置
        setup_chinese_font()
        check_font_display()
        
        # 创建图形和子图，使用更专业的配色
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # 定义漂亮的颜色调色板
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', 
                  '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43']
        
        # 绘制前10队伍的分数变化曲线
        for i, team in enumerate(scoreboard_data['top10_timelines']):
            times = [datetime.fromtimestamp(s['record_time']/1000) for s in team['scores']]
            scores = [s['score'] for s in team['scores']]
            
            color = colors[i % len(colors)]
            
            # 绘制主曲线，使用渐变效果
            ax.plot(times, scores, 
                          color=color, 
                          linewidth=3, 
                          label=team['team_name'],
                          alpha=0.8,
                          zorder=2)
            
            # 添加数据点
            ax.scatter(times, scores, 
                      color=color, 
                      s=40, 
                      alpha=0.9, 
                      edgecolors='white', 
                      linewidth=1.5,
                      zorder=3)
            
            # 为前三名添加填充区域
            if i < 3:
                ax.fill_between(times, scores, alpha=0.1, color=color)
        
        # 设置坐标轴标签和标题
        ax.set_xlabel('时间', fontsize=14, fontweight='bold', color='#2C3E50')
        ax.set_ylabel('分数', fontsize=14, fontweight='bold', color='#2C3E50')
        ax.set_title(f"{scoreboard_data['name']} 积分榜前10队伍分数变化", 
                    fontsize=18, fontweight='bold', color='#2C3E50', pad=20)
        
        # 美化网格
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
        ax.set_facecolor('#FAFAFA')
        
        # 设置图例
        legend = ax.legend(bbox_to_anchor=(1.02, 1), 
                          loc='upper left', 
                          frameon=True,
                          fancybox=True,
                          shadow=True,
                          fontsize=11)
        legend.get_frame().set_facecolor('white')
        legend.get_frame().set_alpha(0.9)
        
        # 格式化时间轴
        date_formatter = DateFormatter("%m-%d %H:%M")
        ax.xaxis.set_major_formatter(date_formatter)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 设置坐标轴颜色和样式
        ax.tick_params(colors='#2C3E50', which='both')
        for spine in ax.spines.values():
            spine.set_color('#BDC3C7')
            spine.set_linewidth(1.2)
        
        # 添加排名标注（为前三名）
        for i, team in enumerate(scoreboard_data['top10_timelines'][:3]):
            if team['scores']:
                last_time = datetime.fromtimestamp(team['scores'][-1]['record_time']/1000)
                last_score = team['scores'][-1]['score']
                
                # 添加排名标注
                rank_colors = ['#FFD700', '#C0C0C0', '#CD7F32']  # 金银铜
                ax.annotate(f'#{i+1}', 
                           xy=(last_time, last_score),
                           xytext=(10, 10), 
                           textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', 
                                    facecolor=rank_colors[i], 
                                    alpha=0.8),
                           fontsize=10,
                           fontweight='bold',
                           color='white')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片，使用高质量设置
        try:
            plt.savefig(save_path, 
                        dpi=300, 
                        bbox_inches='tight', 
                        facecolor='white',
                        edgecolor='none',
                        format='png')
            logger.info(f"✅ 积分榜图片已保存到: {save_path}")
        except Exception as save_error:
            logger.error(f"❌ 保存图片文件失败: {save_error}")
            raise save_error
        finally:
            plt.close()  # 确保图形被关闭
        
    except Exception as e:
        logger.error(f"❌ 生成积分榜图片失败: {e}")
        # 确保清理matplotlib资源
        try:
            plt.close('all')
        except:
            pass
        raise

async def generate_scoreboard() -> Tuple[str, str]:
    """
    生成积分榜图片并返回图片路径和排名信息
    
    Returns:
        Tuple[str, str]: (图片路径, 排名信息文本)
    """
    try:
        # 获取积分榜数据
        logger.info("📡 正在获取积分榜数据...")
        try:
            scoreboard_data = await fetch_scoreboard()
            logger.info(f"✅ 成功获取积分榜数据，队伍数量: {len(scoreboard_data.get('teams', []))}")
        except Exception as fetch_error:
            logger.error(f"❌ 获取积分榜数据失败: {fetch_error}")
            raise fetch_error
        
        # 确保保存目录存在
        save_dir = SCOREBOARD_IMAGE_CONFIG["save_dir"]
        try:
            os.makedirs(save_dir, exist_ok=True)
            logger.info(f"📁 保存目录: {save_dir}")
        except Exception as dir_error:
            logger.error(f"❌ 创建保存目录失败: {dir_error}")
            raise dir_error
        
        # 生成文件路径
        save_path = os.path.join(save_dir, SCOREBOARD_IMAGE_CONFIG["filename"])
        logger.info(f"💾 图片保存路径: {save_path}")
        
        # 在异步环境中使用同步绘图操作需要使用run_in_executor
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: plot_and_save(scoreboard_data, save_path)
            )
            logger.info(f"✅ 图片生成成功: {save_path}")
        except Exception as plot_error:
            logger.error(f"❌ 图片生成失败: {plot_error}")
            raise plot_error
        
        # 验证文件是否真正生成
        if not os.path.exists(save_path):
            error_msg = f"图片文件未生成: {save_path}"
            logger.error(f"❌ {error_msg}")
            raise FileNotFoundError(error_msg)
        
        file_size = os.path.getsize(save_path)
        logger.info(f"✅ 图片文件验证成功，大小: {file_size} bytes")
        
        # 生成排名信息
        ranking_info = f"📊 比赛名称: {scoreboard_data['name']}\n🏆 前三名队伍:\n"
        for i, team in enumerate(scoreboard_data['teams'][:3]):
            medals = ["🥇", "🥈", "🥉"]
            ranking_info += f"   {medals[i]} {team['team_name']} - {team['score']}分\n"
        
        return save_path, ranking_info
        
    except Exception as e:
        logger.error(f"❌ 生成积分榜完全失败: {e}")
        raise
