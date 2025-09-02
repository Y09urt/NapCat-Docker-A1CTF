# CTF赛事通知机器人 - 快速开始

这是一个基于NoneBot2和NapCat的CTF赛事通知机器人，可以实时监控CTF比赛的FirstBlood、SecondBlood、ThirdBlood通知并推送到QQ群。

## 🚀 快速部署

### 方法1: 使用部署脚本（推荐）

**Windows:**
```cmd
deploy.bat
```

**Linux/macOS:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 方法2: 手动部署

1. **配置管理员权限**
   
   编辑 `nonebot/.env` 文件，设置你的QQ号：
   ```env
   SUPERUSERS=["你的QQ号"]
   ```

2. **配置目标群组（可选）**
   
   编辑 `nonebot/plugins/ctf_notice/config.py`：
   ```python
   TARGET_GROUPS = [
       123456789,  # 群组1
       987654321,  # 群组2
   ]
   # 留空则发送到所有群组: TARGET_GROUPS = []
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

## 📋 机器人命令

| 命令 | 说明 | 权限 |
|------|------|------|
| `/ctf_start` | 开始监控 | 管理员 |
| `/ctf_stop` | 停止监控 | 管理员 |
| `/ctf_status` | 查看状态 | 管理员 |
| `/ctf_check` | 手动检查 | 管理员 |
| `/ctf_help` | 显示帮助 | 所有用户 |

## 🎯 通知格式

```
🎮 CTF赛事通知 🎮

🥇 FirstBlood
👥 队伍: WinWinWin
📝 题目: Reverse指北
⏰ 时间: 08-28 01:39

#1
```

## 🔧 管理命令

```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f nonebot

# 重启服务
docker-compose restart nonebot

# 停止服务
docker-compose down
```

## ⚠️ 注意事项

1. **权限配置**: 确保在 `.env` 文件中正确设置了 `SUPERUSERS`
2. **群组权限**: 确保机器人已加入目标群组并有发言权限
3. **API访问**: 如果API无法访问，请检查网络连接和认证
4. **自动启动**: 插件默认在容器启动时自动开始监控

## 🛠️ 故障排除

### 机器人无响应
```bash
# 检查容器状态
docker-compose ps

# 查看错误日志
docker-compose logs nonebot
```

### API连接失败
```bash
# 在容器内测试API
docker-compose exec nonebot python plugins/ctf_notice/simple_test.py
```

### 权限问题
- 检查 `.env` 文件中的 `SUPERUSERS` 配置
- 确认QQ号格式正确（字符串格式）

## 📁 项目结构

```
NapCat-Docker/
├── docker-compose.yaml          # Docker编排配置
├── deploy.bat                   # Windows部署脚本
├── deploy.sh                    # Linux/macOS部署脚本
└── nonebot/                     # NoneBot项目目录
    ├── .env                     # 环境配置
    ├── bot.py                   # 机器人主程序
    ├── requirements.txt         # Python依赖
    ├── start.sh                 # 启动脚本
    └── plugins/                 # 插件目录
        └── ctf_notice/          # CTF通知插件
            ├── __init__.py      # 插件入口
            ├── config.py        # 插件配置
            ├── handlers.py      # 命令处理
            ├── notice_monitor.py # 通知监控
            ├── simple_test.py   # API测试
            └── README.md        # 插件文档
```

## 🎮 API信息

- **API地址**: `http://ctf.zypc.xupt.edu.cn/api/game/3/notices`
- **检查间隔**: 30秒
- **支持类型**: FirstBlood, SecondBlood, ThirdBlood

## 📄 许可证

MIT License
