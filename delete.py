# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
定时
cron: 0 0/60 * * *
任务名称
new Env('删除指定种子');

变量
export qb_url
export username
export password
'''

from __qbittorrent import Client
import os,sys

############### QB参数################
try:
    qb_url   = os.environ['qb_url']
    username = os.environ['username']
    password = os.environ['password']
except KeyError:
    print("未设置变量！")
    sys.exit(1)

if __name__ == '__main__':
    qb = Client(qb_url, username, password)
    torrents = qb.get_satisfied_torrents()
    qb.delete(torrents)
        
    

