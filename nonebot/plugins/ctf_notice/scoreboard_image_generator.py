#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
积分榜图片生成器
通过调用A1CTF平台API获取积分榜数据，生成积分榜图片
"""

import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import pandas as pd
import json
import argparse
import os
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

class ScoreboardImageGenerator:
    def __init__(self, base_url="http://localhost:7777", token=None):
        """
        初始化积分榜图片生成器
        
        Args:
            base_url (str): 平台API基础URL
            token (str): 用户认证token
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        
        # 设置中文字体
        self.setup_fonts()
        
    def setup_fonts(self):
        """设置中文字体"""
        try:
            # 尝试使用系统中文字体
            font_paths = [
                'C:/Windows/Fonts/simhei.ttf',  # 黑体
                'C:/Windows/Fonts/simsun.ttc',  # 宋体
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            ]
            
            self.font_path = None
            for path in font_paths:
                if os.path.exists(path):
                    self.font_path = path
                    break
            
            if self.font_path:
                plt.rcParams['font.sans-serif'] = [font_manager.FontProperties(fname=self.font_path).get_name()]
            else:
                print("警告: 未找到中文字体，图片中的中文可能显示为方块")
                
        except Exception as e:
            print(f"字体设置失败: {e}")
    
    def get_game_info(self, game_id):
        """获取比赛信息"""
        try:
            url = f"{self.base_url}/api/game/{game_id}/info"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()['data']
        except Exception as e:
            print(f"获取比赛信息失败: {e}")
            return None
    
    def get_scoreboard_data(self, game_id, group_id=None, page=1, size=50):
        """获取积分榜数据"""
        try:
            url = f"{self.base_url}/api/game/{game_id}/scoreboard"
            params = {'page': page, 'size': size}
            if group_id:
                params['group_id'] = group_id
                
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()['data']
        except Exception as e:
            print(f"获取积分榜数据失败: {e}")
            return None
    
    def generate_scoreboard_table_image(self, game_info, scoreboard_data, output_path=None, theme='light'):
        """生成积分榜表格图片"""
        if not scoreboard_data or not scoreboard_data.get('teams'):
            print("没有积分榜数据")
            return None
            
        teams = scoreboard_data['teams']
        
        # 设置图片尺寸和DPI
        fig_width = 16
        fig_height = max(8, len(teams) * 0.5 + 4)
        dpi = 150
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
        
        # 设置主题颜色
        if theme == 'dark':
            bg_color = '#0f172a'
            text_color = '#f1f5f9'
            header_color = '#1e293b'
            row_colors = ['#334155', '#475569']
        else:
            bg_color = '#ffffff'
            text_color = '#0f172a'
            header_color = '#e2e8f0'
            row_colors = ['#f8fafc', '#f1f5f9']
        
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        
        # 准备表格数据
        table_data = []
        headers = ['排名', '队伍名称', '总分']
        
        for i, team in enumerate(teams):
            row = [
                str(team.get('rank', i + 1)),
                team.get('team_name', '未知队伍'),
                str(int(team.get('score', 0)))
            ]
            table_data.append(row)
        
        # 创建表格
        table = ax.table(
            cellText=table_data,
            colLabels=headers,
            cellLoc='center',
            loc='center',
            bbox=[0.1, 0.1, 0.8, 0.8]
        )
        
        # 设置表格样式
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)
        
        # 设置表头样式
        for i in range(len(headers)):
            cell = table[(0, i)]
            cell.set_facecolor(header_color)
            cell.set_text_props(weight='bold', color=text_color)
            cell.set_height(0.08)
        
        # 设置数据行样式
        for i in range(len(table_data)):
            for j in range(len(headers)):
                cell = table[(i + 1, j)]
                cell.set_facecolor(row_colors[i % 2])
                cell.set_text_props(color=text_color)
                cell.set_height(0.06)
                
                # 特殊处理排名列
                if j == 0:  # 排名列
                    rank = int(table_data[i][0])
                    if rank == 1:
                        cell.set_facecolor('#ffd700')  # 金色
                        cell.set_text_props(color='#000000', weight='bold')
                    elif rank == 2:
                        cell.set_facecolor('#c0c0c0')  # 银色
                        cell.set_text_props(color='#000000', weight='bold')
                    elif rank == 3:
                        cell.set_facecolor('#cd7f32')  # 铜色
                        cell.set_text_props(color='#ffffff', weight='bold')
        
        # 添加标题
        title = f"{game_info.get('name', '比赛')} - 积分榜"
        if scoreboard_data.get('current_group'):
            title += f" ({scoreboard_data['current_group']['group_name']}组)"
        
        plt.title(title, fontsize=20, fontweight='bold', color=text_color, pad=20)
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plt.figtext(0.95, 0.02, f"生成时间: {timestamp}", 
                   ha='right', va='bottom', fontsize=10, color=text_color)
        
        # 去除坐标轴
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # 保存图片
        if not output_path:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"scoreboard_{game_info.get('name', 'game')}_{timestamp_str}.png"
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', 
                   facecolor=bg_color, edgecolor='none')
        plt.close()
        
        print(f"积分榜表格图片已保存至: {output_path}")
        return output_path
    
    def generate_scoreboard_chart_image(self, game_info, scoreboard_data, output_path=None, theme='light'):
        """生成积分榜图表图片（TOP10时间线图）"""
        if not scoreboard_data or not scoreboard_data.get('top10_timelines'):
            print("没有时间线数据")
            return None
        
        timelines = scoreboard_data['top10_timelines']
        
        # 设置图片尺寸和DPI
        fig_width = 16
        fig_height = 10
        dpi = 150
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
        
        # 设置主题颜色
        if theme == 'dark':
            bg_color = '#0f172a'
            text_color = '#f1f5f9'
            grid_color = '#334155'
        else:
            bg_color = '#ffffff'
            text_color = '#0f172a'
            grid_color = '#e2e8f0'
        
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        
        # 颜色列表
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', 
                 '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43']
        
        # 绘制时间线
        for i, timeline in enumerate(timelines[:10]):  # 只取前10名
            if not timeline.get('scores'):
                continue
                
            # 准备数据
            times = []
            scores = []
            
            for score_item in timeline['scores']:
                times.append(pd.to_datetime(score_item['record_time'], unit='ms'))
                scores.append(score_item['score'])
            
            if not times:
                continue
            
            # 绘制线条
            color = colors[i % len(colors)]
            ax.plot(times, scores, marker='o', linewidth=3, 
                   markersize=6, label=timeline['team_name'], 
                   color=color, markerfacecolor=color)
        
        # 设置图表样式
        ax.set_xlabel('时间', fontsize=14, color=text_color)
        ax.set_ylabel('分数', fontsize=14, color=text_color)
        ax.tick_params(colors=text_color)
        ax.grid(True, alpha=0.3, color=grid_color)
        
        # 设置图例
        legend = ax.legend(loc='upper left', frameon=True, facecolor=bg_color, 
                          edgecolor=text_color, labelcolor=text_color)
        legend.get_frame().set_alpha(0.8)
        
        # 添加标题
        title = f"{game_info.get('name', '比赛')} - TOP10积分变化图"
        if scoreboard_data.get('current_group'):
            title += f" ({scoreboard_data['current_group']['group_name']}组)"
        
        plt.title(title, fontsize=18, fontweight='bold', color=text_color, pad=20)
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plt.figtext(0.95, 0.02, f"生成时间: {timestamp}", 
                   ha='right', va='bottom', fontsize=10, color=text_color)
        
        # 保存图片
        if not output_path:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"scoreboard_chart_{game_info.get('name', 'game')}_{timestamp_str}.png"
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', 
                   facecolor=bg_color, edgecolor='none')
        plt.close()
        
        print(f"积分榜图表图片已保存至: {output_path}")
        return output_path
    
    def generate_combined_image(self, game_id, group_id=None, output_dir="./images", theme='light'):
        """生成组合图片（表格+图表）"""
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取数据
        game_info = self.get_game_info(game_id)
        if not game_info:
            return None
        
        scoreboard_data = self.get_scoreboard_data(game_id, group_id, size=100)
        if not scoreboard_data:
            return None
        
        # 生成表格图片
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        table_path = os.path.join(output_dir, f"scoreboard_table_{game_id}_{timestamp_str}.png")
        self.generate_scoreboard_table_image(game_info, scoreboard_data, table_path, theme)
        
        # 生成图表图片
        chart_path = os.path.join(output_dir, f"scoreboard_chart_{game_id}_{timestamp_str}.png")
        self.generate_scoreboard_chart_image(game_info, scoreboard_data, chart_path, theme)
        
        return {
            'table_image': table_path,
            'chart_image': chart_path,
            'game_info': game_info,
            'scoreboard_data': scoreboard_data
        }

