# coding=utf-8
# Created By Xushier  QQ:1575659493
'''
cron: 0 * * * *
new Env('自动删除QB种子');
export QBENV="第1个cookie&第2个cookie"
'''



# 引入要使用的库
import requests,json,time,re,sys,logging
from logging import handlers

######################################
###############全局变量################

#----------------过滤-----------------#
# 过滤返回种子的数量、排序依据、下载状态和升降序
filterNum      = 5
filterSort     = 'added_on'
filterFilter   = 'all'
filterReverse  = 'false'
# 过滤要删除的种子时，每隔 (Delay) 秒请求一次，共请求 (ReqTimes) 次，每次都满足的情况下才删除
Delay    = 5
ReqTimes = 3


#----------------变量-----------------#
# QB 的连接协议、地址、端口、用户名和密码
QBProtocol  = 'http'
QBAddress   = 'xushier.cf'
QBPort      = '8080'
UserName    = 'xushier'
PassWord    = 'xushier666'
# PushPlus 推送的 Token
PushPlus	= '08dc2406fc484d789406b2f4aa794abf'
# 添加种子的重试次数
retryTimes  = 3

#----------------其他-----------------#
# 相应 API 接口的 URL 链接
baseURL       = QBProtocol + '://' + QBAddress + ':' + QBPort
delURL        = baseURL + '/api/v2/torrents/delete'
resumeURL     = baseURL + '/api/v2/torrents/resume'
uplimitURL    = baseURL + '/api/v2/torrents/setUploadLimit'
infoURL       = baseURL + '/api/v2/torrents/info'
addURL        = baseURL + '/api/v2/torrents/add'
categoryURL   = baseURL + '/api/v2/torrents/setCategory'
createCAURL   = baseURL + '/api/v2/torrents/createCategory'
reannounceURL = baseURL + '/api/v2/torrents/reannounce'
maindataURL   = baseURL + '/api/v2/sync/maindata'
transferURL   = baseURL + '/api/v2/transfer/info'
# 日志记录


class Logger(object):
	def __init__(self,file_name,level='debug',backCount=5,when='D',interval=1):
		logger = logging.getLogger(file_name)  # 先实例化一个logger对象，先创建一个办公室
		logger.setLevel(self.__get_level(level))  # 设置日志的级别的人
		cl = logging.StreamHandler()  # 负责往控制台输出的人
		bl = handlers.TimedRotatingFileHandler(filename=file_name, when=when, interval=interval, backupCount=backCount, encoding='utf-8')
		fmt = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
		cl.setFormatter(fmt)  # 设置控制台输出的日志格式
		bl.setFormatter(fmt)  # 设置文件里面写入的日志格式
		logger.addHandler(cl)
		logger.addHandler(bl)
		self.debug = logger.debug
		self.warning = logger.warning
		self.info = logger.info
		self.error = logger.error


	def __get_level(self,str):
		level = {
			'debug':logging.DEBUG,
			'info':logging.INFO,
			'warn':logging.WARNING,
			'error':logging.ERROR
		}
		str = str.lower()
		return level.get(str)


log           = Logger(file_name='run.log', level='info', when='D', backCount=5, interval=1)

#################结束##################
#######################################




#######################################
# 通过PushPlus通知
# 必传参数：标题、内容
#
#Get
def sendNotify(title:str,content:str):
	token   = PushPlus
	title   = title
	content = content
	headers = {'Content-Type':'application/json'}
	url     = 'http://www.pushplus.plus/send?token='+token+'&title='+title+'&content='+content
	notify = requests.get(url,headers=headers)
	if notify.status_code == 200:
		log.info('通知发送成功！')
	else:
		log.error('通知发送失败！')

#Post
# def sendNotify(title,content):
# 	token   = '你的token' #在pushpush网站中可以找到
# 	title   = '标题' #改成你要的标题内容
# 	content ='内容' #改成你要的正文内容
# 	url     = 'http://www.pushplus.plus/send'
# 	data    = {
#     	"token":token,
#     	"title":title,
#     	"content":content
# 	}
# 	body    =json.dumps(data).encode(encoding='utf-8')
# 	headers = {'Content-Type':'application/json'}
# 	requests.post(url,data=body,headers=headers)

