# NoneBot 配置说明

## 快速开始

### 1. 使用主 docker-compose.yaml 启动
```bash
# Windows PowerShell
$env:NAPCAT_UID=1000; $env:NAPCAT_GID=1000; docker-compose up -d

# Linux/macOS
NAPCAT_UID=$(id -u) NAPCAT_GID=$(id -g) docker-compose up -d
```

### 2. 使用专用的 NoneBot compose 文件启动
```bash
# Windows PowerShell
$env:NAPCAT_UID=1000; $env:NAPCAT_GID=1000; docker-compose -f ./compose/nonebot.yml up -d

# Linux/macOS
NAPCAT_UID=$(id -u) NAPCAT_GID=$(id -g) docker-compose -f ./compose/nonebot.yml up -d
```

## 服务配置

### NapCat 配置
- **端口**: 
  - 3000: HTTP API
  - 3001: WebSocket
  - 6099: Web 管理界面
- **配置文件**: `./napcat/config/`
- **QQ 数据**: `./ntqq/`

### NoneBot 配置
- **端口**: 8080 (HTTP 服务)
- **项目目录**: `./nonebot/`
- **连接方式**: WebSocket 连接到 NapCat (ws://napcat:3001)

## 目录结构
```
.
├── napcat/
│   └── config/          # NapCat 配置文件
├── ntqq/               # QQ 数据目录
├── nonebot/            # NoneBot 项目目录
│   ├── .env            # 环境变量配置 (自动生成)
│   ├── bot.py          # 机器人主程序 (自动生成)
│   └── plugins/        # 插件目录 (手动创建)
```

## NoneBot 配置文件

### .env 文件 (自动生成)
```
HOST=0.0.0.0
PORT=8080
ONEBOT_WS_URLS=["ws://napcat:3001"]
```

### bot.py 文件 (自动生成)
```python
import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

if __name__ == "__main__":
    nonebot.run()
```

## 常用命令

### 查看日志
```bash
docker-compose logs -f napcat
docker-compose logs -f nonebot
```

### 重启服务
```bash
docker-compose restart napcat
docker-compose restart nonebot
```

### 停止服务
```bash
docker-compose down
```

## 插件开发

1. 在 `./nonebot/plugins/` 目录下创建插件文件
2. 重启 NoneBot 服务使插件生效
3. 插件示例：
```python
# ./nonebot/plugins/hello.py
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event

hello = on_command("hello", aliases={"你好"})

@hello.handle()
async def handle_hello(bot: Bot, event: Event):
    await hello.send("Hello World!")
```

## 注意事项

1. 首次启动需要登录 QQ，请访问 http://localhost:6099 进行登录
2. NoneBot 会自动安装所需依赖，首次启动可能需要较长时间
3. 如果需要修改端口，请同时修改 docker-compose 文件和 NapCat 配置
4. 建议定期备份 `./napcat/config/` 和 `./ntqq/` 目录
