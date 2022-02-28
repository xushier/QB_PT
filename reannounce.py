# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
定时
cron: 30 0/5 * * * *
任务名称
new Env('重新汇报前15个种子');

变量
export qb_url=""
export username=""
export password=""
'''

from __qbittorrent import Client
import os,sys

############### QB参数################
try:
    qb_url   = os.environ['qb_url']
    username = os.environ['username']
    password = os.environ['password']
except KeyError:
    print("请检查 qb_url username password 变量是否设置！")
    sys.exit(1)
if __name__ == '__main__':
    qb        = Client(qb_url, username, password)
    torrents  = qb.filter_torrents(filter='all', limit=15, sorted='added_on', reverse=True)
    info_hash = []
    for torrent in torrents:
        info_hash.append(torrent['hash'])
    print(qb.reannounce(info_hash))