🔐 重要安全提示
==================

在使用此CTF通知机器人之前，请务必完成以下配置：

1. 📋 复制凭据模板：
   ```
   复制 nonebot/plugins/ctf_notice/credentials.example.py 
   为   nonebot/plugins/ctf_notice/credentials.py
   ```

2. ✏️ 编辑登录信息：
   在 credentials.py 中填入你的真实A1CTF登录凭据

3. ⚠️ 安全注意事项：
   - credentials.py 已自动添加到 .gitignore
   - 请勿将真实密码提交到版本控制系统  
   - 建议使用专门的机器人账号

如果你看到导入错误，说明 credentials.py 文件不存在或配置不正确。

详细配置说明请查看：nonebot/plugins/ctf_notice/README.md