######################################




######################################
# Cookie 会话保持

cookie_Session = requests.session()
login_URL      = baseURL + '/api/v2/auth/login'
auth_Data      = {"username": UserName,"password": PassWord}

try:
	cookie_Get     = cookie_Session.post(login_URL,auth_Data,timeout=(5.05,30))
	if cookie_Get.text == 'Fails.':
		log.error("QB 用户名或密码错误!")
		sendNotify("QB","用户名或密码错误!")
		sys.exit(1)
	if cookie_Get.status_code == 403:
		log.error("登录认证失败次数过多，IP 已被封禁！请更换 IP 或重启 QB!")
		sendNotify("QB 登录失败!","登录认证失败次数过多，IP 已被封禁！请更换 IP 或重启 QB!")
		sys.exit(1)
except Exception:
	log.error("QB 连接超时！")
	sendNotify("QB","连接超时！")
	sys.exit(1)

######################################




######################################
# 请求 QB 删除指定种子
# 必传参数：种子哈希列表
# 选传参数：删除文件开关
# 返回删除结果
# 
# Get
def deleteTorrents(hashes:list,delFiles='true'):
	join     = "|"
	joinHash = join.join(hashes)
	url      = delURL + '?hashes=' + joinHash + '&deleteFiles=' + delFiles
	del_Post = cookie_Session.get(url)
	if del_Post.status_code == 200:
		log.info("种子已删除！")

# Post
# def deleteTorrents(hashes:list,delFiles='true'):
# 	join     = "|"
# 	joinHash = join.join(hashes)
# 	data = {"hashes": joinHash,"deleteFiles": delFiles}
# 	del_Post = cookie_Session.post(delURL,data)
# 	if del_Post.status_code == 200:
# 		print('已删除')

######################################




######################################
# 重新汇报种子
# 必传参数：种子哈希列表
# 
# Get
def reannounceTorrents(hashes:list):
	join     = "|"
	joinHash = join.join(hashes)
	url      = reannounceURL + '?hashes=' + joinHash
	annc_Post = cookie_Session.get(url)
	if annc_Post.status_code == 200:
		log.info("种子已重新汇报")

# Post
# def reannounceTorrents(hashes:list):
# 	join     = "|"
# 	joinHash = join.join(hashes)
# 	data = {"hashes": joinHash}
# 	annc_Post = cookie_Session.post(reannounceURL,data)
# 	if annc_Post.status_code == 200:
# 		print('已重新汇报')

######################################




######################################
# 向 QB 添加种子
# 必传参数：种子下载链接列表
# 选传参数：保存路径、分类、添加后是否暂停
# 返回添加结果
# 
def addTorrents(urls:list,uplimit:int,savepath:str,category:str,dllimit=60,paused='false'):
	sep      = "\n"
	urls     = sep.join(urls)
	data     = {"urls": urls,"upLimit": str(uplimit*1048576),"dlLimit": str(dllimit*1048576),"savepath": savepath,"category": category,"paused": paused}
	for i in range(retryTimes):
		add_Post = cookie_Session.post(addURL,data)
		time.sleep(1)
		if add_Post.status_code == 200:
			break
		time.sleep(1)
	if add_Post.status_code != 200:
		log.error("响应码 {}，网络或网站异常，程序退出！".format(add_Post.status_code))
		sendNotify("种子添加失败","响应码 {}，网络或网站异常，程序退出！".format(add_Post.status_code))
		sys.exit(1)
	log.info("种子已成功添加！")

######################################




######################################
# 日期和时间戳互转
# 
# 将任意格式日期转换为结构体时间
# StructTime  = time.strptime(DateTime, "%a, %d %b %Y %H:%M:%S +0800")
# 
# 将结构体时间转换为指定格式日期
# DateTime     = time.strftime("%Y-%m-%d %H:%M:%S", StructTime)
# 
# 将结构体时间转换为整数时间戳
# StampTime  = int(time.mktime(StructTime))
# 
# 将时间戳转换为结构体时间
# StructTime = time.localtime(StampTime)
# 
# 
def StampToDate(timestamp:int,outputformat='%Y-%m-%d %H:%M:%S') -> str:
	DateTime = time.strftime(outputformat, time.localtime(timestamp))
	return DateTime

