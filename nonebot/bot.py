import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

# 初始化nonebot
nonebot.init()

# 获取驱动器并注册适配器
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

# 加载插件
nonebot.load_plugins("plugins")  # 加载plugins目录下的所有插件

if __name__ == "__main__":
    nonebot.run()
