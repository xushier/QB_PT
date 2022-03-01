# coding=utf-8
# Created By Xushier  QQ:1575659493

import re,requests,time,os,sys
from __notifier import Send_Notify
from __logger import Logger
from __shift import *

###############  参数  ################

rss_re_rule  = r'<title><!\[CDATA\[(.*)\]\]><\/title>[\s\S]*?<link>(.*\.php\?id=\d+)<\/link>[\s\S]*?<enclosure url="(.*)" length="(.*)" type.*[\s\S]*?<guid isPermaLink="false">(.*)<\/guid>[\s\S]*?<pubDate>(.*)<\/pubDate>'
free_re_rule = r'<font class=\'(free|twoup|twouphalfdown|twoupfree)\''

#######################################


class Get_Free(object):
    def __init__(self, cookie:str, rss_url:str, log_file:str) -> None:
        self.log_file     = log_file
        self.cookie       = cookie
        self.rss_url      = rss_url
        self.log_level    = 'info'
        self.verify       = True
        self.timeout      = (5.05,20)
        self.base_url     = re.match(r'http.*/', rss_url).group()
        self.send_notify  = Send_Notify()
        self.hr_re_rule   = r'<img class="hitandrun"'
        self.log          = Logger(file_name=self.log_file, level=self.log_level, when='D', backCount=5, interval=1)

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

        session_try = requests.Session()
        login = session_try.get(self.base_url, verify=self.verify, timeout=self.timeout, headers=self.host_referer)
        if re.search('login.php', login.text):
            self.log.warning("登录已失效，请更新Cookie！")
            self.send_notify.pushplus('登录失效！','登录已失效，请更新Cookie！')
            sys.exit(1)
        else:
            self.log.info('Cookie有效')
            self.session = session_try

    def get_free_torrents(self, temp_file, min_size=15, max_size=800, filter_free=True, filter_hr=True, filter_old=True, delay=1, allow_time=10, rss_nums=15, rss_time=3, time_format='%a, %d %b %Y %H:%M:%S +0800', rss_re_rule=rss_re_rule, free_re_rule=free_re_rule) -> list:
        free_list   = []
        notify_data = ""
        detail_info = re.findall(rss_re_rule,self.session.get(self.rss_url, headers=self.host_referer).text)
        if os.path.isfile(temp_file):
            past_time = round(time.time() - os.path.getmtime(temp_file))
            self.log.info("文件存在，距上次运行已过 {} 秒".format(past_time))
            if past_time <= rss_time*66:
                self.log.info("使用正常模式")
                mode = False
            else:
                self.log.info("时间过久，使用初始运行模式")
                mode = True
        else:
            self.log.info("文件不存在，使用初始运行模式")
            mode = True

        if mode:
            url_dl_list = []
            for l in detail_info:
                url_dl  = l[2].replace("amp;", "")
                url_dl_list.append(url_dl + '\n')
            url_dl_list.sort(key = lambda i:int(re.search(r'id=(\d+)', i).group(1)))
            with open(temp_file, "w+") as f:
                f.writelines(url_dl_list)
            self.log.info("已记录，退出")
            sys.exit(0)

        with open(temp_file) as f:
            dl_url_history = f.readlines()

        for info in detail_info:
            name          = info[0]
            detail_url    = info[1]
            hash_code     = info[4]
            download_url  = info[2].replace("amp;", "")
            gbytes        = bytes_to_gbytes(info[3])
            pub_date      = olddate_to_newdate(info[5], time_format)
            pub_seconds   = date_to_timestamp(info[5], time_format)

            if download_url + '\n' in dl_url_history:
                self.log.info("跳过：{} - 原因：已添加 - 链接：{}".format(name,detail_url))
                continue

            dl_url_history.append(download_url + '\n')

            if filter_old:
                past_seconds = int(time.time()) - pub_seconds
                if past_seconds >= allow_time*60:
                    self.log.info("跳过：{} - 原因：发布于 {}，{} 秒前，时间过久 - 链接：{}".format(name,pub_date,past_seconds,detail_url))
                    continue
                self.log.info("时间符合要求：{} - 发布于 {} - {} 秒前 - 链接：{}".format(name,pub_date,past_seconds,detail_url))

            req_detail_url  = self.session.get(detail_url, headers=self.host_referer)
            if re.search('未登录!', req_detail_url.text):
                self.log.warning("登录已失效，请更新Cookie！")
                self.send_notify.pushplus('站点登录失效！','登录已失效，请更新Cookie！')
                sys.exit(1)

            # 获取种子的促销指定状态，若非指定状态则退出本次循环
            if filter_free:
                free_info = re.search(free_re_rule, req_detail_url.text)
                if free_info == None:
                    self.log.info("跳过：{} - 原因：黑种或 %50 下载 - 链接：{}".format(name,detail_url))
                    continue
                free_status = self.free_dict[free_info.group(1)]
                self.log.info("促销符合要求：{} - 促销状态：{} - 链接：{}".format(name,free_status,detail_url))

            # 获取种子的 HR 状态，若为 HR 状态则退出本次循环
            if filter_hr:
                hr_info = re.search(self.hr_re_rule,req_detail_url.text)
                if hr_info != None:
                    self.log.info("跳过：{} - 原因：HR 种子 - 链接：{}".format(name,detail_url))
                    continue
                self.log.info("HR 符合要求：{} - 非 HR - 链接：{}".format(name,detail_url))

            # 判断种子大小是否满足筛选条件，若不满足则退出本次循环
            if max_size <= gbytes or gbytes <= min_size:
                self.log.info("跳过：{} - 原因：过大或过小({} GB) - 链接：{}".format(name,gbytes,detail_url))
                continue
            self.log.info("大小符合要求：{} - 大小：{} - 链接：{}".format(name,gbytes,detail_url))
            notify_data = notify_data + "名称：{}\n大小：{} GB\n状态：{}\n发布：{}\n链接：{}\n".format(name,gbytes,free_status,pub_date,detail_url)

            # 将符合条件的种子下载链接存入列表
            free_list.append(download_url)

            # 执行完延时 1 秒
            time.sleep(delay)
            self.log.info("延时 {} 秒".format(delay))

        dl_url_history.sort(key = lambda i:int(re.search(r'id=(\d+)', i).group(1)))

        if len(dl_url_history) > rss_nums:
            del_counts = len(dl_url_history) - rss_nums
            self.log.info("指定 {} 个记录，共有 {} 个，删除 {} 个".format(rss_nums,len(dl_url_history),del_counts))
            del dl_url_history[:del_counts]

        with open(temp_file, "w+") as f:
            f.writelines(dl_url_history)

        if len(free_list):
            self.log.info("本次运行满足条件的种子有 {} 个，下载链接：{}".format(len(free_list),free_list))
            self.send_notify.pushplus("添加种子", notify_data)
            return(free_list)
        else:
            self.log.info("没有符合条件的种子")
            sys.exit(0)
