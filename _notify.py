# coding=utf-8

from logger import Logger
import requests

class SendNotify(object):

    def __init__(self, token:str) -> None:
        self.token   = token
        self.url     = 'http://www.pushplus.plus/send?' + 'token=' + self.token
        self.log     = Logger(file_name='run.log', level='info', when='D', backCount=5, interval=1)

    def pushplus(self, title:str, content:str) -> None:
        pushplus_headers = {'Content-Type':'application/json'}
        # pushplus_data    = {'token': self.token, 'title': title, 'content': content}
        # pushplus_req     = requests.post(self.url, data=pushplus_data, headers=pushplus_headers)
        pushplus_req = requests.get(self.url+'&title='+title+'&content='+content,headers=pushplus_headers)
        if pushplus_req.status_code == 200:
            self.log.info("通知发送成功！")
        else:
            self.log.warning("通知发送失败！")



    def wechat(self, title:str, content:str) -> None:
        pass

    def iyuu(self, title:str, content:str) -> None:
        pass
