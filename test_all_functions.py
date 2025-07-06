#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有邮箱清理功能
包括邮件通知功能
"""

from clear_qq_email import QQEmailCleaner
import configparser

def test_all_functions():
    """测试所有功能"""
    print("邮箱清理工具 - 全功能测试")
    print("=" * 60)
    
    # 检查配置文件
    try:
        config = configparser.ConfigParser()
        config.read('email_config.ini', encoding='utf-8')
        
        email = config.get('EMAIL', 'email')
        email_type = config.get('EMAIL', 'email_type', fallback='qq')
        notification_email = config.get('EMAIL', 'notification_email')
        send_notification = config.getboolean('EMAIL', 'send_notification', fallback=True)
        
        print(f"邮箱地址: {email}")
        print(f"邮箱类型: {email_type}")
        print(f"通知邮箱: {notification_email}")
        print(f"是否启用通知: {send_notification}")
        
    except Exception as e:
        print(f"读取配置文件失败: {str(e)}")
        return
    
    # 创建清理器实例
    cleaner = QQEmailCleaner()
    
    print("\n=== 1. 测试邮箱连接 ===")
    try:
        if cleaner.connect_to_mailbox():
            print("✅ 邮箱连接成功")
            cleaner.disconnect()
        else:
            print("❌ 邮箱连接失败")
            return
    except Exception as e:
        print(f"❌ 邮箱连接出错: {str(e)}")
        return
    
    print("\n=== 2. 测试邮件通知功能 ===")
    try:
        # 模拟清理结果
        total_deleted = 10
        details = "测试邮件1: 5封; 测试邮件2: 3封; 已读邮件: 2封"
        
        print(f"模拟清理结果: {total_deleted} 封邮件")
        print(f"详细信息: {details}")
        
        # 发送通知邮件
        cleaner.send_notification_email(total_deleted, details)
        print("✅ 通知邮件发送成功！")
        print("请检查您的邮箱是否收到通知邮件")
        
    except Exception as e:
        print(f"❌ 发送通知邮件失败: {str(e)}")
        print("可能的原因:")
        print("1. 邮箱授权码不正确")
        print("2. 未开启SMTP服务")
        print("3. 网络连接问题")
        print("4. 邮箱类型配置错误")
    
    print("\n=== 3. 测试邮箱信息获取 ===")
    try:
        cleaner.connect_to_mailbox()
        
        # 获取收件箱邮件数量
        inbox_count = cleaner.get_email_count()
        print(f"收件箱邮件数量: {inbox_count} 封")
        
        # 获取文件夹列表
        print("邮件文件夹列表:")
        cleaner.list_folders()
        
        cleaner.disconnect()
        print("✅ 邮箱信息获取成功")
        
    except Exception as e:
        print(f"❌ 获取邮箱信息失败: {str(e)}")
    
    print("\n=== 4. 功能说明 ===")
    print("现在您可以运行以下脚本:")
    print("1. python example_usage.py - 交互式清理（带通知）")
    print("2. python cron_cleaner.py - 自动清理（适合cron）")
    print("3. python test_email_notification.py - 仅测试通知功能")
    
    print("\n=== 5. Cron 设置建议 ===")
    print("每天凌晨2点执行:")
    print("0 2 * * * cd /path/to/your/project && /usr/bin/python3 cron_cleaner.py >> /path/to/your/project/cron.log 2>&1")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_all_functions() 