def DateToStampAndDate(datetime:str,inputformat='%Y-%m-%d %H:%M:%S',outputformat='%Y-%m-%d %H:%M:%S'):
	StructTime = time.strptime(datetime, inputformat)
	StampTime  = int(time.mktime(StructTime))
	if inputformat != outputformat:
		DateTime = time.strftime(outputformat, StructTime)
	DateTime   = datetime
	return StampTime,DateTime

######################################




######################################
# 字符串类型字节转换为整型MB和GB
# 整型MB和GB转换为整型字节
# 
def StrBytesToMGB(bytes:str) -> int:
	GB = round(int(bytes)/1073741824,2)
	MB = round(int(bytes)/1048576,2)
	return GB,MB

def MGBToBytes(MB,GB) -> int:
	if MB == '' and GB != '':
		Bytes = GB*1073741824
	if MB != '' and GB == '':
		Bytes = MB*1048576
	return Bytes

######################################




def GetGlobalInfo():
	gbinfo        = cookie_Session.post(maindataURL).json()
	free_space    = StrBytesToMGB(gbinfo['server_state']['free_space_on_disk'])[0]
	dl_info_data  = StrBytesToMGB(gbinfo['server_state']['dl_info_data'])[0]
	up_info_data  = StrBytesToMGB(gbinfo['server_state']['up_info_data'])[0]
	dl_info_speed = StrBytesToMGB(gbinfo['server_state']['dl_info_speed'])[1]
	up_info_speed = StrBytesToMGB(gbinfo['server_state']['up_info_speed'])[1]