def main():
    # ========== 配置参数 ==========
    # 在这里修改您的配置参数
    CONFIG = {
        'game_id': 1,                                    # 比赛ID
        'base_url': 'http://ctf.zypc.online:28888',     # 平台API基础URL
        'token': None,                                   # 用户认证token (如需要请填写)
        'group_id': None,                                # 分组ID (可选)
        'output_dir': './images',                        # 输出目录
        'theme': 'light',                                # 主题: 'light' 或 'dark'
        'type': 'both'                                   # 生成类型: 'table', 'chart', 'both'
    }
    # ========== 配置参数结束 ==========
    
    # 如果仍然想支持命令行参数，可以保留下面的代码
    # 命令行参数会覆盖上面的配置
    parser = argparse.ArgumentParser(description='A1CTF积分榜图片生成器')
    parser.add_argument('game_id', type=int, nargs='?', default=CONFIG['game_id'], help='比赛ID')
    parser.add_argument('--base-url', default=CONFIG['base_url'], 
                       help='平台API基础URL (默认: http://ctf.zypc.online:28888)')
    parser.add_argument('--token', default=CONFIG['token'], help='用户认证token')
    parser.add_argument('--group-id', type=int, default=CONFIG['group_id'], help='分组ID（可选）')
    parser.add_argument('--output-dir', default=CONFIG['output_dir'], help='输出目录 (默认: ./images)')
    parser.add_argument('--theme', choices=['light', 'dark'], default=CONFIG['theme'], 
                       help='主题 (默认: light)')
    parser.add_argument('--type', choices=['table', 'chart', 'both'], default=CONFIG['type'],
                       help='生成类型: table(表格), chart(图表), both(两者) (默认: both)')
    
    args = parser.parse_args()
    
    print("当前配置:")
    print(f"  比赛ID: {args.game_id}")
    print(f"  平台URL: {args.base_url}")
    print(f"  认证Token: {'已设置' if args.token else '未设置'}")
    print(f"  分组ID: {args.group_id if args.group_id else '全部'}")
    print(f"  输出目录: {args.output_dir}")
    print(f"  主题: {args.theme}")
    print(f"  生成类型: {args.type}")
    print("-" * 50)
    
    # 创建生成器
    generator = ScoreboardImageGenerator(args.base_url, args.token)
    
    try:
        if args.type == 'both':
            result = generator.generate_combined_image(
                args.game_id, args.group_id, args.output_dir, args.theme
            )
            if result:
                print(f"积分榜图片生成完成!")
                print(f"表格图片: {result['table_image']}")
                print(f"图表图片: {result['chart_image']}")
        else:
            # 获取数据
            game_info = generator.get_game_info(args.game_id)
            if not game_info:
                print("获取比赛信息失败")
                return
            
            scoreboard_data = generator.get_scoreboard_data(args.game_id, args.group_id, size=100)
            if not scoreboard_data:
                print("获取积分榜数据失败")
                return
            
            os.makedirs(args.output_dir, exist_ok=True)
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if args.type == 'table':
                output_path = os.path.join(args.output_dir, f"scoreboard_table_{args.game_id}_{timestamp_str}.png")
                generator.generate_scoreboard_table_image(game_info, scoreboard_data, output_path, args.theme)
            elif args.type == 'chart':
                output_path = os.path.join(args.output_dir, f"scoreboard_chart_{args.game_id}_{timestamp_str}.png")
                generator.generate_scoreboard_chart_image(game_info, scoreboard_data, output_path, args.theme)
                
    except Exception as e:
        print(f"生成积分榜图片时发生错误: {e}")

if __name__ == "__main__":
    main()
