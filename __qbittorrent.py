# coding=utf-8
# Created By Xushier  QQ:1575659493

'''
变量
export QB_URL=""
export USERNAME=""
export PASSWORD=""
'''
from __shift import *
from __logger import Logger
from __notifier import Send_Notify
import requests,json,time,sys,os

############### QB参数################

qb_config = {
    'QB_URL': '',
    'USERNAME': '',
    'PASSWORD': '',
    'FILTER_FILTER': 'all',
    'FILTER_SORT': 'added_on',
    'FILTER_LIMIT': 50,
    'FILTER_REVERSE': 'False',
    'FILTER_TIMES': 3,
    'DELAY': 5,
    'MAX_DELETE': 3,
    'MIN_HOUR': 2,
    'MAX_HOUR': 5,
}

for n in qb_config:
    if os.getenv(n):
        v = os.getenv(n)
        qb_config[n] = v

###############其他参数################

filter_filter  = qb_config['FILTER_FILTER']
filter_limit   = int(qb_config['FILTER_LIMIT'])
filter_sort    = qb_config['FILTER_SORT']
filter_reverse = qb_config['FILTER_REVERSE']
filter_times   = int(qb_config['FILTER_TIMES'])
delay          = int(qb_config['DELAY'])
max_delete     = int(qb_config['MAX_DELETE'])
min_hour       = int(qb_config['MIN_HOUR'])
max_hour       = int(qb_config['MAX_HOUR'])

#######################################

