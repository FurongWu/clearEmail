#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试邮件通知功能
"""

from clear_qq_email import QQEmailCleaner
import configparser

def test_email_notification():
    """测试邮件通知功能"""
    print("测试邮件通知功能")
    print("=" * 50)
    
    # 检查配置文件
    try:
        config = configparser.ConfigParser()
        config.read('email_config.ini', encoding='utf-8')
        
        email = config.get('EMAIL', 'email')
        password = config.get('EMAIL', 'password')
        notification_email = config.get('EMAIL', 'notification_email')
        
        print(f"邮箱地址: {email}")
        print(f"通知邮箱: {notification_email}")
        print(f"是否启用通知: {config.getboolean('EMAIL', 'send_notification', fallback=True)}")
        
    except Exception as e:
        print(f"读取配置文件失败: {str(e)}")
        return
    
    # 创建清理器实例
    cleaner = QQEmailCleaner()
    
    # 测试发送通知邮件
    print("\n开始测试发送通知邮件...")
    
    try:
        # 模拟清理结果
        total_deleted = 5
        details = "测试邮件1: 2封; 测试邮件2: 3封"
        
        print(f"模拟清理结果: {total_deleted} 封邮件")
        print(f"详细信息: {details}")
        
        # 发送通知邮件
        cleaner.send_notification_email(total_deleted, details)
        
        print("通知邮件发送测试完成！")
        print("请检查您的邮箱是否收到通知邮件")
        
    except Exception as e:
        print(f"发送通知邮件失败: {str(e)}")
        print("可能的原因:")
        print("1. 邮箱授权码不正确")
        print("2. 未开启SMTP服务")
        print("3. 网络连接问题")
        print("4. 邮箱类型配置错误")

if __name__ == "__main__":
    test_email_notification() 