# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
定时
cron: 30 0/5 * * * *
任务名称
new Env('重新汇报前15个种子');
'''

from __qbittorrent import Client

if __name__ == '__main__':
    qb        = Client()
    torrents  = qb.filter_torrents(filter='all', limit=15, sorted='added_on', reverse='True')
    info_hash = []
    for torrent in torrents:
        info_hash.append(torrent['hash'])
    qb.reannounce(info_hash)