# NapCat-Docker-A1CTF

本项目在 NapCat Docker 方案基础上扩展，集成了 NoneBot2 与「CTF 赛事通知」插件，实现 CTF 比赛通知实时推送、积分榜图片生成与广告检测等功能，开箱即用地将 NapCat 变为 CTF 群聊助手。

- 上游镜像（NapCat）：[DockerHub: mlikiowa/napcat-docker](https://hub.docker.com/r/mlikiowa/napcat-docker)

## ✨ 本项目在 NapCat 基础上的新增功能

- CTF 通知实时监控：定时拉取赛事通知（支持 FirstBlood/SecondBlood/ThirdBlood 等）并推送到 QQ 群
- 管理员命令集：/ctf_start, /ctf_stop, /ctf_status, /ctf_check, /ctf_help
- 积分榜图片生成：一键生成前 10 队伍分数变化图（关键词：排行榜/积分榜/scoreboard）
- 智能广告检测：支持自动撤回/阈值配置/检测统计（/ad_detect, /ad_control, /ad_config）
- 预置 Docker 编排：包含 napcat 与 nonebot 两个服务，已配置中文字体与依赖
- 一键部署脚本：Windows `deploy.bat`、Linux/macOS `deploy.sh`

## 🖥️ 支持平台/架构
- [x] Linux/Amd64
- [x] Linux/Arm64

---

## 🚀 快速开始

### 方法一：使用部署脚本（推荐）

- Windows（PowerShell）：
    ```powershell
    .\deploy.bat
    ```
- Linux/macOS：
    ```bash
    chmod +x deploy.sh
    ./deploy.sh
    ```

首次启动后，请访问 NapCat WebUI 完成 QQ 登录。

### 方法二：手动使用 Docker Compose

项目已提供 `docker-compose.yaml`，包含 napcat 与 nonebot 两个服务：

```bash
docker-compose up -d
```

查看日志（示例）：

```bash
docker-compose logs -f nonebot
docker-compose logs -f napcat
```

> 提示：容器内已安装中文字体，首次启动会自动安装依赖并运行 `nonebot/start.sh`。

---

## 🔐 基础配置

### 1) 设置超级用户（管理员 QQ）

编辑 `nonebot/.env`：

```env
SUPERUSERS=["你的QQ号"]
```

### 2) 配置目标群（可选）

编辑 `nonebot/plugins/ctf_notice/config.py`：

```python
TARGET_GROUPS = [
        123456789,  # 群1
        987654321,  # 群2
]
# 留空则发送到所有群组：TARGET_GROUPS = []
```

### 3) 启动与常用操作

```bash
docker-compose up -d           # 启动
docker-compose restart         # 重启全部
docker-compose restart nonebot # 仅重启 nonebot
docker-compose ps              # 查看状态
docker-compose logs -f nonebot # 跟随查看 nonebot 日志
docker-compose down            # 停止并移除
```

---

## 🤖 机器人命令

| 命令 | 说明 | 权限 |
|------|------|------|
| `/ctf_start` | 开始监控 | 管理员 |
| `/ctf_stop`  | 停止监控 | 管理员 |
| `/ctf_status`| 查看状态 | 管理员 |
| `/ctf_check` | 手动检查 | 管理员 |
| `/ctf_help`  | 显示帮助 | 所有用户 |
| `/ad_detect <文本>` | 检测广告 | 所有用户 |
| `/ad_control` | 广告策略（开关/阈值/状态）| 管理员 |
| `/ad_config`  | 查看广告检测配置摘要 | 所有用户 |

群聊发送关键词生成积分榜图片：`排行榜` / `积分榜` / `scoreboard`

### 通知消息示例

```
🎮 CTF赛事通知 🎮

🥇 FirstBlood
👥 队伍: WinWinWin
📝 题目: Reverse指北
⏰ 时间: 08-28 01:39

#1
```

---

## 🧩 插件与配置要点（nonebot/plugins/ctf_notice）

- 自动监控：默认开机自动开始，间隔 30s（`AUTO_START=True`, `CHECK_INTERVAL=30`）
- 推送范围：`TARGET_GROUPS=[]` 表示所有群
- 通知类型过滤：`NOTICE_CATEGORIES` 留空表示全部通知
- API 端点（示例）：
    - 通知：`https://ctf.zypc.online/api/game/3/notices`
    - 积分榜：`https://ctf.zypc.online:28888/api/game/3/scoreboard?page=1&size=20`
- 积分榜图片：默认保存到容器内 `/app/nonebot/scoreboard/scoreboard.png`
- 广告检测：支持自动撤回、阈值、关键词、群号模式等多维配置（见 `config.py`）

---

## 🐳 Docker 与容器管理

### 访问 NapCat WebUI 登录

在浏览器打开：`http://<宿主机IP>:6099/webui`

### 常用日志与状态

```bash
docker-compose ps
docker-compose logs -f            # 全部服务
docker-compose logs -f nonebot    # 仅 nonebot
docker-compose logs -f napcat     # 仅 napcat
```

### 进入容器调试

```bash
docker-compose exec nonebot bash
docker-compose exec napcat bash
```

### 数据持久化目录

- `./napcat/config` → 容器 `/app/napcat/config`
- `./ntqq` → 容器 `/app/.config/QQ`
- `./nonebot` → NoneBot 项目与插件代码

---

## ⚙️ 环境变量与路径

- NapCat UID/GID（用于宿主映射权限）：`NAPCAT_UID`, `NAPCAT_GID`
- QQ 数据：`/app/.config/QQ`
- NapCat 配置：`/app/napcat/config`

> 关于 UID/GID 的更多说明，可参考上游文档（容器挂载与权限实践）。

---

## 🛠️ 故障排除

1) 机器人无响应/无法启动

