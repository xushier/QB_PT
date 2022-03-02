# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
变量
export PUSH_PLUS_TOKEN=""
'''

import requests,os

push_config = {
    'HITOKOTO': False,                  # 启用一言（随机句子）

    'BARK_PUSH': '',                    # bark IP 或设备码，例：https://api.day.app/DxHcxxxxxRxxxxxxcm/
    'BARK_ARCHIVE': '',                 # bark 推送是否存档
    'BARK_GROUP': '',                   # bark 推送分组
    'BARK_SOUND': '',                   # bark 推送声音
    'BARK_ICON': '',                    # bark 推送图标

    'CONSOLE': True,                    # 控制台输出

    'DD_BOT_SECRET': '',                # 钉钉机器人的 DD_BOT_SECRET
    'DD_BOT_TOKEN': '',                 # 钉钉机器人的 DD_BOT_TOKEN

    'FSKEY': '',                        # 飞书机器人的 FSKEY

    'GOTIFY_URL': '',                   # gotify地址,如https://push.example.de:8080
    'GOTIFY_TOKEN': '',                 # gotify的消息应用token
    'GOTIFY_PRIORITY': 0,               # 推送消息优先级,默认为0

    'IGOT_PUSH_KEY': '',                # iGot 聚合推送的 IGOT_PUSH_KEY

    'PUSH_KEY': '',                     # server 酱的 PUSH_KEY，兼容旧版与 Turbo 版

    'PUSH_PLUS_TOKEN': '',              # push+ 微信推送的用户令牌
    'PUSH_PLUS_USER': '',               # push+ 微信推送的群组编码

    'QMSG_KEY': '',                     # qmsg 酱的 QMSG_KEY
    'QMSG_TYPE': '',                    # qmsg 酱的 QMSG_TYPE

    'QYWX_AM': '',                      # 企业微信应用

    'QYWX_KEY': '',                     # 企业微信机器人

    'TG_BOT_TOKEN': '',                 # tg 机器人的 TG_BOT_TOKEN，例：1407203283:AAG9rt-6RDaaX0HBLZQq0laNOh898iFYaRQ
    'TG_USER_ID': '',                   # tg 机器人的 TG_USER_ID，例：1434078534
    'TG_API_HOST': '',                  # tg 代理 api
    'TG_PROXY_AUTH': '',                # tg 代理认证参数
    'TG_PROXY_HOST': '',                # tg 机器人的 TG_PROXY_HOST
    'TG_PROXY_PORT': '',                # tg 机器人的 TG_PROXY_PORT
}

for k in push_config:
    if os.getenv(k):
        v = os.getenv(k)
        push_config[k] = v

class Send_Notify(object):

    def __init__(self) -> None:
        self.pushplus_url = 'http://www.pushplus.plus/send?' + 'token='

    def pushplus(self, title:str, content:str) -> None:
        if not push_config.get("PUSH_PLUS_TOKEN"):
            print("PUSHPLUS 服务的 PUSH_PLUS_TOKEN 未设置!!\n取消推送")
            return
        print("PUSHPLUS 服务启动")

        pushplus_headers = {'Content-Type':'application/json'}
        pushplus_req = requests.get(self.pushplus_url + push_config.get("PUSH_PLUS_TOKEN") +'&title='+title+'&content='+content,headers=pushplus_headers)
        if pushplus_req.status_code == 200:
            print("通知发送成功！")
        else:
            print("通知发送失败！")



    def wechat(self, title:str, content:str) -> None:
        pass

    def iyuu(self, title:str, content:str) -> None:
        pass