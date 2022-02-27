# coding=utf-8

import logging
from logging import handlers

class Logger(object):
	def __init__(self,file_name:str,level='info',backCount=5,when='D',interval=1):
		logger = logging.getLogger(file_name)  # 实例化一个logger对象，先创建一个办公室
		logger.setLevel(self.__get_level(level))  # 设置日志的级别的人
		cl  = logging.StreamHandler()  # 负责往控制台输出的人
		bl  = handlers.TimedRotatingFileHandler(filename=file_name, when=when, interval=interval, backupCount=backCount, encoding='utf-8')
		fmt = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
		cl.setFormatter(fmt)  # 设置控制台输出的日志格式
		bl.setFormatter(fmt)  # 设置文件里面写入的日志格式
		logger.addHandler(cl)
		logger.addHandler(bl)
		self.debug   = logger.debug
		self.warning = logger.warning
		self.info    = logger.info
		self.error   = logger.error


	def __get_level(self,str):
		level = {
			'debug':logging.DEBUG,
			'info':logging.INFO,
			'warn':logging.WARNING,
			'error':logging.ERROR
		}
		str = str.lower()
		return level.get(str)