class Client(object):
    """class to interact with qBittorrent WEB API"""
    def __init__(self, log_file_name='qb_run.log', verify=False, timeout=(3.05,20)):
        """
        Initialize the client

        :param url: Base URL of the qBittorrent WEB API
        :param verify: Boolean to specify if SSL verification should be done.
                       Defaults to True. 
        :param timeout: How many seconds to wait for the server to send data
                        before giving up, as a float, or a
                        `(connect timeout, read timeout)` tuple.
                       Defaults to None.
        """

        self.send_notify = Send_Notify()

        size = os.path.getsize(log_file_name)
        if os.path.isfile(log_file_name):
            size = os.path.getsize(log_file_name)
            if size > 100000:
                print("QB 运行日志大小超过 100K，清空")
                with open(log_file_name, "w+") as f:
                    f.writelines('')
        self.log         = Logger(file_name=log_file_name, level='info', when='D', backCount=5, interval=1)

        if not qb_config.get("QB_URL"):
            self.log.warning("qbittorrent 地址未设置!!\n取消操作")
            sys.exit(1)
        if not qb_config.get("USERNAME"):
            self.log.warning("qbittorrent 用户名未设置!!\n取消操作")
            sys.exit(1)
        if not qb_config.get("PASSWORD"):
            self.log.warning("qbittorrent 密码未设置!!\n取消操作")
            sys.exit(1)

        url = qb_config.get("QB_URL")
        if not url.endswith('/'):
            url += '/'
        self.url      = url + 'api/v2/'
        self.verify   = verify
        self.timeout  = timeout
        self.username = qb_config.get("USERNAME")
        self.password = qb_config.get("PASSWORD")

        try:
            self.log.info("连接 qbittorrent······")
            session = requests.session()
            login = session.post(self.url + 'auth/login',
                                    data={'username': self.username,
                                            'password': self.password},
                                    verify=self.verify, timeout=self.timeout)
            if login.text == 'Ok.':
                self.log.info("连接成功")
                self.session = session
            elif login.text == 'Fails.':
                self.log.warning("QB 用户名或密码错误!")
                self.send_notify("QB","用户名或密码错误!")
                sys.exit(1)
            elif login.status_code == 403:
                self.log.error("登录认证失败次数过多，IP 已被封禁！请更换 IP 或重启 QB!")
                self.send_notify("QB 登录失败!","登录认证失败次数过多，IP 已被封禁！请更换 IP 或重启 QB!")
                sys.exit(1)
            else:
                self.log.error("QB 未知错误！")
                self.send_notify("QB 未知错误!","未知错误")
                sys.exit(1)
        except Exception:
            self.log.error("QB 连接超时！")
            self.send_notify("QB","连接超时！")
            sys.exit(1)

    def _get(self, endpoint, **kwargs):
        """
        Method to perform GET request on the API.

        :param endpoint: Endpoint of the API.
        :param kwargs: Other keyword arguments for requests.

        :return: Response of the GET request.
        """
        return self._request(endpoint, 'get', **kwargs)

    def _post(self, endpoint, data, **kwargs):
        """
        Method to perform POST request on the API.

        :param endpoint: Endpoint of the API.
        :param data: POST DATA for the request.
        :param kwargs: Other keyword arguments for requests.

        :return: Response of the POST request.
        """
        return self._request(endpoint, 'post', data, **kwargs)

    def _request(self, endpoint, method, data=None, **kwargs):
        """
        Method to hanle both GET and POST requests.

        :param endpoint: Endpoint of the API.
        :param method: Method of HTTP request.
        :param data: POST DATA for the request.
        :param kwargs: Other keyword arguments.

        :return: Response for the request.
        """
        final_url = self.url + endpoint

        kwargs['verify']  = self.verify
        kwargs['timeout'] = self.timeout
        if method == 'get':
            request = self.session.get(final_url, **kwargs)
        else:
            request = self.session.post(final_url, data, **kwargs)

        request.raise_for_status()
        request.encoding = 'utf_8'

        if len(request.text) == 0:
            data = json.loads('{}')
        else:
            try:
                data = json.loads(request.text)
            except ValueError:
                data = request.text

        return data

    def get_torrent_info(self, infohash):
        """
        Get details of the torrent.

        :param infohash: INFO HASH of the torrent.
        """
        return self._get('torrents/properties?hash=' + infohash.lower())

    @property
    def global_transfer_info(self):
        """
        :return: dict{} of the global transfer info of qBittorrent.

        """
        return self._get('transfer/info')

    def sync_main_data(self, rid=0):
        """
        Sync the torrents main data by supplied LAST RESPONSE ID.
        Read more @ https://git.io/fxgB8

        :param rid: Response ID of last request.
        """
        return self._get('sync/maindata', params={'rid': rid})

    def filter_torrents(self, **filters):
        """
        Returns a list of torrents matching the supplied filters.

        :param filter: Current status of the torrents.
        :param category: Fetch all torrents with the supplied label.
        :param sort: Sort torrents by.
        :param reverse: Enable reverse sorting.
        :param limit: Limit the number of torrents returned.
        :param offset: Set offset (if less than 0, offset from end).

        :return: list() of torrent with matching filter.
        For example: qb.torrents(filter='downloading', sort='ratio').
        """
        params = {}
        for name, value in filters.items():
            # make sure that old 'status' argument still works
            name = 'filter' if name == 'status' else name
            params[name] = value

        return self._get('torrents/info', params=params)

    @staticmethod
    def _process_infohash_list(infohash_list):
        """
        Method to convert the infohash_list to qBittorrent API friendly values.

        :param infohash_list: List of infohash.
        """
        if isinstance(infohash_list, list):
            data = {'hashes': '|'.join([h.lower() for h in infohash_list])}
        else:
            data = {'hashes': infohash_list.lower()}
        return data

    def add_torrents_from_link(self, link, uplimit:int, savepath:str, category:str, dllimit=50, paused='false'):
        """
        Download torrent using a link.

        :param link: URL Link or list of.
        :param savepath: Path to download the torrent.
        :param category: Label or Category of the torrent(s).

        :return: Empty JSON data.
        """
        if isinstance(link, list): 
            hashes = {"urls": '\n'.join(link), "upLimit": mbytes_to_bytes(uplimit, return_type='str'), "dlLimit": mbytes_to_bytes(dllimit, return_type='str'), "savepath": savepath, "category": category, "paused": paused}
        else:
            hashes = {"urls": link, "upLimit": mbytes_to_bytes(uplimit, return_type='str'), "dlLimit": mbytes_to_bytes(dllimit, return_type='str'), "savepath": savepath, "category": category, "paused": paused}
        connections = self.sync_main_data()['server_state']['total_peer_connections']
        dl_account  = self.get_torrents_amount()[0]
        if connections > 1000 and dl_account > 9 :
            self.log.warning("QB 总连接用户数为 {}，超过 1000，下载中的种子数 {}，不添加种子".format(connections,dl_account))
            self.send_notify("连接数过多，不添加种子", "QB 总连接用户数为 {}，下载中的种子数 {}".format(connections,dl_account))
            return
        add_torrents = self.session.post(self.url + 'torrents/add', data=hashes)
        if add_torrents.status_code == 200:
            self.log.info("种子添加成功！")
            return add_torrents.text

    def reannounce(self, infohash_list):
        """
        Recheck all torrents.

        :param infohash_list: Single or list() of infohashes; pass 'all' for all torrents.
        """
        data = self._process_infohash_list(infohash_list)
        reannounce_torrents = self.session.post(self.url + 'torrents/reannounce', data=data)
        if reannounce_torrents.status_code == 200:
            self.log.info("种子重新汇报成功！")
            return reannounce_torrents.text

    def delete(self, infohash_list, delete_files=True):
        """
        Delete torrents.

        :param infohash_list: Single or list() of infohashes.
        :param delete_files: Whether to delete files along with torrent.
        """
        data = self._process_infohash_list(infohash_list)
        data['deleteFiles'] = json.dumps(delete_files)
        delete_torrents = self.session.post(self.url + 'torrents/delete', data=data)
        if delete_torrents.status_code == 200:
            self.log.info("种子删除成功！")
            return delete_torrents.text
    
    @property
    def global_transfer_info(self):
        """
        :return: dict{} of the global transfer info of qBittorrent.

        """
        return self._get('transfer/info')

    def get_torrents_amount(self):
        return len(self.filter_torrents(filter='downloading')),len(self.filter_torrents(filter='all'))

    def get_satisfied_torrents(self,limit=filter_limit,filter=filter_filter,sort=filter_sort,reverse=filter_reverse,delay=delay,filter_times=filter_times,max_delete=max_delete,min_hour=min_hour,max_hour=max_hour) -> list:
        dl_account    = self.get_torrents_amount()[0]
        all_account   = self.get_torrents_amount()[1]
        free_space    = bytes_to_gbytes(self.sync_main_data()['server_state']['free_space_on_disk'])
        transfer_info = self.global_transfer_info
        dl_gb_data    = bytes_to_gbytes(transfer_info['dl_info_data'])
        up_gb_data    = bytes_to_gbytes(transfer_info['up_info_data'])
        dl_gb_speed   = transfer_info['dl_info_speed']
        up_gb_speed   = transfer_info['up_info_speed']
        speed_ratio   = round(dl_gb_speed/up_gb_speed,2)
        time_now      = time.localtime().tm_hour

        if max_hour <= time_now or time_now < min_hour:
            self.log.info("当前时间：{}点，可以删种".format(time_now))
            notify_data  = "当前时间：{}点\n".format(time_now)
        else:
            self.log.info("当前时间：{}点，无需删种".format(time_now))
            sys.exit(0)

        if free_space >= 500 and speed_ratio < 3 and all_account < 30 and dl_account < 10:
            self.log.info("可用空间：{} GB，速度比：{}，种子数量：{}，下载数量：{}，无需删种".format(free_space,speed_ratio,all_account,dl_account))
            sys.exit(0)
        else:
            self.log.info("可用空间：{} GB，速度比：{}，种子数量：{}，下载数量：{}，满足删种条件，可以删种".format(free_space,speed_ratio,all_account,dl_account))
            notify_data = notify_data + "可用空间：{} GB\n速度比率：{}\n种子数量：{}\n下载数量：{}\n满足删种条件，可以删种\n\n".format(free_space,speed_ratio,all_account,dl_account)

        names = locals()
        for i in range(1, filter_times+1):
            names['hashes' + str(i)] = set()

            torinfo = self.filter_torrents(filter=filter, limit=limit, sort=sort, reverse=reverse)

            for tr in torinfo:
                added_on, completion_on    = timestamp_to_date(tr['added_on']), timestamp_to_date(tr['completion_on'])
                name, hashcode, category   = tr['name'], tr['hash'], tr['category']
                ratio, size, state         = round(tr['ratio'],2), bytes_to_gbytes(tr['size']), tr['state']
                progress                   = int(tr['progress']*100)
                num_leechs, num_seeds      = tr['num_leechs'], tr['num_seeds']
                dlspeed, upspeed, uploaded = tr['dlspeed'], tr['upspeed'], bytes_to_gbytes(tr['uploaded'])
                num_incomplete, time_active= tr['num_incomplete'], tr['time_active']
                # st = int((time.time() - tr['completion_on']) / 3600)
                # if category == 'chdbits' or category == None:
                #     if st < 120:
                #         continue
                if state != 'downloading':
                    seed_time = round(((time.time() - tr['completion_on']) / 3600),2)
                if state == 'stalledUP' and ( ratio >= 2 or seed_time > 24 ) and num_leechs < 5:
                    self.log.info("删除确认第{}次 - 空闲中 - {} - 大小：{} - 已上传：{} GB - 分享率：{} - 完成于：{} - ({})".format(i,category,size,uploaded,ratio,completion_on,name))
                    names['hashes' + str(i)].add(hashcode)
                if state == 'uploading' and ( ratio >= 2 or seed_time > 24 ) and upspeed < 600*1024 and num_leechs < 5:
                    self.log.info("删除确认第{}次 - 上传中 - {} - 大小：{} - 已上传：{} GB - 分享率：{} - 完成于：{} - ({})".format(i,category,size,uploaded,ratio,completion_on,name))
                    names['hashes' + str(i)].add(hashcode)
                # if state == 'downloading' and dlspeed > 20*1048576 and dlspeed / upspeed >= 3 and progress > 15:
                if state == 'downloading' and ratio < 0.12 and dlspeed >= ( upspeed*5 ) and progress > 15 and time_active > 500:
                    self.log.info("删除确认第{}次 - 下载中 - {} - 大小：{} - 已上传：{} GB - 分享率：{} - ({})".format(i,category,size,uploaded,ratio,name))
                    names['hashes' + str(i)].add(hashcode)
                if state == 'downloading' and ratio < 0.12 and dlspeed >= ( upspeed*5 ) and num_incomplete < 20 and time_active > 500:
                    self.log.info("删除确认第{}次 - 下载中 - {} - 大小：{} - 已上传：{} GB - 分享率：{} - ({})".format(i,category,size,uploaded,ratio,name))
                    names['hashes' + str(i)].add(hashcode)
                if state == 'stalledDL' and ratio < 0.12 and dlspeed >= ( upspeed*5 ) and num_incomplete < 20 and time_active > 500:
                    self.log.info("删除确认第{}次 - 等待中 - {} - 大小：{} - 已上传：{} GB - 分享率：{} - 完成于：{} - ({})".format(i,category,size,uploaded,ratio,completion_on,name))
                    names['hashes' + str(i)].add(hashcode)
            time.sleep(delay)

        final_hashes = names['hashes' + str(1)]
        for n in range(2, filter_times+1):
            final_hashes = final_hashes & names['hashes' + str(n)]
        if len(final_hashes):
            final_hashes = list(final_hashes)
            if len(final_hashes) > max_delete:
                del final_hashes[max_delete:]
            for t in final_hashes:
                h           = self.get_torrent_info(t)
                t_uploaded, t_ratio = bytes_to_gbytes(h['total_uploaded']), round(h['share_ratio'], 2)
                t_size      = bytes_to_gbytes(h['total_size'])
                t_seedtime  = round(h['seeding_time'] / 3600, 2)
                t_addon     = timestamp_to_date(h['addition_date'])
                t_compon    = timestamp_to_date(h['completion_date'])
                notify_data = notify_data + "删除种子\n添加于：{}\n完成于：{}\n大小：{} GB - 已上传：{} GB\n分享率：{} - 做种时间：{} 小时\n\n".format(t_addon,t_compon,t_size,t_uploaded,t_ratio,t_seedtime)
                time.sleep(delay)
            self.send_notify.wechat("青龙刷流脚本\n本次删除 {} 个种子".format(len(final_hashes)), notify_data)
            self.log.info(final_hashes)
            return final_hashes
        else:
            self.log.info("没有符合条件的种子，无需删除")
            sys.exit(0)