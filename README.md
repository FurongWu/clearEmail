# 邮箱自动清理工具

这是一个用于自动清理邮箱中指定发送人邮件和已读且不带附件邮件的Python脚本，支持多种邮箱类型。

## 功能特性

- 🔍 自动搜索指定发送人的邮件
- 📖 清理已读且不带附件的邮件
- 🗑️ 支持批量删除邮件
- 📝 详细的日志记录
- 🛡️ 模拟运行模式，安全预览删除操作
- ⚙️ 配置文件管理，方便设置
- 📊 查看邮箱文件夹和邮件数量
- 📧 清理完成后发送通知邮件
- 🌐 支持多种邮箱类型（QQ、163、126、新浪、Gmail、Outlook、Yahoo等）

## 安装要求

- Python 3.6+
- 标准库模块（无需额外安装包）

## 使用方法

### 1. 获取邮箱授权码

#### QQ邮箱
1. 登录您的QQ邮箱
2. 进入 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务**
4. 开启 **IMAP/SMTP服务**
5. 按照提示获取授权码（不是登录密码）

#### 163邮箱
1. 登录您的163邮箱
2. 进入 **设置** → **POP3/SMTP/IMAP**
3. 开启 **IMAP/SMTP服务**
4. 按照提示获取授权码

#### 其他邮箱
请参考各邮箱服务商的官方文档获取IMAP授权码

### 2. 配置脚本

1. 编辑 `email_config.ini` 文件：
   ```ini
   [EMAIL]
   email = your_email@qq.com
   password = your_app_password
   email_type = qq
   target_senders = spam@example.com,advertisement@company.com
   delete_permanently = False
   dry_run = True
   days_before_delete = 3
   clean_read_no_attachment = False
   send_notification = True
   notification_email = your_email@qq.com
   ```

2. 配置说明：
   - `email`: 您的邮箱地址
   - `password`: 邮箱授权码
   - `email_type`: 邮箱类型（qq, 163, 126, sina, gmail, outlook, yahoo）
   - `target_senders`: 要删除邮件的发送人，多个用逗号分隔
   - `delete_permanently`: 是否永久删除（False=移动到垃圾箱）
   - `dry_run`: 是否模拟运行（True=预览，False=实际删除）
   - `days_before_delete`: 只删除几天前的邮件（默认3，3表示只删除3天前及更早的邮件，3天内新邮件不会被删除）
   - `clean_read_no_attachment`: 是否清理已读且不带附件的邮件
   - `send_notification`: 是否发送清理完成通知邮件
   - `notification_email`: 通知邮件接收地址

### 3. 运行脚本

```