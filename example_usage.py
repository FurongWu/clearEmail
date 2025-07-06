#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮箱清理工具 - 实际运行脚本
执行真实的邮箱清理操作
"""

from clear_qq_email import QQEmailCleaner
import configparser
import os

def check_config():
    """检查配置文件"""
    if not os.path.exists('email_config.ini'):
        print("错误：未找到 email_config.ini 配置文件")
        print("请先运行主程序生成配置文件，或手动创建配置文件")
        return False
    
    config = configparser.ConfigParser()
    config.read('email_config.ini', encoding='utf-8')
    
    email = config.get('EMAIL', 'email', fallback='')
    password = config.get('EMAIL', 'password', fallback='')
    
    if email == 'your_email@qq.com' or not email:
        print("错误：请先配置您的邮箱地址")
        return False
        
    if password == 'your_app_password' or not password:
        print("错误：请先配置您的邮箱授权码")
        return False
        
    return True

def run_email_cleaner():
    """运行邮箱清理器"""
    print("邮箱清理工具 - 实际运行")
    print("=" * 50)
    
    # 检查配置
    if not check_config():
        return
    
    # 创建清理器实例
    cleaner = QQEmailCleaner()
    
    print("\n=== 1. 查看邮箱信息 ===")
    print("正在获取收件箱邮件数量...")
    inbox_count = cleaner.get_email_count()
    
    print("\n正在获取邮件文件夹列表...")
    cleaner.list_folders()
    
    print("\n=== 2. 执行邮箱清理 ===")
    
    # 检查是否配置了目标发送人
    config = configparser.ConfigParser()
    config.read('email_config.ini', encoding='utf-8')
    target_senders = config.get('EMAIL', 'target_senders', fallback='')
    
    total_deleted = 0
    details = []
    
    if target_senders and target_senders != 'sender1@example.com,sender2@example.com':
        print("\n开始清理指定发送人的邮件...")
        # 这里需要手动调用清理并获取结果
        deleted_count = clean_sender_emails(cleaner, config)
        if deleted_count and deleted_count > 0:
            total_deleted += deleted_count
            details.append(f"指定发送人邮件: {deleted_count} 封")
    else:
        print("\n未配置目标发送人，跳过指定发送人邮件清理")
    
    # 检查是否启用清理已读邮件功能
    clean_read = config.getboolean('EMAIL', 'clean_read_no_attachment', fallback=False)
    if clean_read:
        print("\n开始清理已读且不带附件的邮件...")
        deleted_count = cleaner.clean_read_no_attachment_emails()
        if deleted_count and deleted_count > 0:
            total_deleted += deleted_count
            details.append(f"已读且不带附件的邮件: {deleted_count} 封")
    else:
        print("\n未启用清理已读邮件功能，跳过此步骤")
    
    print("\n=== 3. 清理完成 ===")
    print(f"邮箱清理操作已完成！总共删除 {total_deleted} 封邮件")
    print("详细日志请查看 email_cleaner.log 文件")
    
    # 发送汇总通知邮件
    if total_deleted > 0:
        print("\n=== 4. 发送通知邮件 ===")
        details_str = "; ".join(details)
        try:
            cleaner.send_notification_email(total_deleted, details_str)
            print("通知邮件发送成功！")
        except Exception as e:
            print(f"通知邮件发送失败: {str(e)}")

def clean_sender_emails(cleaner, config):
    """清理指定发送人的邮件并返回删除数量"""
    try:
        # 获取目标发送人列表
        target_senders = config['EMAIL']['target_senders'].split(',')
        target_senders = [sender.strip() for sender in target_senders if sender.strip()]
        
        if not target_senders:
            return 0
            
        dry_run = config['EMAIL'].getboolean('dry_run', True)
        days_before_delete = int(config['EMAIL'].get('days_before_delete', 3))
        
        total_deleted = 0
        
        for sender in target_senders:
            print(f"处理来自 {sender} 的邮件...")
            
            # 获取该发送人的所有邮件
            email_ids = cleaner.get_sender_emails(sender)
            
            if email_ids:
                # 删除邮件
                deleted_count = cleaner.delete_emails(email_ids, dry_run, days_before_delete)
                total_deleted += deleted_count
                
                if dry_run:
                    print(f"模拟删除完成，共 {deleted_count} 封邮件")
                else:
                    print(f"删除完成，共 {deleted_count} 封邮件")
                    
        return total_deleted
        
    except Exception as e:
        print(f"清理指定发送人邮件时出错: {str(e)}")
        return 0

def main():
    """主函数 - 无交互模式，适合cron定时任务"""
    print("邮箱清理工具 - 自动运行模式")
    print("=" * 50)
    print("开始执行邮箱清理任务...")
    
    try:
        run_email_cleaner()
        print("邮箱清理任务执行完成")
    except Exception as e:
        print(f"邮箱清理任务执行失败: {str(e)}")
        # 在cron环境中，错误信息会记录到系统日志
        exit(1)

if __name__ == "__main__":
    main() 