#######################################
# 从 QB 过滤种子
# 必传参数：类型、分类、数量
# 选传参数：排序类型、排序升降序
# 返回满足条件种子的哈希值列表
# 
def GetSatisfiedTorrents(filterNum=filterNum,filterFilter=filterFilter,filterSort=filterSort,filterReverse=filterReverse,Delay=Delay,ReqTimes=ReqTimes) -> list:
	gbinfo      = cookie_Session.post(maindataURL).json()
	all_Num     = len(cookie_Session.get(infoURL + '?filter=' + 'all').json())
	dl_Num      = len(cookie_Session.get(infoURL + '?filter=' + 'downloading').json())
	free_space  = StrBytesToMGB(gbinfo['server_state']['free_space_on_disk'])[0]
	dl_gb_data  = StrBytesToMGB(gbinfo['server_state']['dl_info_data'])[0]
	up_gb_data  = StrBytesToMGB(gbinfo['server_state']['up_info_data'])[0]
	dl_gb_speed = gbinfo['server_state']['dl_info_speed']
	up_gb_speed = gbinfo['server_state']['up_info_speed']
	speedRatio  = round(dl_gb_speed/up_gb_speed,2)
	timeNow     = time.localtime().tm_hour

	if 9 <= timeNow <= 23 :
		log.info("当前时间：{}点，可以删种".format(timeNow))
		NotifyData  = "当前时间：{}点\n".format(timeNow)
	else:
		log.info("当前时间：{}点，无需删种".format(timeNow))
		sys.exit(0)

	if free_space >= 500 and speedRatio < 3 and all_Num < 40 and dl_Num < 15:
		log.info("可用空间：{} GB，速度比：{}，种子数量：{}，下载数量：{}，无需删种".format(free_space,speedRatio,all_Num,dl_Num))
		sys.exit(0)
	else:
		log.info("可用空间：{} GB，速度比：{}，种子数量：{}，下载数量：{}，满足删种条件，可以删种".format(free_space,speedRatio,all_Num,dl_Num))
		NotifyData = NotifyData + "可用空间：{} GB\n速度比率：{}\n种子数量：{}\n下载数量：{}\n满足删种条件，可以删种\n\n".format(free_space,speedRatio,all_Num,dl_Num)

	names = locals()
	for i in range(1,ReqTimes+1):
		names['hashes' + str(i)] = set()

		data = {"filter": filterFilter,"limit": str(filterNum),"sort": filterSort,"reverse": filterReverse}
		torinfo = cookie_Session.post(infoURL,data).json()

		for tr in torinfo:
			added_on,completion_on,completion_on_date = StampToDate(tr['added_on']),tr['completion_on'],StampToDate(tr['completion_on'])
			hashcode,name,category,num_leechs         = tr['hash'],tr['name'],tr['category'],tr['num_leechs']
			num_complete,num_incomplete,num_seeds     = tr['num_complete'],tr['num_incomplete'],tr['num_seeds']
			progress,ratio,savepath,size,state        = int(tr['progress'])*100,round(tr['ratio'],2),tr['save_path'],StrBytesToMGB(tr['size'])[0],tr['state']
			dl_limit,dlspeed,downloaded               = StrBytesToMGB(tr['dl_limit'])[1],tr['dlspeed'],StrBytesToMGB(tr['downloaded'])[0]
			up_limit,upspeed,uploaded                 = StrBytesToMGB(tr['up_limit'])[1],tr['upspeed'],StrBytesToMGB(tr['uploaded'])[0]

			if state == 'stalledUP' and ( ratio >= 1 or time.time() - completion_on > 24*3600 ) and num_leechs < 5 :
				log.info("删除确认第{}次 - 空闲中 - {} - 已上传：{} GB - 分享率：{} - 完成于：{} - ({})".format(i,category,uploaded,ratio,completion_on_date,name))
				names['hashes' + str(i)].add(hashcode)
				NotifyData = NotifyData + "删除确认第{}次 - 空闲中 - {} - 已上传：{} GB - 分享率：{} - 完成于：{} - ({})\n".format(i,category,uploaded,ratio,completion_on_date,name)
			if state == 'uploading' and ( ratio >= 1 or time.time() - completion_on > 24*3600 ) and upspeed < 600*1024 :
				log.info("删除确认第{}次 - 上传中 - {} - 已上传：{} GB - 分享率：{} - 完成于：{} - ({})".format(i,category,uploaded,ratio,completion_on_date,name))
				names['hashes' + str(i)].add(hashcode)
				NotifyData = NotifyData + "删除确认第{}次 - 上传中 - {} - 已上传：{} GB - 分享率：{} - 完成于：{} - ({})\n".format(i,category,uploaded,ratio,completion_on_date,name)
			if state == 'downloading' and dlspeed > 20*1048576 and dlspeed/upspeed >= 3 and progress > 0.15 :
				log.info("删除确认第{}次 - 下载中 - {} - 已上传：{} GB - 分享率：{} - 完成于：{} - ({})".format(i,category,uploaded,ratio,completion_on_date,name))
				# log.info("添加于：{}\n完成于：{}\n下载速度限制：{}\n下载速度：{}\n已下载：{}\n哈希值：{}\n名称：{}\n分类：{}\n做种人数：{}\n下载人数：{}\n已连接做种人数：{}\n已连接下载人数：{}\n下载进度：{}\n分享率：{}\n保存路径：{}\n大小：{}\n状态：{}\n上传速度限制：{}\n已上传：{}\n上传速度：{}\n".format(added_on,completion_on_date,dl_limit,dlspeed,downloaded,hashcode,name,category,num_complete,num_incomplete,num_seeds,num_leechs,progress,ratio,savepath,size,state,up_limit,uploaded,upspeed))
				names['hashes' + str(i)].add(hashcode)
				NotifyData = NotifyData + "删除确认第{}次 - 下载中 - {} - 已上传：{} GB - 分享率：{} - 完成于：{} - ({})\n".format(i,category,uploaded,ratio,completion_on_date,name)
		time.sleep(Delay)

	FinalHashes = names['hashes' + str(1)]
	for n in range(2,ReqTimes+1):
		FinalHashes = FinalHashes & names['hashes' + str(n)]
	if len(FinalHashes):
		log.info(FinalHashes)
		sendNotify("删种结果",NotifyData)
		return list(FinalHashes)
	else:
		log.info("没有符合条件的种子，无需删除")
		sendNotify("删种结果","没有满足删种条件的种子")
		sys.exit(0)

######################################



deleteTorrents(GetSatisfiedTorrents())
