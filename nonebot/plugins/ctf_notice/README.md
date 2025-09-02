# CTF赛事通知插件

这是一个用于实时播报CTF比赛通知的NoneBot插件，支持监控FirstBlood、SecondBlood、ThirdBlood等通知。

## 功能特性

- 🔄 实时监控CTF比赛通知API
- 🎯 支持FirstBlood、SecondBlood、ThirdBlood通知
- 📢 自动推送到指定QQ群组
- ⚙️ 可配置监控间隔和目标群组
- 🎮 丰富的emoji和格式化消息
- 👑 管理员命令控制

## 安装配置

### 1. 安装依赖

```bash
cd nonebot
pip install -r requirements.txt
```

### 2. 配置管理员

编辑 `.env` 文件，将 `SUPERUSERS` 设置为你的QQ号：

```env
SUPERUSERS=["你的QQ号"]
```

### 3. 配置群组（可选）

编辑 `plugins/ctf_notice/config.py`，设置要接收通知的群组：

```python
# 群组配置 - 需要接收通知的群组ID列表
# 留空则发送到所有群组
TARGET_GROUPS = [
    123456789,  # 你的群组ID
    987654321,  # 你的群组ID
]
```

### 4. 配置API（可选）

如果API地址发生变化，可以在 `config.py` 中修改：

```python
NOTICES_API = "http://ctf.xypc.xupt.edu.cn/api/game/3/notices"
```

## 使用方法


### 基本命令

| 命令/关键词 | 别名 | 说明 | 权限 |
|------|------|------|------|
| `/ctf_start` | `ctf开始`, `开始监控` | 开始监控 | 超级用户 |
| `/ctf_stop` | `ctf停止`, `停止监控` | 停止监控 | 超级用户 |
| `/ctf_status` | `ctf状态`, `监控状态` | 查看状态 | 超级用户 |
| `/ctf_check` | `ctf检查`, `手动检查` | 手动检查 | 超级用户 |
| `/ctf_help` | `ctf帮助` | 显示帮助 | 所有用户 |
| `排行榜` |  | 群聊发送此关键词，自动生成并发送最新积分榜图片 | 所有群成员 |


### 使用示例

1. **开始监控**
   ```
   /ctf_start
   ```

2. **查看状态**
   ```
   /ctf_status
   ```

3. **停止监控**
   ```
   /ctf_stop
   ```

4. **获取积分榜图片**
   
   在群聊中直接发送：
   ```
   排行榜
   ```
   机器人会自动生成并发送最新积分榜图片。

4. **手动检查新通知**
   ```
   /ctf_check
   ```

## 通知格式

插件会发送格式化的通知消息，包含：

```
🎮 CTF赛事通知 🎮

🥇 FirstBlood
👥 队伍: WinWinWin
📝 题目: Reverse指北
⏰ 时间: 08-28 01:39

#1
```

## 配置选项

### config.py 配置文件

```python
# API配置
NOTICES_API = "http://ctf.xypc.xupt.edu.cn/api/game/3/notices"
CHECK_INTERVAL = 30  # 检查间隔（秒）

# 群组配置
TARGET_GROUPS = []  # 留空则发送到所有群组

# 通知过滤配置
NOTICE_CATEGORIES = [
    "FirstBlood",
    "SecondBlood", 
    "ThirdBlood"
]

# 是否在启动时自动开始监控
AUTO_START = True
```

## 自动启动

插件默认在机器人启动时自动开始监控。如果不希望自动启动，可以将 `config.py` 中的 `AUTO_START` 设置为 `False`。

## 故障排除

### 1. 插件无法加载
- 检查是否安装了所需依赖：`aiohttp`、`nonebot-plugin-apscheduler`
- 检查插件目录结构是否正确

### 2. 无法发送消息
- 检查机器人是否已加入目标群组
- 检查机器人是否有发言权限
- 检查 `SUPERUSERS` 配置是否正确

### 3. API请求失败
- 检查网络连接
- 检查API地址是否正确
- 检查API服务是否正常

### 4. 权限不足
- 确保发送命令的用户在 `SUPERUSERS` 列表中
- 管理员命令需要超级用户权限

## 注意事项

1. 请适当设置检查间隔，避免过于频繁的API请求
2. 建议配置特定的群组列表，避免打扰其他群组
3. 插件会记录已处理的通知ID，重启后不会重复发送旧通知
4. 如果API结构发生变化，可能需要更新插件代码

## 许可证

此插件遵循 MIT 许可证。
