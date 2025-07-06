#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ邮箱自动清理工具
自动删除来自指定发送人的邮件
"""

import imaplib
import email
import os
import configparser
from email.header import decode_header
from datetime import datetime
import logging

class QQEmailCleaner:
    def __init__(self, config_file='email_config.ini'):
        """
        初始化邮箱清理器
        
        Args:
            config_file (str): 配置文件路径
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.mail = None
        
        # 设置日志
        self.setup_logging()
        
        # 邮箱服务器配置
        self.email_servers = {
            'qq': {'server': 'imap.qq.com', 'port': 993},
            '163': {'server': 'imap.163.com', 'port': 993},
            '126': {'server': 'imap.126.com', 'port': 993},
            'sina': {'server': 'imap.sina.com', 'port': 993},
            'gmail': {'server': 'imap.gmail.com', 'port': 993},
            'outlook': {'server': 'outlook.office365.com', 'port': 993},
            'yahoo': {'server': 'imap.mail.yahoo.com', 'port': 993}
        }
        
    def setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('email_cleaner.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            config.read(self.config_file, encoding='utf-8')
        else:
            # 创建默认配置
            config['EMAIL'] = {
                'email': 'your_email@qq.com',
                'password': 'your_app_password',
                'email_type': 'qq',
                'target_senders': 'sender1@example.com,sender2@example.com',
                'delete_permanently': 'False',
                'dry_run': 'True',
                'days_before_delete': '3',
                'clean_read_no_attachment': 'False',
                'send_notification': 'True',
                'notification_email': 'your_email@qq.com'
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
                
            print(f"已创建配置文件: {self.config_file}")
            print("请编辑配置文件，填入您的邮箱信息")
            
        return config
        
    def connect_to_mailbox(self):
        """连接到邮箱"""
        try:
            email_type = self.config['EMAIL'].get('email_type', 'qq')
            if email_type not in self.email_servers:
                self.logger.error(f"不支持的邮箱类型: {email_type}")
                return False
                
            server_config = self.email_servers[email_type]
            self.mail = imaplib.IMAP4_SSL(server_config['server'], server_config['port'])
            email_address = self.config['EMAIL']['email']
            password = self.config['EMAIL']['password']
            
            self.mail.login(email_address, password)
            self.logger.info(f"成功连接到{email_type}邮箱: {email_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"连接邮箱失败: {str(e)}")
            return False
            
    def disconnect(self):
        """断开邮箱连接"""
        if self.mail:
            try:
                self.mail.logout()
                self.logger.info("已断开邮箱连接")
            except Exception as e:
                self.logger.error(f"断开连接时出错: {str(e)}")
                
    def get_sender_emails(self, sender):
        """获取指定发送人的邮件ID列表"""
        try:
            if not self.mail:
                self.logger.error("邮箱连接未建立")
                return []
                
            # 选择收件箱
            self.mail.select('INBOX')
            
            # 搜索来自指定发送人的邮件
            search_criteria = f'FROM "{sender}"'
            status, message_ids = self.mail.search(None, search_criteria)
            
            if status == 'OK' and message_ids and message_ids[0]:
                email_ids = message_ids[0].split()
                self.logger.info(f"找到来自 {sender} 的邮件 {len(email_ids)} 封")
                return email_ids
            else:
                self.logger.info(f"未找到来自 {sender} 的邮件")
                return []
                
        except Exception as e:
            self.logger.error(f"搜索邮件时出错: {str(e)}")
            return []
            
    def get_email_info(self, email_id):
        """获取邮件信息"""
        try:
            if not self.mail:
                return None
                
            status, msg_data = self.mail.fetch(email_id, '(RFC822)')
            if status == 'OK' and msg_data and len(msg_data) > 0:
                email_body = msg_data[0][1]
                if isinstance(email_body, bytes):
                    email_message = email.message_from_bytes(email_body)
                    
                    # 解析邮件头信息
                    subject = decode_header(email_message['subject'])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode('utf-8', errors='ignore')
                        
                    from_addr = decode_header(email_message['from'])[0][0]
                    if isinstance(from_addr, bytes):
                        from_addr = from_addr.decode('utf-8', errors='ignore')
                        
                    date = email_message['date']
                    
                    return {
                        'subject': subject,
                        'from': from_addr,
                        'date': date
                    }
        except Exception as e:
            self.logger.error(f"获取邮件信息时出错: {str(e)}")
            
        return None
        
    def delete_emails(self, email_ids, dry_run=True, days_before_delete=3):
        """删除邮件，只删除N天前的邮件"""
        deleted_count = 0
        
        if not self.mail:
            self.logger.error("邮箱连接未建立")
            return deleted_count
        
        now = datetime.now()
        
        for email_id in email_ids:
            try:
                # 获取邮件信息用于日志
                email_info = self.get_email_info(email_id)
                
                # 判断邮件日期
                skip = False
                if email_info and email_info['date']:
                    try:
                        # 解析邮件日期
                        from email.utils import parsedate_to_datetime
                        mail_date = parsedate_to_datetime(email_info['date'])
                        if mail_date.tzinfo is not None:
                            mail_date = mail_date.astimezone().replace(tzinfo=None)
                        days_diff = (now - mail_date).days
                        if days_diff < days_before_delete:
                            skip = True
                    except Exception as e:
                        self.logger.warning(f"解析邮件日期失败: {email_info['date']}，跳过此邮件。错误: {str(e)}")
                        skip = True
                if skip:
                    self.logger.info(f"[跳过] 邮件ID: {email_id.decode()}，日期: {email_info['date'] if email_info else '未知'}，未达到删除天数")
                    continue
                
                if dry_run:
                    self.logger.info(f"[模拟删除] 邮件ID: {email_id.decode()}")
                    if email_info:
                        self.logger.info(f"  主题: {email_info['subject']}")
                        self.logger.info(f"  发件人: {email_info['from']}")
                        self.logger.info(f"  日期: {email_info['date']}")
                    deleted_count += 1
                else:
                    # 实际删除邮件
                    self.mail.store(email_id, '+FLAGS', '\\Deleted')
                    self.logger.info(f"[已删除] 邮件ID: {email_id.decode()}")
                    if email_info:
                        self.logger.info(f"  主题: {email_info['subject']}")
                        self.logger.info(f"  发件人: {email_info['from']}")
                    deleted_count += 1
                    
            except Exception as e:
                self.logger.error(f"删除邮件时出错: {str(e)}")
                
        # 如果实际删除，则执行expunge
        if not dry_run and deleted_count > 0:
            try:
                self.mail.expunge()
                self.logger.info("已永久删除邮件")
            except Exception as e:
                self.logger.error(f"永久删除邮件时出错: {str(e)}")
                
        return deleted_count
        
    def clean_emails(self):
        """清理邮件主函数"""
        if not self.connect_to_mailbox():
            return
            
        try:
            # 获取目标发送人列表
            target_senders = self.config['EMAIL']['target_senders'].split(',')
            target_senders = [sender.strip() for sender in target_senders if sender.strip()]
            
            if not target_senders:
                self.logger.warning("未配置目标发送人")
                return
                
            dry_run = self.config['EMAIL'].getboolean('dry_run', True)
            delete_permanently = self.config['EMAIL'].getboolean('delete_permanently', False)
            days_before_delete = int(self.config['EMAIL'].get('days_before_delete', 3))
            
            total_deleted = 0
            details = []
            
            for sender in target_senders:
                self.logger.info(f"开始处理来自 {sender} 的邮件...")
                
                # 获取该发送人的所有邮件
                email_ids = self.get_sender_emails(sender)
                
                if email_ids:
                    # 删除邮件
                    deleted_count = self.delete_emails(email_ids, dry_run, days_before_delete)
                    total_deleted += deleted_count
                    details.append(f"{sender}: {deleted_count} 封")
                    
                    if dry_run:
                        self.logger.info(f"模拟删除完成，共 {deleted_count} 封邮件")
                    else:
                        self.logger.info(f"删除完成，共 {deleted_count} 封邮件")
                        
            self.logger.info(f"清理完成，总共处理 {total_deleted} 封邮件")
            
            # 发送通知邮件
            if total_deleted > 0:
                details_str = "; ".join(details)
                self.send_notification_email(total_deleted, details_str)
            
        except Exception as e:
            self.logger.error(f"清理邮件时出错: {str(e)}")
        finally:
            self.disconnect()
            
    def list_folders(self):
        """列出所有邮件文件夹"""
        if not self.connect_to_mailbox():
            return
            
        try:
            status, folders = self.mail.list()
            if status == 'OK':
                self.logger.info("邮件文件夹列表:")
                for folder in folders:
                    folder_name = folder.decode().split('"')[-2]
                    self.logger.info(f"  - {folder_name}")
        except Exception as e:
            self.logger.error(f"获取文件夹列表时出错: {str(e)}")
        finally:
            self.disconnect()
            
    def get_email_count(self, folder='INBOX'):
        """获取指定文件夹的邮件数量"""
        if not self.connect_to_mailbox():
            return 0
            
        try:
            self.mail.select(folder)
            status, messages = self.mail.search(None, 'ALL')
            if status == 'OK':
                count = len(messages[0].split())
                self.logger.info(f"{folder} 文件夹共有 {count} 封邮件")
                return count
        except Exception as e:
            self.logger.error(f"获取邮件数量时出错: {str(e)}")
        finally:
            self.disconnect()
            
        return 0
        
    def get_read_no_attachment_emails(self, days_before_delete=3):
        """获取已读且不带附件的邮件ID列表"""
        try:
            if not self.mail:
                self.logger.error("邮箱连接未建立")
                return []
                
            # 选择收件箱
            self.mail.select('INBOX')
            
            # 搜索已读邮件
            status, message_ids = self.mail.search(None, 'SEEN')
            
            if status != 'OK' or not message_ids or not message_ids[0]:
                self.logger.info("未找到已读邮件")
                return []
                
            email_ids = message_ids[0].split()
            filtered_ids = []
            now = datetime.now()
            
            for email_id in email_ids:
                try:
                    email_info = self.get_email_info(email_id)
                    if not email_info:
                        continue
                        
                    # 检查日期
                    if email_info['date']:
                        try:
                            from email.utils import parsedate_to_datetime
                            mail_date = parsedate_to_datetime(email_info['date'])
                            if mail_date.tzinfo is not None:
                                mail_date = mail_date.astimezone().replace(tzinfo=None)
                            days_diff = (now - mail_date).days
                            if days_diff < days_before_delete:
                                continue
                        except Exception:
                            continue
                    
                    # 检查是否有附件
                    has_attachment = self.check_has_attachment(email_id)
                    if not has_attachment:
                        filtered_ids.append(email_id)
                        
                except Exception as e:
                    self.logger.warning(f"检查邮件 {email_id.decode()} 时出错: {str(e)}")
                    continue
                    
            self.logger.info(f"找到已读且不带附件的邮件 {len(filtered_ids)} 封")
            return filtered_ids
            
        except Exception as e:
            self.logger.error(f"搜索已读邮件时出错: {str(e)}")
            return []
            
    def check_has_attachment(self, email_id):
        """检查邮件是否有附件"""
        try:
            if not self.mail:
                return False
                
            status, msg_data = self.mail.fetch(email_id, '(RFC822)')
            if status == 'OK' and msg_data and len(msg_data) > 0:
                email_body = msg_data[0][1]
                if isinstance(email_body, bytes):
                    email_message = email.message_from_bytes(email_body)
                    
                    # 检查是否有附件
                    for part in email_message.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is not None:
                            return True
                            
            return False
            
        except Exception as e:
            self.logger.error(f"检查附件时出错: {str(e)}")
            return False
            
    def send_notification_email(self, total_deleted, details):
        """发送清理完成通知邮件"""
        try:
            if not self.config['EMAIL'].getboolean('send_notification', True):
                return
                
            notification_email = self.config['EMAIL'].get('notification_email', '')
            if not notification_email:
                self.logger.warning("未配置通知邮箱地址")
                return
                
            # 获取SMTP配置
            email_type = self.config['EMAIL'].get('email_type', 'qq')
            smtp_config = self.get_smtp_config(email_type)
            
            if not smtp_config:
                self.logger.error(f"不支持的邮箱类型: {email_type}")
                return
                
            # 发送邮件
            self.send_email_via_smtp(
                smtp_config,
                notification_email,
                total_deleted,
                details
            )
            
        except Exception as e:
            self.logger.error(f"发送通知邮件时出错: {str(e)}")
            
    def get_smtp_config(self, email_type):
        """获取SMTP服务器配置"""
        smtp_configs = {
            'qq': {
                'server': 'smtp.qq.com',
                'port': 587,
                'use_tls': True
            },
            '163': {
                'server': 'smtp.163.com',
                'port': 587,
                'use_tls': True
            },
            '126': {
                'server': 'smtp.126.com',
                'port': 587,
                'use_tls': True
            },
            'sina': {
                'server': 'smtp.sina.com',
                'port': 587,
                'use_tls': True
            },
            'gmail': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True
            },
            'outlook': {
                'server': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True
            },
            'yahoo': {
                'server': 'smtp.mail.yahoo.com',
                'port': 587,
                'use_tls': True
            }
        }
        return smtp_configs.get(email_type)
        
    def send_email_via_smtp(self, smtp_config, to_email, total_deleted, details):
        """通过SMTP发送邮件"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.config['EMAIL']['email']
            msg['To'] = to_email
            msg['Subject'] = f"邮箱清理完成通知 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # 邮件内容
            body = f"""
邮箱清理任务执行完成

执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
清理邮箱: {self.config['EMAIL']['email']}

清理结果:
- 总共删除邮件: {total_deleted} 封
- 详细信息: {details}

清理配置:
- 邮箱类型: {self.config['EMAIL'].get('email_type', 'qq')}
- 删除天数限制: {self.config['EMAIL'].get('days_before_delete', '3')} 天
- 清理已读邮件: {self.config['EMAIL'].get('clean_read_no_attachment', 'False')}

此邮件由邮箱自动清理工具发送
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 连接SMTP服务器
            if smtp_config['use_tls']:
                server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'])
            
            # 登录
            server.login(self.config['EMAIL']['email'], self.config['EMAIL']['password'])
            
            # 发送邮件
            text = msg.as_string()
            server.sendmail(self.config['EMAIL']['email'], to_email, text)
            server.quit()
            
            self.logger.info(f"通知邮件发送成功: {to_email}")
            
        except Exception as e:
            self.logger.error(f"SMTP发送邮件失败: {str(e)}")
            raise
            
    def clean_read_no_attachment_emails(self):
        """清理已读且不带附件的邮件"""
        if not self.connect_to_mailbox():
            return
            
        try:
            days_before_delete = int(self.config['EMAIL'].get('days_before_delete', 3))
            dry_run = self.config['EMAIL'].getboolean('dry_run', True)
            
            self.logger.info(f"开始清理已读且不带附件的邮件（{days_before_delete}天前）...")
            
            # 获取已读且不带附件的邮件
            email_ids = self.get_read_no_attachment_emails(days_before_delete)
            
            if email_ids:
                # 删除邮件
                deleted_count = self.delete_emails(email_ids, dry_run, days_before_delete)
                
                if dry_run:
                    self.logger.info(f"模拟删除完成，共 {deleted_count} 封邮件")
                else:
                    self.logger.info(f"删除完成，共 {deleted_count} 封邮件")
                    
                # 发送通知邮件
                if deleted_count > 0:
                    details = f"已读且不带附件的邮件: {deleted_count} 封"
                    self.send_notification_email(deleted_count, details)
                    
                return deleted_count
            else:
                self.logger.info("没有找到符合条件的邮件")
                return 0
                
        except Exception as e:
            self.logger.error(f"清理已读邮件时出错: {str(e)}")
            return 0
        finally:
            self.disconnect()


def main():
    """主函数"""
    print("邮箱自动清理工具")
    print("=" * 50)
    
    cleaner = QQEmailCleaner()
    
    while True:
        print("\n请选择操作:")
        print("1. 清理指定发送人的邮件")
        print("2. 清理已读且不带附件的邮件")
        print("3. 查看邮件文件夹列表")
        print("4. 查看收件箱邮件数量")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == '1':
            print("\n开始清理指定发送人的邮件...")
            cleaner.clean_emails()
            
        elif choice == '2':
            print("\n开始清理已读且不带附件的邮件...")
            cleaner.clean_read_no_attachment_emails()
            
        elif choice == '3':
            print("\n获取文件夹列表...")
            cleaner.list_folders()
            
        elif choice == '4':
            print("\n获取收件箱邮件数量...")
            cleaner.get_email_count()
            
        elif choice == '5':
            print("退出程序")
            break
            
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    main()
