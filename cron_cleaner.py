#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮箱清理工具 - Cron定时任务版本
专门用于通过cron定时执行邮箱清理任务
"""

import sys
import os
import logging
from datetime import datetime
from clear_qq_email import QQEmailCleaner

# 设置日志
def setup_logging():
    """设置日志配置"""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('cron_cleaner.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def main():
    """主函数 - 无交互，适合cron执行"""
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("邮箱清理任务开始执行")
    logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # 检查配置文件
        if not os.path.exists('email_config.ini'):
            logger.error("配置文件 email_config.ini 不存在")
            sys.exit(1)
        
        # 创建清理器实例
        cleaner = QQEmailCleaner()
        
        # 执行清理任务
        logger.info("开始执行邮箱清理任务...")
        
        total_deleted = 0
        details = []
        
        # 1. 清理指定发送人的邮件
        logger.info("步骤1: 清理指定发送人的邮件")
        try:
            # 获取配置
            target_senders = cleaner.config['EMAIL']['target_senders'].split(',')
            target_senders = [sender.strip() for sender in target_senders if sender.strip()]
            
            if target_senders and target_senders[0] != 'sender1@example.com':
                for sender in target_senders:
                    logger.info(f"处理来自 {sender} 的邮件...")
                    email_ids = cleaner.get_sender_emails(sender)
                    if email_ids:
                        deleted_count = cleaner.delete_emails(email_ids, False, int(cleaner.config['EMAIL'].get('days_before_delete', 3)))
                        total_deleted += deleted_count
                        details.append(f"{sender}: {deleted_count} 封")
            else:
                logger.info("未配置目标发送人，跳过此步骤")
        except Exception as e:
            logger.error(f"清理指定发送人邮件时出错: {str(e)}")
        
        # 2. 清理已读且不带附件的邮件
        logger.info("步骤2: 清理已读且不带附件的邮件")
        try:
            if cleaner.config['EMAIL'].getboolean('clean_read_no_attachment', False):
                deleted_count = cleaner.clean_read_no_attachment_emails()
                if deleted_count and deleted_count > 0:
                    total_deleted += deleted_count
                    details.append(f"已读且不带附件的邮件: {deleted_count} 封")
            else:
                logger.info("未启用清理已读邮件功能，跳过此步骤")
        except Exception as e:
            logger.error(f"清理已读邮件时出错: {str(e)}")
        
        # 3. 发送汇总通知邮件
        if total_deleted > 0:
            logger.info("步骤3: 发送通知邮件")
            try:
                details_str = "; ".join(details)
                cleaner.send_notification_email(total_deleted, details_str)
                logger.info("通知邮件发送成功")
            except Exception as e:
                logger.error(f"发送通知邮件失败: {str(e)}")
        else:
            logger.info("没有删除任何邮件，跳过通知邮件发送")
        
        logger.info("=" * 60)
        logger.info("邮箱清理任务执行完成")
        logger.info(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"邮箱清理任务执行失败: {str(e)}")
        logger.error(f"错误详情: {sys.exc_info()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 