#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ邮箱清理工具 - 快速开始示例
"""

from clear_qq_email import QQEmailCleaner

def quick_clean_example():
    """快速清理示例"""
    print("QQ邮箱清理工具 - 快速开始示例")
    print("=" * 50)
    
    # 创建清理器实例
    cleaner = QQEmailCleaner()
    
    # 示例1: 查看收件箱邮件数量
    print("\n1. 查看收件箱邮件数量...")
    cleaner.get_email_count()
    
    # 示例2: 查看邮件文件夹列表
    print("\n2. 查看邮件文件夹列表...")
    cleaner.list_folders()
    
    # 示例3: 模拟清理邮件（不会实际删除）
    print("\n3. 模拟清理邮件...")
    print("注意：这是模拟运行，不会实际删除邮件")
    cleaner.clean_emails()
    
    print("\n示例完成！")
    print("请编辑 email_config.ini 文件配置您的邮箱信息")

if __name__ == "__main__":
    quick_clean_example() 