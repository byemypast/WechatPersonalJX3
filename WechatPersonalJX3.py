# -*- coding:utf-8 -*-  
import itchat, time, os
from itchat.content import *

import core.game
from core.debug import *
import core.userinfo
import core.settings
import core.jx3tieba
import os

#@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
@itchat.msg_register(TEXT)
def text_reply(msg):
	#itchat.send('%s: %s' % (msg['Type'], msg['Text']), msg['FromUserName'])
	try:
		userinfo = itchat.update_friend(msg['FromUserName'])
		usernick = userinfo['NickName']
		debug("收到消息！来源："+usernick+" 内容："+msg['Text'])
	except Exception as e:
		debug("回复消息：解析用户错误！错误原因："+str(e)+",msg = "+str(msg))
	if core.settings.get_value('TIEBA_SHIDA_UPDATEING_STATE')==False:
		core.game.core_input(usernick,int(time.time()),msg['Text'],msg['FromUserName'])
	else:
		itchat.send_msg('贴吧更新正在进行中，请稍后访问本公众号！',msg['FromUserName'])

@itchat.msg_register(FRIENDS)
def add_friend(msg):
	print(msg)
	itchat.add_friend(**msg['Text']) # 该操作会自动将新好友的消息录入，不需要重载通讯录
	itchat.send_msg('Nice to meet you!', msg['RecommendInfo']['UserName'])

@itchat.msg_register([MAP, CARD, NOTE, SHARING])
def other_reply(msg):
	itchat.send('你好~~',msg['FromUserName'])

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
	msg['Text'](msg['FileName'])
	return '@%s@%s' % ({'Picture': 'img', 'Video': 'vid'}.get(msg['Type'], 'fil'), msg['FileName'])

@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
	if msg['isAt']:
		itchat.send(u'@%s\u2005I received: %s' % (msg['ActualNickName'], msg['Content']), msg['FromUserName'])

class Init(object):
	def __init__(self):
		core.settings.set_value('TIEBA_SHIDA_UPDATEING_STATE',False)
		core.settings.set_value('RESTARTTIME',self.init_rewritetime())
		self.Init_userinfo()
		self.InitUpdateTieba()
		self.init_readskills()
	def init_readskills(self):
		debug("readskills组件初始化")
		try:
			f = open(core.settings.APP_skill_filename)
			skilllist = f.readlines()
			f.close()
			core.settings.set_value("APP_SKILL_SKILLLIST",skilllist)

			if not os.path.exists(core.settings.APP_skill_savedir):
				os.mkdir(core.settings.APP_skill_savedir)
		except Exception as e:
			debug("readskills组件初始化失败，原因："+str(e),'错误')
			return
		debug("readskills组件初始化成功！")

	def init_rewritetime(self):
		f = open("starttime.txt",'rU')
		s = f.readline()
		f.close()
		s = str(int(s)+1)
		f = open("starttime.txt",'w')
		f.write(s)
		f.close()
		return s
	def Init_userinfo(self):
		debug("userinfo组件初始化")
		if not os.path.exists(core.userinfo.dbname):
			debug("未找到数据库"+core.userinfo.dbname+"，开始重建数据库")
			core.userinfo.database_buildup()
		debug("userinfo组件初始化结束")
	def InitUpdateTieba(self):
		debug("初始化贴吧十大 启动",2)
		todayymd = time.strftime("%y-%m-%d")
		if not os.path.exists(todayymd+"_2"):
			debug("未检测到今日十大")
			core.jx3tieba.tiebatop_update("剑网三",todayymd)
			time.sleep(1)
		else:
			debug("检测到今日十大，直接使用已生成文件")	
		if core.settings.TIEBA_UPDATE_FORCE ==1:
			debug("十大强制更新开关 打开，开始更新十大")
			core.jx3tieba.tiebatop_update("剑网三",todayymd)
			time.sleep(1)
		f = open(todayymd+"_2",'rU',encoding = 'utf-8')
		tmplist = []
		for i in range(0,10):
			tmplist.append(f.readline().strip("\n"))
		core.settings.set_value('TIEBA_SHIDA',tmplist)
		core.settings.set_value('TIEBA_SHIDA_UPDATE',todayymd)
		core.settings.set_value('TIEBA_UPDATE_TO',todayymd)
	def RealTimeUpdateTieba(self): 
		timehm = time.strftime("%H-%M")
		todayymd = time.strftime("%y-%m-%d")
		if timehm==core.settings.get_value("TIEBA_UPDATETIME"):
			if core.settings.get_value("TIEBA_UPDATE_TO") != todayymd:
				core.settings.set_value('TIEBA_SHIDA_UPDATEING_STATE',True)
				debug("REALTIME_TIEBA_UPDATE : START",1)
				core.jx3tieba.tiebatop_update("剑网三",todayymd)
				core.settings.set_value('TIEBA_UPDATE_TO',todayymd)
				time.sleep(1)
				try:
					f = open(todayymd+"_2",'rU',encoding = 'utf-8')
					tmplist = []
					for i in range(0,10):
						tmplist.append(f.readline().strip("\n"))
					core.settings.set_value('TIEBA_SHIDA',tmplist)
					core.settings.set_value('TIEBA_SHIDA_UPDATE',todayymd)
				except:
					debug("******REALTIME_TIEBA_UPDATE : ERROR",1)
				debug("贴吧十大实时更新结束")
				core.settings.set_value('TIEBA_SHIDA_UPDATEING_STATE',False)
#start:

initobj = Init()
itchat.auto_login(True,enableCmdQR =2) #for linux
itchat.run(True,False)


while (1):
	initobj.RealTimeUpdateTieba()
	time.sleep(1)

'''
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
	msg['Text'](msg['FileName'])
	return '@%s@%s' % ({'Picture': 'img', 'Video': 'vid'}.get(msg['Type'], 'fil'), msg['FileName'])
'''

'''
@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
	if msg['isAt']:
		itchat.send(u'@%s\u2005I received: %s' % (msg['ActualNickName'], msg['Content']), msg['FromUserName'])
'''