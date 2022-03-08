# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
变量
export PUSH_PLUS_TOKEN=""
export QYWX="" #以英文逗号分割，顺序是 corpid,corpsecret,touser,agentid （企业ID，企业密钥，用户ID，客户端ID）
'''

import requests,os,re

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

    'QYWX': '',                      # 企业微信应用

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

    def wechat(self, title: str, content: str) -> None:
        """
        通过 企业微信 APP 推送消息。
        """
        if not push_config.get("QYWX"):
            print("QYWX 未设置!!\n取消推送")
            return
        QYWX_AY = re.split(",", push_config.get("QYWX"))
        if 4 < len(QYWX_AY) > 5:
            print("QYWX 设置错误!!\n取消推送")
            return
        print("企业微信 APP 服务启动")

        corpid = QYWX_AY[0]
        corpsecret = QYWX_AY[1]
        touser = QYWX_AY[2]
        agentid = QYWX_AY[3]
        try:
            media_id = QYWX_AY[4]
        except IndexError:
            media_id = ""
        wx = We_Com(corpid, corpsecret, agentid)
        # 如果没有配置 media_id 默认就以 text 方式发送
        if not media_id:
            message = title + "\n\n" + content
            response = wx.send_text(message, touser)
        else:
            response = wx.send_mpnews(title, content, media_id, touser)

        if response == "ok":
            print("企业微信推送成功！")
        else:
            print("企业微信推送失败！错误信息如下：\n", response)

        def iyuu(self, title:str, content:str) -> None:
            pass

class We_Com(object):
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid

    def get_access_token(self):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        values = {
            "corpid": self.CORPID,
            "corpsecret": self.CORPSECRET,
        }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {"content": message},
            "safe": "0",
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace("\n", "<br/>"),
                        "digest": message,
                    }
                ]
            },
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

