# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
变量
export qb_url
export username
export password
export pushplus_token
'''

import re,requests,time,os,sys
from __notifier import SendNotify
from __logger import Logger
from __qbittorrent import Client

######################################
###############全局变量################

###############  参数  ################
try:
    qb_url         = os.environ['qb_url']
    username       = os.environ['username']
    password       = os.environ['password']
    pushplus_token = os.environ['pushplus']
except KeyError:
    print("请检查 qb_url username password pushplus 变量是否设置！")
    sys.exit(1)

#######################################
###############全局变量################



class Get_Free(object):
    def __init__(self, cookie:str, rss_url:str, log_file:str, log_level='info', verify=True, timeout=(5.05,20)) -> None:
        self.cookie       = cookie
        self.rss_url      = rss_url
        self.verify       = verify
        self.timeout      = timeout
        self.log_file     = log_file
        self.base_url     = re.match(r'http.*/', self.rss_url).group()
        self.log          = Logger(file_name=self.log_file, level=log_level, when='D', backCount=5, interval=1)

        self.rss_re_rule  = r'<title><!\[CDATA\[(.*)\]\]><\/title>[\s\S]*?<link>(.*\.php\?id=\d+)<\/link>[\s\S]*?<enclosure url="(.*)" length="(.*)" type.*[\s\S]*?<guid isPermaLink="false">(.*)<\/guid>[\s\S]*?<pubDate>(.*)<\/pubDate>'
        self.free_re_rule = r'<font class=\'(free|twoup|twouphalfdown|twoupfree)\''
        self.hr_re_rule   = r'<img class="hitandrun"'

        self.free_dict    = {
            'free'            : '免费',
            'twoup'           : '两倍上传',
            'twouphalfdown'   : '两倍上传%50下载',
            'twoupfree'       : '两倍上传免费',
            'thirtypercent'   : '%30下载',
            'pro_free'        : '免费',
            'pro_2up'         : '两倍上传',
            'pro_50pctdown2up': '两倍上传%50下载',
            'pro_free2up'     : '两倍上传免费',
            'pro_30pctdown'   : '%30下载'
        }
        self.host_referer = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'Referer': self.base_url,
            'Cookie': self.cookie
        }
        
        self.qbittorrent = Client(qb_url, username, password)
        self.send_notify = SendNotify(pushplus_token)

        session = requests.Session()
        try:
            login   = session.post(self.base_url, verify=self.verify, timeout=self.timeout, headers=self.host_referer)
        except KeyError:
            self.log.warning("环境变量未设置！")
            sys.exit(1)
        if re.search('login.php', login.text):
            self.log.warning("登录已失效，请更新Cookie！")
            self.send_notify.pushplus('OB','登录已失效，请更新Cookie！')
            self._is_authenticated = False
            sys.exit(1)
        else:
            self.log.info('Cookie有效')
            self._is_authenticated = True
            self.session = session

    def _get(self, url, **kwargs):
        kwargs['verify']  = self.verify
        kwargs['timeout'] = self.timeout

        request = self.session.get(url, **kwargs)
        request.raise_for_status()
        request.encoding = 'utf_8'

        if re.search('login.php', request.text):
            self.log.warning("登录已失效，请更新Cookie！")
            self.send_notify.pushplus('OB','登录已失效，请更新Cookie！')
            self._is_authenticated = False
            sys.exit(1)
        else:
            data = request.text

        return data

    def get_free_torrents(self, temp_file, time_format='%a, %d %b %Y %H:%M:%S +0800', min_size=15, max_size=800, filter_free=1, filter_hr=1, filter_old=1, delay=1, allow_time=10, rss_nums=10, rss_time=3) -> list:
        free_list   = []
        detail_info = re.findall(self.rss_re_rule,self._get(self.rss_url))

        if os.path.isfile(temp_file):
            past_time = round(time.time() - os.path.getmtime(temp_file))
            self.log.info("文件存在，距上次运行已过 {} 秒".format(past_time))
            if past_time <= rss_time*60:
                self.log.info("使用正常模式\n")
                mode = 0
            else:
                self.log.info("时间过久，使用初始运行模式\n")
                mode = 1
        else:
            self.log.info("文件不存在，使用初始运行模式\n")
            mode = 1

        if mode:
            url_dl_list = []
            for l in detail_info:
                url_dl  = l[2].replace("amp;", "")
                url_dl_list.append(url_dl + '\n')
            url_dl_list.sort(key = lambda i:int(re.search(r'id=(\d+)', i).group(1)))
            with open(temp_file, "w+") as f:
                f.writelines(url_dl_list)
            self.log.info("已记录，退出\n")
            sys.exit(0)

        with open(temp_file) as f:
            dl_url_history = f.readlines()

        for info in detail_info:
            name          = info[0]
            detail_url    = info[1]
            hash_code     = info[4]
            download_url  = info[2].replace("amp;", "")
            gbyte         = self.qbittorrent.bytes_to_gbytes(info[3])
            pub_date      = self.qbittorrent.olddate_to_newdate(info[5], time_format)
            pub_seconds   = self.qbittorrent.date_to_timestamp(info[5], time_format)

            if download_url + '\n' in dl_url_history:
                self.log.info("跳过：{} - 原因：已添加 - 链接：{}".format(name,detail_url))
                continue

            dl_url_history.append(download_url + '\n')

            if filter_old:
                past_seconds = int(time.time()) - pub_seconds
                if pub_seconds >= allow_time*60:
                    self.log.info("跳过：{} - 原因：发布于 {}，{} 秒前，时间过久 - 链接：{}".format(name,pub_date,past_seconds,detail_url))
                    continue
                self.log.info("时间符合要求：{} - 发布于 {} - {} 秒前 - 链接：{}".format(name,pub_date,past_seconds,detail_url))

            req_detail_url  = self._get(detail_url)
            if re.search('未登录!', req_detail_url.text):
                self.log.warning("登录已失效，请更新Cookie！")
                self.send_notify.pushplus('站点登录失效！','登录已失效，请更新Cookie！')
                sys.exit(1)

            # 获取种子的促销指定状态，若非指定状态则退出本次循环
            if filter_free:
                free_info = re.search(self.free_re_rule, req_detail_url.text)
                if free_info == None:
                    self.log.info("跳过：{} - 原因：黑种或 %50 下载 - 链接：{}".format(name,detail_url))
                    continue
                self.log.info("促销符合要求：{} - 促销状态：{} - 链接：{}".format(name,self.free_dict[free_info.group(1)],detail_url))

            # 获取种子的 HR 状态，若为 HR 状态则退出本次循环
            if filter_hr:
                hr_info = re.search(self.hr_re_rule,req_detail_url.text)
                if hr_info != None:
                    self.log.info("跳过：{} - 原因：HR 种子 - 链接：{}".format(name,detail_url))
                    continue
                self.log.info("HR 符合要求：{} - 非 HR - 链接：{}".format(name,detail_url))

            # 判断种子大小是否满足筛选条件，若不满足则退出本次循环
            if max_size <= gbyte or gbyte <= min_size:
                self.log.info("跳过：{} - 原因：过大或过小({} GB) - 链接：{}".format(name,gbyte,detail_url))
                continue
            self.log.info("大小符合要求：{} - 大小：{} - 链接：{}".format(name,gbyte,detail_url))
            self.send_notify.pushplus("添加种子","名称：{}\n大小：{} GB\n详情页:{}\n".format(name,gbyte,detail_url))

            # 将符合条件的种子下载链接存入列表
            free_list.append(download_url)

            # 执行完延时 1 秒
            time.sleep(delay)
            self.log.info("延时 {} 秒".format(delay))

        dl_url_history.sort(key = lambda i:int(re.search(r'id=(\d+)', i).group(1)))

        if len(dl_url_history) > rss_nums:
            del_counts = len(dl_url_history) - rss_nums
            del dl_url_history[:del_counts]
            self.log.info("指定 {} 个记录，共有 {} 个，删除 {} 个".format(rss_nums,len(dl_url_history),del_counts))

        with open(temp_file, "w+") as f:
            f.writelines(dl_url_history)

        if len(free_list):
            self.log.info("本次运行满足条件的种子有 {} 个，下载链接：{}".format(len(free_list),free_list))
            return(free_list)
        else:
            self.log.info("没有符合条件的种子")
            self.send_notify.pushplus('开始RSS订阅','没有符合条件的种子')
            sys.exit(0)