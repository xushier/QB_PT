# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
定时
cron: 30 0/3 * * * *
任务名称
new Env('SoulVoice 刷流');

变量
export SOULVOICE_COOKIE=""
export SOULVOICE_RSS_URL=""
export SOULVOICE_CONFIG=""
'''
import sys,re,os
from __qbittorrent import Client
from __get_free import Get_Free

site = 'SOULVOICE'
site_lower = site.lower()

config = {
    site + '_COOKIE': '',
    site + '_RSS_URL': '',
    site + '_CONFIG': '',

    site + '_SAVE_PATH': '/downloads/' + site_lower,
    site + '_RUN_LOG': site_lower + '_run.log',
    site + '_TEMP_LOG': site_lower + '_temp.log',
}

for n in config:
    if os.getenv(n):
        v = os.getenv(n)
        config[n] = v

if not config[site + '_COOKIE']:
    print("请检查 SOULVOICE_COOKIE 变量是否设置！")
    sys.exit(1)
if not config[site + '_RSS_URL']:
    print("请检查 SOULVOICE_RSS_URL 变量是否设置！")
    sys.exit(1)
if not config[site + '_COOKIE']:
    print("请检查 SOULVOICE_CONFIG 变量是否设置！")
    sys.exit(1)

site_config = re.split('-', config[site + '_CONFIG'])
category    = site_lower
min_size    = int(site_config[0])
max_size    = int(site_config[1])
up_limit    = int(site_config[2])
save_path   = config[site + '_SAVE_PATH']
run_log     = config[site + '_RUN_LOG']
temp_log    = config[site + '_TEMP_LOG']
cookie      = config[site + '_COOKIE']
rss_url     = config[site + '_RSS_URL']

free_torrents = Get_Free(cookie, rss_url, run_log).get_free_torrents(temp_log, category, min_size=min_size, max_size=max_size)
qb = Client()
qb.add_torrents_from_link(free_torrents, up_limit, save_path, category)
