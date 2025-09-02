# CTF通知机器人 - Docker部署指南

## 快速开始

### 1. 配置管理员权限

编辑 `nonebot/.env` 文件，设置你的QQ号为超级用户：

```env
SUPERUSERS=["你的QQ号"]
```

### 2. 配置目标群组（可选）

编辑 `nonebot/plugins/ctf_notice/config.py` 文件：

```python
# 设置要接收通知的群组ID列表
TARGET_GROUPS = [
    123456789,  # 你的群组ID
    987654321,  # 你的群组ID
]

# 留空则发送到所有群组
# TARGET_GROUPS = []
```

### 3. 启动服务

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f nonebot

# 停止服务
docker-compose down
```

## 插件功能

### 自动监控

- 插件会在容器启动时自动开始监控
- 每30秒检查一次API获取新通知
- 支持FirstBlood、SecondBlood、ThirdBlood通知

### 手动控制命令

| 命令            | 说明     | 权限要求 |
| --------------- | -------- | -------- |
| `/ctf_start`  | 开始监控 | 超级用户 |
| `/ctf_stop`   | 停止监控 | 超级用户 |
| `/ctf_status` | 查看状态 | 超级用户 |
| `/ctf_check`  | 手动检查 | 超级用户 |
| `/ctf_help`   | 显示帮助 | 所有用户 |

### 通知格式示例

```
🎮 CTF赛事通知 🎮

🥇 FirstBlood
👥 队伍: WinWinWin
📝 题目: Reverse指北
⏰ 时间: 08-28 01:39

#1
```

## 容器管理

### 查看容器状态

```bash
docker-compose ps
```

### 查看实时日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 只查看nonebot日志
docker-compose logs -f nonebot

# 只查看napcat日志
docker-compose logs -f napcat
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 只重启nonebot
docker-compose restart nonebot
```

### 进入容器调试

```bash
# 进入nonebot容器
docker-compose exec nonebot bash

# 进入napcat容器
docker-compose exec napcat bash
```

## 配置文件说明

### 环境变量文件 (.env)

```env
HOST=0.0.0.0
PORT=8080
ONEBOT_WS_URLS=["ws://napcat:3001"]
LOG_LEVEL=INFO
SUPERUSERS=["你的QQ号"]  # 设置管理员
ENVIRONMENT=prod
```

### 插件配置 (plugins/ctf_notice/config.py)

```python
# API配置
NOTICES_API = "http://ctf.zypc.xupt.edu.cn/api/game/3/notices"
CHECK_INTERVAL = 30  # 检查间隔（秒）

# 群组配置
TARGET_GROUPS = []  # 留空发送到所有群组

# 通知类型过滤
NOTICE_CATEGORIES = [
    "FirstBlood",
    "SecondBlood", 
    "ThirdBlood"
]

# 自动启动
AUTO_START = True
```

## 故障排除

### 1. 机器人无法启动

```bash
# 查看容器日志
docker-compose logs nonebot

# 检查依赖安装
docker-compose exec nonebot pip list
```

### 2. 插件无法加载

```bash
# 检查插件目录结构
docker-compose exec nonebot ls -la plugins/

# 检查Python导入
docker-compose exec nonebot python -c "import plugins.ctf_notice"
```

### 3. API连接失败

```bash
# 在容器内测试API
docker-compose exec nonebot python plugins/ctf_notice/test.py
```

### 4. 权限问题

- 确保 `.env` 文件中的 `SUPERUSERS` 包含你的QQ号
- 确保机器人已加入目标群组并有发言权限

### 5. 群组消息发送失败

- 检查机器人是否已加入群组
- 检查机器人在群组中的权限
- 查看napcat连接状态

## 更新插件

如果需要更新插件代码：

```bash
# 1. 停止服务
docker-compose down

# 2. 修改插件代码

# 3. 重新启动（会自动安装新依赖）
docker-compose up -d
```

## 数据持久化

以下目录会持久化保存：

- `./napcat/config` - NapCat配置
- `./ntqq` - QQ数据
- `./nonebot` - NoneBot代码和配置

## 性能优化

- 适当调整 `CHECK_INTERVAL` 避免过于频繁的API请求
- 配置 `TARGET_GROUPS` 避免向不必要的群组发送消息
- 使用 `docker-compose logs --tail=100` 限制日志输出

## 安全建议

1. 不要将包含真实QQ号的 `.env` 文件提交到版本控制
2. 定期更新容器镜像
3. 限制容器网络访问权限
4. 定期备份配置文件
