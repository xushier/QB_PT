# coding=utf-8
# Created By Xushier  QQ:1575659493

import requests

class SendNotify(object):

    def __init__(self, token:str) -> None:
        self.token   = token
        self.url     = 'http://www.pushplus.plus/send?' + 'token=' + self.token

    def pushplus(self, title:str, content:str) -> None:
        if self.token:
            pushplus_headers = {'Content-Type':'application/json'}
            pushplus_req = requests.get(self.url+'&title='+title+'&content='+content,headers=pushplus_headers)
            if pushplus_req.status_code == 200:
                print("通知发送成功！")
            else:
                print("通知发送失败！")
        else:
            print("pushplus token 未设置！")



    def wechat(self, title:str, content:str) -> None:
        pass

    def iyuu(self, title:str, content:str) -> None:
        pass