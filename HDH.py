# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
定时
cron: 0 0/3 * * *
任务名称
new Env('获取 HDHome 指定种子');

变量
export hdhome_cookie=""
export hdhome_rssurl=""
export hdhome_limit=""  # 格式:最小-最大-上传速度 例: 15-800-50,即过滤 15GB 到 800GB 的免费非 HR 非老种,且添加到 QB 时设置上传限速为 50 MB/S
'''

from __get_free import Get_Free
import os,sys,re

site_name  = 'hdhome'

try:
    cookie = os.environ[site_name + '_cookie']
    url    = os.environ[site_name + '_rssurl']
    limit  = os.environ[site_name + '_limit']
except KeyError:
    print("请检查 {}_cookie {}_rssurl {}_limit 变量是否设置！".format(site_name,site_name,site_name))
    sys.exit(1)

if __name__ == '__main__':
    min_size = re.split('-', limit)[0]
    max_size = re.split('-', limit)[1]
    up_limit = re.split('-', limit)[2]
    get_free = Get_Free(cookie, url, site_name + '_run.log')
    torrents = get_free.get_free_torrents(site_name + '_temp.log', min_size=min_size, max_size=max_size)
    get_free.qbittorrent.add_torrents_from_link(torrents, up_limit - 1, '/downloads/' + site_name, site_name)