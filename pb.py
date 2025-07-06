# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import calendar

import requests
import json
import time
import hashlib
import base64
import hmac
import logging
from urllib.parse import quote_plus

class DingTalkRobot:
    def __init__(self, webhook_url, secret=None, retries=3):
        """
        初始化钉钉机器人
        :param webhook_url: 机器人Webhook地址 (必填)
        :param secret: 加签密钥 (安全设置选择加签时需要)
        :param retries: 消息发送失败重试次数
        """
        self.webhook_url = webhook_url
        self.secret = secret
        self.retries = retries
        self.logger = logging.getLogger("DingTalkRobot")
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def _generate_signature(self):
        """生成加签时间戳和签名 (用于安全验证) [citation:4]"""
        timestamp = str(round(time.time() * 1000))
        if not self.secret:
            return timestamp, ""
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        sign = quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def _send_message(self, payload):
        """发送消息核心逻辑 (含重试机制) [citation:3][citation:5]"""
        timestamp, sign = self._generate_signature()
        params = {"timestamp": timestamp}
        if sign:
            params["sign"] = sign

        for attempt in range(self.retries):
            try:
                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    self.webhook_url,
                    params=params,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=5
                )
                result = response.json()
                if result.get("errcode") == 0:
                    self.logger.info("消息发送成功")
                    return True
                else:
                    self.logger.error(f"发送失败 (尝试 {attempt+1}/{self.retries}): {result.get('errmsg')}")
            except Exception as e:
                self.logger.error(f"网络异常 (尝试 {attempt+1}/{self.retries}): {str(e)}")
            time.sleep(2)  # 等待2秒后重试
        return False

    def send_text(self, content, at_mobiles=None, at_all=False):
        """
        发送文本消息
        :param content: 消息内容
        :param at_mobiles: 被@的手机号列表 (["13800138000"])
        :param at_all: 是否@所有人 (True/False)
        """
        payload = {
            "msgtype": "text",
            "text": {"content": content},
            "at": {"atMobiles": at_mobiles or [], "isAtAll": at_all}
        }
        return self._send_message(payload)

    def send_markdown(self, title, text, at_mobiles=None, at_all=False):
        """
        发送Markdown消息
        :param title: 消息标题
        :param text: Markdown格式内容
        :param at_mobiles: 被@的手机号列表
        """
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": text},
            "at": {"atMobiles": at_mobiles or [], "isAtAll": at_all}
        }
        return self._send_message(payload)



def generate_free_time(first_day):
    """生成上二休二工作制的空闲时间段（字符数≤195）"""
    now = datetime.now()
    year, month = now.year, now.month
    
    # 获取当月最大天数并验证输入有效性
    _, last_day = calendar.monthrange(year, month)
    if not 1 <= first_day <= last_day:
        return f"错误：{month}月没有{first_day}号"

    # 构建日期对象
    day1 = datetime(year, month, first_day)  # 白班日期
    day2 = day1 + timedelta(days=1)          # 夜班日期（自动计算）
    
    # 生成标题
    title = f"1、地球aliyuntts\n2、做不出来的会退费\n3、可接单时间\n"
    output = title
    
    # 周期生成空闲时段（最多6个周期）
    for cycle in range(6):
        # 计算当前周期的日期
        base_date = day1 + timedelta(days=cycle * 4)
        
        # 第二天（夜班）：8:00-12:00空闲
        day2_free = (base_date + timedelta(days=1)).strftime("%Y年%m月%d日【8~12】\n")
        # 第三天：14:00-24:00空闲
        day3_free = (base_date + timedelta(days=2)).strftime("%Y年%m月%d日【14~24】\n")
        # 第四天：全天空闲
        day4_free = (base_date + timedelta(days=3)).strftime("%Y年%m月%d日【8~24】\n")
        #   # 第二天（夜班）：8:00-12:00空闲
        # day2_free = (base_date + timedelta(days=1)).strftime("%d号08:00-12:00\n")
        # # 第三天：14:00-24:00空闲
        # day3_free = (base_date + timedelta(days=2)).strftime("%d号14:00-24:00\n")
        # # 第四天：全天空闲3

        # day4_free = (base_date + timedelta(days=3)).strftime("%d号08:00-24:00\n")
        # 合并空闲区块
        new_block = day2_free + day3_free + day4_free
        
        # 字符数控制（195字符上限）
        if len(output) + len(new_block) > 205:
            break
            
        output += new_block
    
    return output.rstrip()  # 移除末尾换行

if __name__ == "__main__":
    try:
        # day_num = int(input("请输入本月白班起始号数（1-31）: "))
        import sys

        day_num = int(sys.argv[1]) 
        content =  generate_free_time(day_num)
        print("\n" +content)
    except ValueError:
        print("错误：请输入有效的日期号数（如1、15）")
    # 1. 替换为你的机器人Webhook和密钥 (从钉钉群机器人设置获取)
    WEBHOOK_URL = "https://oapi.dingtalk.com/robot/send?access_token=7f403cc1629208925fc451efb855dbd545fd360794c479b014ea6a4c94d70501"
    SECRET = "SEC9c3ed34a5de7d2de46790c82d49de9143247b8f97cae9ec9143f673476d4a736" # 若未启用加签则设为None
    #SECRET = "YOUR_SECRET"  # 若未启用加签则设为None

    
    # 2. 初始化机器人
    robot = DingTalkRobot(webhook_url=WEBHOOK_URL, secret=SECRET)
    
    # 3. 发送测试消息
    # 文本消息 (@指定人)
    robot.send_text(
        content=content,
        #at_mobiles=["15761097319"]  # 替换为你的手机号
    )
    
    # # Markdown消息 (带格式和链接)
    # robot.send_markdown(
    #     title="每日运维报告",
    #     text="### 服务器状态监控\n- ​**CPU**: 负载正常\n- ​**内存**: 使用率 65%\n- [查看详情](http://your-monitor-system.com)"
    # )