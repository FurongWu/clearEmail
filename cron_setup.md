# Cron 定时任务设置指南

## 设置 Cron 定时任务

### 1. 编辑 Crontab
```bash
crontab -e
```

### 2. 添加定时任务

#### 每天凌晨2点执行邮箱清理
```bash
# 每天凌晨2点执行邮箱清理
0 2 * * * cd /path/to/your/project && /usr/bin/python3 example_usage.py >> /path/to/your/project/cron.log 2>&1
```

#### 每周一凌晨3点执行邮箱清理
```bash
# 每周一凌晨3点执行邮箱清理
0 3 * * 1 cd /path/to/your/project && /usr/bin/python3 example_usage.py >> /path/to/your/project/cron.log 2>&1
```

#### 每月1号凌晨4点执行邮箱清理
```bash
# 每月1号凌晨4点执行邮箱清理
0 4 1 * * cd /path/to/your/project && /usr/bin/python3 example_usage.py >> /path/to/your/project/cron.log 2>&1
```

### 3. Cron 时间格式说明
```
分钟 小时 日期 月份 星期
 0    2    *    *    *    # 每天凌晨2点
 0    3    *    *    1    # 每周一凌晨3点
 0    4    1    *    *    # 每月1号凌晨4点
```

### 4. 查看 Cron 日志
```bash
# 查看cron执行日志
tail -f /path/to/your/project/cron.log

# 查看系统cron日志
tail -f /var/log/cron
```

## 重要配置

### 1. 确保配置文件正确
- 检查 `email_config.ini` 中的邮箱信息
- 确保 `dry_run = False`（实际删除模式）
- 根据需要设置 `clean_read_no_attachment = True`

### 2. 设置日志轮转
创建 `/etc/logrotate.d/email-cleaner` 文件：
```
/path/to/your/project/cron.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 root root
}
```

### 3. 测试 Cron 任务
```bash
# 手动执行一次测试
cd /path/to/your/project
python3 example_usage.py

# 检查日志文件
tail -f cron.log
```

## 安全建议

1. **首次设置时使用模拟模式**
   - 设置 `dry_run = True`
   - 运行几次确认无误后再改为 `dry_run = False`

2. **定期检查日志**
   - 监控 `cron.log` 文件
   - 检查 `email_cleaner.log` 文件

3. **备份重要邮件**
   - 在启用自动清理前备份重要邮件
   - 定期检查清理结果

4. **设置合理的执行频率**
   - 建议每天或每周执行一次
   - 避免过于频繁的执行

## 故障排除

### 1. 脚本无法执行
```bash
# 检查Python路径
which python3

# 检查脚本权限
chmod +x example_usage.py

# 检查工作目录
pwd
```

### 2. 配置文件问题
```bash
# 检查配置文件是否存在
ls -la email_config.ini

# 检查配置文件权限
chmod 600 email_config.ini
```

### 3. 网络连接问题
```bash
# 测试网络连接
ping imap.qq.com

# 检查防火墙设置
iptables -L
```

## 示例完整配置

### email_config.ini（用于cron）
```ini
[EMAIL]
email = your_email@qq.com
password = your_app_password
email_type = qq
target_senders = spam@example.com,advertisement@company.com
delete_permanently = False
dry_run = False
days_before_delete = 7
clean_read_no_attachment = True
send_notification = True
notification_email = your_email@qq.com
```

### Crontab 条目
```bash
# 每天凌晨2点执行邮箱清理
0 2 * * * cd /home/user/email-cleaner && /usr/bin/python3 example_usage.py >> /home/user/email-cleaner/cron.log 2>&1
``` 