```bash
docker-compose ps
docker-compose logs nonebot
```

2) 插件无法加载/依赖问题

```bash
docker-compose exec nonebot pip list
docker-compose exec nonebot ls -la plugins/
docker-compose exec nonebot python -c "import plugins.ctf_notice"
```

3) API 连接失败

```bash
docker-compose exec nonebot python plugins/ctf_notice/simple_test.py
```

4) 权限与群聊问题

- `.env` 的 `SUPERUSERS` 是否包含你的 QQ
- 机器人是否已加入目标群并有发言/撤回权限

5) 图片发送失败

- 检查生成路径与文件大小（默认限制 5MB）
- 查看 nonebot 日志中的错误堆栈

---

## 📁 主要目录结构

```
NapCat-Docker-A1CTF/
├── docker-compose.yaml          # 编排：napcat + nonebot
├── deploy.bat / deploy.sh       # 一键部署脚本（Win / Linux/macOS）
├── napcat/                      # NapCat 配置（持久化）
├── ntqq/                        # QQ 数据（持久化）
└── nonebot/                     # NoneBot 项目
        ├── .env                     # 环境配置（SUPERUSERS 等）
        ├── bot.py                   # 机器人主程序
        ├── requirements.txt         # Python 依赖
        ├── start.sh                 # 启动脚本
        └── plugins/
                └── ctf_notice/          # CTF 通知插件
                        ├── __init__.py      # 插件入口（自动启动/关闭）
                        ├── config.py        # 插件与广告检测配置
                        ├── handlers.py      # 命令/关键词处理
                        ├── notice_monitor.py# 通知监控逻辑
                        ├── scoreboard.py    # 积分榜绘制
                        └── README.md        # 插件说明
```

---

## 🔒 安全建议

1. 不要将包含真实 QQ 的 `.env` 提交到公共仓库
2. 定期更新镜像与依赖，限制容器网络访问
3. 定期备份 `napcat/config` 与 `ntqq` 数据

---

## 📜 许可证与致谢

- 许可证：MIT
- 致谢：基于并感谢上游 NapCat Docker 镜像与社区生态

