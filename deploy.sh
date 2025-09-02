#!/bin/bash

echo "🎮 CTF通知机器人部署脚本"
echo "========================="

# 检查当前目录
if [ ! -f "docker-compose.yaml" ]; then
    echo "❌ 请在NapCat-Docker项目根目录运行此脚本"
    exit 1
fi

echo "📋 部署步骤："
echo "1. 配置管理员QQ号"
echo "2. 配置目标群组（可选）"  
echo "3. 启动服务"
echo ""

# 步骤1：配置管理员QQ号
echo "🔧 步骤1: 配置管理员QQ号"
ENV_FILE="nonebot/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "📝 创建.env配置文件..."
    cat > "$ENV_FILE" << 'EOF'
HOST=0.0.0.0
PORT=8080
ONEBOT_WS_URLS=["ws://napcat:3001"]
LOG_LEVEL=INFO

# 超级用户配置（管理员QQ号）
SUPERUSERS=["123456789"]  # 请替换为你的QQ号

# 环境配置
ENVIRONMENT=prod
EOF
fi

echo "⚠️  请编辑 $ENV_FILE 文件，将 SUPERUSERS 设置为你的QQ号"
echo "   示例: SUPERUSERS=[\"1234567890\"]"
echo ""

# 步骤2：配置目标群组
echo "🔧 步骤2: 配置目标群组（可选）"
CONFIG_FILE="nonebot/plugins/ctf_notice/config.py"

echo "💡 编辑 $CONFIG_FILE 文件来设置目标群组:"
echo "   TARGET_GROUPS = [123456789, 987654321]  # 指定群组"
echo "   TARGET_GROUPS = []                       # 发送到所有群组"
echo ""

# 步骤3：启动服务
echo "🚀 步骤3: 启动服务"
echo "执行以下命令启动服务:"
echo ""
echo "   docker-compose up -d"
echo ""
echo "📋 启动后可用的机器人命令:"
echo "   /ctf_start  - 开始监控"
echo "   /ctf_stop   - 停止监控"
echo "   /ctf_status - 查看状态"
echo "   /ctf_check  - 手动检查"
echo "   /ctf_help   - 显示帮助"
echo ""

echo "🔍 查看日志:"
echo "   docker-compose logs -f nonebot"
echo ""

echo "⚠️  注意事项："
echo "1. 确保机器人已加入目标QQ群组"
echo "2. 确保机器人在群组中有发言权限"
echo "3. 管理员命令需要超级用户权限"
echo "4. API可能需要特殊认证，如果无法访问请检查网络"
echo ""

read -p "是否现在启动服务？(y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 启动服务..."
    docker-compose up -d
    echo ""
    echo "✅ 服务已启动！"
    echo "📋 查看状态: docker-compose ps"
    echo "📋 查看日志: docker-compose logs -f nonebot"
else
    echo "💡 请手动执行 'docker-compose up -d' 启动服务"
fi
