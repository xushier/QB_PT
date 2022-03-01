# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
定时
cron: 30 0/30 * * * *
任务名称
new Env('删种');
'''

from __qbittorrent import Client

qb = Client()
torrents = qb.get_satisfied_torrents()
qb.delete(torrents)