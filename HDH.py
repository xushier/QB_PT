# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
定时
cron: 30 0/3 * * * *
任务名称
new Env('HDHome 刷流');

变量
export HDHOME_COOKIE=""
export HDHOME_USERNAME=""
export HDHOME_PASSWORD=""
'''
import sys,re,os
from __qbittorrent import Client
from __get_free import Get_Free

site = 'HDHOME'
site_lowwer = site.lower()

config = {
    site + '_COOKIE': '',
    site + '_RSS_URL': '',
    site + '_CONFIG': '',

    site + '_SAVE_PATH': '/downloads/' + site_lowwer,
    site + '_RUN_LOG': site_lowwer + '_run.log',
    site + '_TEMP_LOG': site_lowwer + '_temp.log',
}

for n in config:
    if os.getenv(n):
        v = os.getenv(n)
        config[n] = v

if not config[site + '_COOKIE']:
    print("请检查 HDHOME_COOKIE 变量是否设置！")
    sys.exit(1)
if not config[site + '_RSS_URL']:
    print("请检查 HDHOME_RSS_URL 变量是否设置！")
    sys.exit(1)
if not config[site + '_COOKIE']:
    print("请检查 HDHOME_CONFIG 变量是否设置！")
    sys.exit(1)

site_config = re.split('-', config[site + '_CONFIG'])

category  = site.lower()
min_size  = int(site_config[0])
max_size  = int(site_config[1])
up_limit  = int(site_config[2])
save_path = config[site + '_SAVE_PATH']
run_log   = config[site + '_RUN_LOG']
temp_log  = config[site + '_TEMP_LOG']
cookie    = config[site + '_COOKIE']
rss_url   = config[site + '_RSS_URL']


h = Get_Free(cookie, rss_url, run_log).get_free_torrents(temp_log, min_size=min_size, max_size=max_size)
s = Client()
s.add_torrents_from_link(h, up_limit, save_path, category)
