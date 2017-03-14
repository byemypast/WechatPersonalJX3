# -*- coding:utf8 -*-  

import datetime
import core.settings
import core.userinfo
import core.floater
import core.goldprice
from core.debug import *
import time
import itchat
import requests
import random
import os
import json
import core.gameroom
import core.fetchhm
import core.tiebagold
PlayerState = {}
PlayerSendID = {}
VIPID = '@148cdb5861ba223818e905b76663b7591de19d1d6287838ffe9cf1bc73383e29'
TULINGKEY = '67896e1c48174b3c906c4f505226790b'
userdata = {}
TIEBA_state = {}
TotalServiceTime = 0
TalkingMode = {} #唠嗑模式记录
app_skill_lastinfo = {} #技能模式记录上一次技能
lobbyhelper = core.gameroom.gameroomhelper()
#0: 第一次对话介绍+主选单列出
#1：非第一次对话+主选单列出
#2：选择主选单
#3-5：唠嗑模式
#6：聊天模式
#10-20：看图标猜技能
#100：职业选择APP初始化
#200：贴吧百大
#300：漂流瓶
#400：VIP调戏模式
#500：游戏大厅
#600：狼人杀


def sendstr(talkto,sendmsg):
	debug('向【'+talkto+'】发送消息: '+str(sendmsg))
	itchat.send(sendmsg,PlayerSendID[talkto])

def sendlist(talkto,lists,pauserandom =0 ,pausefrom = 0,pauseto = 0):
	for i in lists:
		itchat.send(i,PlayerSendID[talkto])

def record_user(player_id,msg):
	f = open(core.settings.recordname,'a')
	f.write(time.ctime()+","+player_id+","+msg+"\n")
	f.close()

def get_userdata(player_id,retlist):
	allinfo = retlist
	dict2d_construct(userdata,player_id,'FLOATER_LEFT',allinfo[0][1]) #等待重构
	dict2d_construct(userdata,player_id,'VIP_LEVEL',allinfo[0][2])
	dict2d_construct(userdata,player_id,'SCORE',allinfo[0][3])
	dict2d_construct(userdata,player_id,'JOB',allinfo[0][4])
	dict2d_construct(userdata,player_id,'REGTIME',allinfo[0][5])


def flash_userdata(player_id):
	allinfo = core.userinfo.database_getall(player_id)
	if player_id in userdata:
		if allinfo==[]:
			debug("******Database damage in flash_userdata,"+ player_id)
			return
		else:
			get_userdata(player_id,allinfo)
	else:
		if allinfo==[]:
			core.userinfo.database_newuser(player_id)
			allinfo = core.userinfo.database_getall(player_id)
			get_userdata(player_id,allinfo)
		else:
			get_userdata(player_id,allinfo)
			
			
def get_usertype(player_id): 
	vip_value = str(userdata[player_id]['VIP_LEVEL'])
	if vip_value=='1':
		return '超级VIP'
	elif vip_value == '2':
		return 'VIP'
	elif vip_value =='3':
		return '首测'
	elif vip_value =='-1':
		return '黑名单'
	else:
		return '普通'
		
def core_input(player_id,talktime,msg,talksendid):
	flash_userdata(player_id)
	if get_usertype(player_id)=='黑名单':
		return
	if not player_id in PlayerState:
		PlayerState[player_id] = 0 #init

	PlayerSendID[player_id] = talksendid
	response(PlayerState[player_id],player_id,msg)

def APP_working(player_id):
	sendstr(player_id,"正在施工中，敬请期待~回复任意键返回主菜单")
	PlayerState[player_id] = 1

def APP_professiontest(player_id,state,msg):
	if state==100:
		strcache = ['唔，下面我会问你一些问题，请根据提示输入1或2或3',
								'Q1: 你喜欢读条吗？【1】我超喜欢的；【2】去特么的']
		sendlist(player_id,strcache,0,0,0)
		PlayerState[player_id] = 101
	elif state==101:
		if msg=='1':
			#万花 长歌 七秀 五毒 唐门 藏剑 纯阳
			sendstr(player_id,'Q2：那……你希望顺便玩玩治疗吗？【1】当然啦很有成就感；【2】治疗超累总是背锅')
			PlayerState[player_id] = 102
		elif msg=='2':
			#苍云 霸刀 少林 天策 丐帮 纯阳 明教
			sendstr(player_id,'Q2：你觉得当阵眼怎么样？【1】老子就要当小队VIP；【2】阵眼都是要饭的')
			PlayerState[player_id] = 103
		else:
			pass #随机输入不回答
	elif state==102:
		if msg=='1':
			#万花 长歌 七秀 五毒
			sendstr(player_id,'Q3：一个人在午夜，寂寞吗？【1】当然有人陪最好了；【2】老子无所畏惧')
			PlayerState[player_id] = 104
		elif msg=='2':
			#唐门 藏剑 纯阳
			sendstr(player_id,'Q3：一个人在午夜，有安全感吗？【1】吓得我开始熟悉技能了；【2】老子无所畏惧')
			PlayerState[player_id] = 105
		else:
			pass #随机输入不回答
	elif state==103:
		if msg=='1':
			#少林 丐帮
			sendstr(player_id,'Q3：遇到危险更喜欢明哲保身还是舍己为人？【1】死道友不死贫道；【2】艺高人胆大当然两肋插刀在所不辞')
			PlayerState[player_id] = 106
		elif msg=='2':
			#霸刀 苍云 天策 纯阳 明教
			sendstr(player_id,'Q3：遇到危险，你更希望以攻为守还是全身而退？【1】以攻为守；【2】全身而退；【3】钻地底下')
			PlayerState[player_id] = 107
		else:
			pass #随机输入不回答
	elif state==104:
		if msg=='1':
			#长歌 五毒
			sendstr(player_id,'Q4：你真的很希望试试治疗吗？【1】当然了；【2】打个酱油就好')
			PlayerState[player_id] = 108
		elif msg=='2':
			#万花 七秀
			sendstr(player_id,'Q4：在你理想中，你是个什么样的人？【1】知书达理的；【2】能歌善舞的')
			PlayerState[player_id] = 109
	elif state==105:
		if msg=='1':
			#唐门 纯阳
			sendstr(player_id,'Q4：喜欢移位吗？【1】那是我不仅自己跑跑跳跳，也要让别人跑跑跳跳；【2】老子就缩在这儿来打我啊')
			PlayerState[player_id] = 110
		elif msg=='2':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：藏剑~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
	elif state==106:
		if msg=='1':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：丐帮~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
		elif msg=='2':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：少林~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
	elif state==107:
		if msg=='1':
			#苍云 天策
			sendstr(player_id,'Q4：当你放大招被打断的时候，一点都忍不了吗？【1】气得手抖【2】被打断是常事儿早就习惯了')
			PlayerState[player_id] = 112
		elif msg=='2':
			#明教 纯阳 霸刀
			sendstr(player_id,'Q4：相权和皇权你觉得哪个更有翻云覆雨的潜力？【1】皇权【2】相权')
			PlayerState[player_id] = 113
		elif msg=='3':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：明教~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
	elif state==108:
		if msg=='1':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：五毒~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
		elif msg=='2':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：长歌~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
	elif state==109:
		if msg=='1':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：万花~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
		elif msg=='2':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：七秀~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
	elif state==110:
		if msg=='1':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：唐门~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
		elif msg=='2':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：纯阳~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
	elif state==111:
		#1 再来；2回主菜单
		if msg=='1':
			PlayerState[player_id] = 100
			APP_professiontest(player_id,100,"from state 111")
		elif msg=='2':
			PlayerState[player_id] = 1
			response(1,player_id,"from state 111")
	elif state==112:
		if msg=='1':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：苍云~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
		elif msg=='2':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：天策~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
	elif state==113:
		if msg=='1':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：霸刀~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
		elif msg=='2':
			sendstr(player_id,'Q5：恋家吗？【1】志在四方【2】常回家看看')
			PlayerState[player_id] = 114
	elif state==114:
		if msg=='1':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：明教~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111
		elif msg=='2':
			sendstr(player_id,'嘿嘿嘿，你最适合的职业大概是：纯阳~【仅供娱乐】希望再试一次吗？【1】我不服！再来！【2】玩腻了回主菜单')
			PlayerState[player_id] = 111

def APP_TuLing(player_id,msg):
	if msg=='退出':
		PlayerState[player_id] = 1
		response(1,player_id,'from state 6')
	else:
		apiUrl = 'http://www.tuling123.com/openapi/api'
		data = {
						'key'    : TULINGKEY, # 如果这个Tuling Key不能用，那就换一个
						'info'   : msg, # 这是我们发出去的消息
						'userid' : 'wechat-robot-'+str(player_id), # 这里你想改什么都可以
						}
		try:
			r = requests.post(apiUrl, data=data).json()
			sendstr(player_id,r.get('Text'))
		except Exception as e:
			debug("图灵机器人出错，错误原因："+str(e))
			sendstr(player_id,"群宝在打盹儿= =过会儿再来呗~~~")
		

def APP_ToTUTU(player_id):
	if (player_id =='若竹')or(player_id =='君逸')or(player_id =='春风扫残雪'):
		dnow = datetime.datetime.now()
		d0 = datetime.datetime(2017,2,14)
		d1 = datetime.datetime(2016,12,10)
		d2 = datetime.datetime(2016,11,13)
		d3 = datetime.datetime(2016,8,10)
		d4 = datetime.datetime(2016,5,21)
		strcache = [
		'秃秃~嘿嘿嘿你喜欢吗~这个程序是特意做给你的~',
		'平时咱俩都很忙的，本来见面次数就不多。再加上这个寒假各种贪睡，上线的次数也少了……',
		'我好内疚啊 #欣喜 所以一天夜里突发奇想开始码了这个程序，不知不觉已经几千行了',
		'当我在睡觉的时候，忙的时候，不能陪你的时候，希望你看到这个程序就能想起我_(:з」∠)_嘿嘿嘿~',
		'玩着玩着说不定就会忘了时间，我会很快赶来陪秃秃的~'
		'——以此纪念我们2017年2月14日，我们过的第一个情人节 ^_^',
		'#欣喜 #欣喜 我爱你！'
		'表白纪念日：       2016年12月10日 距离此日已经：' + str((dnow-d1).days),
		'见面纪念日：       2016年11月13日 距离此日已经：' + str((dnow-d2).days),
		'情缘纪念日：       2016年 8月10日 距离此日已经：' + str((dnow-d3).days),
		'认识纪念日：       2016年 5月21日 距离此日已经：' + str((dnow-d4).days),
		'程序上线日：       2017年 2月14日 距离此日已经：' + str((dnow-d0).days),
		'·回复任意键返回主菜单'
		]
		sendlist(player_id,strcache,1,0.1,0.5)
	else:
		strcache = [
		'有一个姑娘~她有一些任性她还有一些~~嚣张~~ #笨猪',
		'有一个姑娘~她有一些叛逆她还有一些~~疯狂~~ #欣喜',
		'哦~~是哪个姑娘啊~~哦~~ #噢',
		'哦~~~~那就是蠢秃秃啊~ #笨猪',
		'以此纪念2017年和情缘缘蠢秃秃的情人节',
		'·回复任意键返回主菜单']
		sendlist(player_id,strcache,1,0.1,0.5)
	PlayerState[player_id] = 1 #主菜单

def APP_TIEBA_TOP10(player_id,state,msg):
	debug("进入应用：贴吧十大 "+player_id+" state:"+str(state)+" msg:"+msg)
	global TIEBA_state
	TIEBA_UPDATE_TO = core.settings.get_value("TIEBA_UPDATE_TO")
	TIEBA_SHIDA = core.settings.get_value("TIEBA_SHIDA")
	TIEBA_SHIDA_UPDATE = core.settings.get_value("TIEBA_SHIDA_UPDATE")
	f = open(TIEBA_UPDATE_TO+"_1",encoding = 'utf-8')
	top100_1 = f.readlines()
	f.close()
	
	f = open(TIEBA_UPDATE_TO+"_2",encoding = 'utf-8')
	top100_2 = f.readlines()
	f.close()
		
	if (userdata[player_id]['VIP_LEVEL']>2)and(core.settings.TIEBA_TOP100_TONONVIP == 0):
		#非VIP,且不对所有人开放百大
		strcache = [
		"今日（"+TIEBA_SHIDA_UPDATE+"）十大：",
		"(*您目前的权限为 普通用户，可浏览TOP 10)",
		"标题--回复数--作者--发帖时间--贴吧地址(kz)"]
		sendlist(player_id,strcache,0,0,0)
		sendlist(player_id,TIEBA_SHIDA,0,0,0)
		sendstr(player_id,"本程序约于每晚六点自动更新，届时系统会卡住一段时间，请您耐心等待")
		PlayerState[player_id] = 1
	else:
		if state == 200:
			sendstr(player_id,"嘿嘿嘿~你好呀~ "+get_usertype(player_id)+ " 用户 "+player_id+", 请选择您想查询的类别：【1】今日百大（今日内发帖）；【2】全部百大（今日内回复）")
			PlayerState[player_id] = 201
			TIEBA_state[player_id] = (0,0) #(文件名序号,页数--页数*10)
			return
		elif state == 201:
			if msg =='1':
				strcache = [
				"今日（"+TIEBA_SHIDA_UPDATE+"）百大：",
				"(*您目前的权限为 "+get_usertype(player_id)+ " 用户，可浏览TOP 100)",
				"标题--回复数--作者--发帖时间--贴吧地址(kz)"]
				sendlist(player_id,strcache,0,0,0)
				sendlist(player_id,top100_2[0:10],0,0,0)
				sendstr(player_id,"第 1 / 10 页 【-1】上一页 【1】下一页 【x】退出")
				PlayerState[player_id] = 202
				TIEBA_state[player_id] = (2,0)
			else:
				strcache = [
				"全部（"+TIEBA_SHIDA_UPDATE+"）百大：",
				"(*您目前的权限为 "+get_usertype(player_id)+ " 用户，可浏览TOP 100)",
				"标题--回复数--作者--发帖时间--贴吧地址(kz)"]
				sendlist(player_id,strcache,0,0,0)
				sendlist(player_id,top100_1[0:10],0,0,0)
				sendstr(player_id,"第 1 / 10 页 【-1】上一页 【1】下一页 【x】退出")
				PlayerState[player_id] = 202
				TIEBA_state[player_id] = (1,0)
		elif state == 202:
			fname_id,page = TIEBA_state[player_id]
			if (msg.lower()=='x')or(msg=='退出'):
				PlayerState[player_id] = 1
				response(1,player_id,'from state 202')
				return
			try:
				addmsg = int(msg)
			except:
				if msg.find('上')>=0:
					addmsg = -1
				elif msg.find('下')>=0:
					addmsg = 1
				else:
					addmsg = 0
			page += addmsg
			if page<0:
				page = 9
			if page>9:
				page = 0
			TIEBA_state[player_id] = (fname_id,page)
			sendstr(player_id,"标题--回复数--作者--发帖时间--贴吧地址(kz)")
			if fname_id == 1:
				sendlist(player_id,top100_1[page*10:(page+1)*10],0,0,0)
			else:
				sendlist(player_id,top100_2[page*10:(page+1)*10],0,0,0)
			sendstr(player_id,"第 "+ str(page+1)+" / 10 页 【-1】上一页 【1】下一页 【x】退出")


def APP_GameLobby(player_id,state,msg):
	if state==500:
		#刚进大厅
		sendstr(player_id,"欢迎来到游戏大厅！当前房间号有：" + str(lobbyhelper.RoomNameList)+"。您可以输入相应的房间号进入房间，或使用指令【建立房间】新建一个房间。")
		for room in lobbyhelper.RoomNameList:
			sendstr(player_id,lobbyhelper.RoomList[room].GetRoomInfo())
		PlayerState[player_id] = 501
	elif state==501:
		if msg=='建立房间':
			sendstr(player_id,"请输入您的房间名称：")
			PlayerState[player_id] = 502
		else:
			if msg in lobbyhelper.RoomNameList:
				room = lobbyhelper.RoomList[msg]
				if room.roommax <= len(room.PlayerID):
					pass #待完成
			else:
				sendstr(player_id,"没有这个房间，请重试！")
def APP_GuessSkill(player_id,state,msg):
	if state==10:
		#第一次进入
		sendstr(player_id,'请输入每个图标代表的技能/奇穴名，不记得的话随便输啥都行。系统会稍后自动给出正确答案（多个版本可能由于多心法/技能/版本等）。回复【退出】退出该模式~')
		sendstr(player_id,'*注：说明针对各门派JJC奇穴')
		PlayerState[player_id] = 11
		app_skill_lastinfo[player_id] = ("",[])
	else:
		if msg=='退出':
			PlayerState[player_id] = 1
			response(1,player_id,'state 10/11 from guessskill')
			return
		lastname,lastdescribe = app_skill_lastinfo[player_id]
		if msg!=lastname:
			sendstr(player_id,'猜错啦！上次的技能是：' + lastname)
		else:
			sendstr(player_id,'猜对啦！')
		for index,msg in enumerate(lastdescribe):
			sendstr(player_id,'版本 %s' % (index+1))
			sendstr(player_id,"\n".join(msg))


	skilllist = core.settings.get_value("APP_SKILL_SKILLLIST")
	randskill = random.choice(skilllist).replace("/",'or').strip("\n").split("\t")
	if os.path.exists(core.settings.APP_skill_savedir+str(hash(randskill[0]))+".png"):
		#有缓存
		skilliconfile = core.settings.APP_skill_savedir+str(hash(randskill[0]))+".png"
		skillinfo = json.loads(open(core.settings.APP_skill_savedir+randskill[0]+".txt").read())
	else:
		hminfo = core.fetchhm.GetHMInfo()
		skillicon,skillinfo = hminfo.GetSkill(randskill[0])
		if skillinfo == None:
			sendstr(player_id,'获取信息失败！可能是网络错误~')
			PlayerState[player_id] = 1
			response(1,player_id,'state 10/11 from guessskill error')
			return
		skillicon.save(core.settings.APP_skill_savedir+randskill[0]+".png")
		skillicon.save(core.settings.APP_skill_savedir+str(hash(randskill[0]))+".png")
		skilliconfile = core.settings.APP_skill_savedir+str(hash(randskill[0]))+".png"
		f = open(core.settings.APP_skill_savedir+randskill[0]+".txt",'w')
		f.write(json.dumps(skillinfo))
	app_skill_lastinfo[player_id] = (randskill[0],skillinfo)
	sendstr(player_id,randskill[1]+", 功能简要描述："+randskill[2], player_id)
	msg = itchat.send_image(core.settings.APP_skill_savedir+str(hash(randskill[0]))+".png",PlayerSendID[player_id])
	info = APP_GuessSkill_GetALikeSkill(randskill[0])
	if info!=None:
		#是奇穴
		sendstr(player_id,"该技能的同层重要奇穴为："+"\n".join(info))
def APP_GuessSkill_GetALikeSkill(skillname):
	'''得到同层奇穴信息。如果为技能则不返回任何'''
	returnlist = []
	if skillname.find("重")<0:
		return None
	else:
		for index,skill in enumerate(core.settings.get_value("APP_SKILL_SKILLLIST")):
			if skill.find(skillname[1:])>=0:
				returnlist.append(skill)
	return returnlist
def response(state,player_id,msg):
	debug("response received. state: "+str(state)+" "+player_id+" "+msg,1)
	global TotalServiceTime 
	global PlayerState
	TotalServiceTime += 1
	VIPChoice = ['【VIP1】: 强制更新贴吧百大','【VIP2】: 返回系统日志']
	
	if state == 0: #第一次对话，应介绍本程序，并列出所有的application msg:随机内容
		strcache = [
		'嘿嘿嘿你好啊~ ' + player_id+'，抓到我啦~',
		'这里是网三纵月【北京大学】帮会聊天机器人，目前版本 '+ str(core.settings.VERSION),
		'希望能给在无聊的日日日日常中给你一点乐趣和惊喜',
		'【1】: 查看给蠢蠢秃的特别消息 ',
		'【2】: 剑网3 贴吧 今日热门(每晚六点更新) '
		'【3】: 我真的适合玩这个鬼职业吗 '
		'【4】: 漂流瓶 ',
		'【5】: 瞎比唠唠嗑 '
		'【6】: 入帮/给作者提意见添加更多功能 '
		'【7】: 本次开机统计/我的状态 '
		'【8】: 给蠢蠢秃的女生节消息(几率开放/新消息)'
		'【9】: 纵月实时最高金价(5173/贴吧)'
		'【10】: 看图标猜技能']
		if get_usertype(player_id).find('VIP')>=0:
			strcache += VIPChoice
		sendlist(player_id,strcache,1,0.1,0.5)
		PlayerState[player_id] = 2
	elif state == 1: #非第一次对话，主选单，msg:随机内容
		strcache = [
		'嘿嘿嘿~ ' + player_id+'，欢迎回来~ #欣喜',
		'【1】: 查看给蠢蠢秃的特别消息 ',
		'【2】: 剑网3 贴吧 今日热门(每晚六点更新) '
		'【3】: 我真的适合玩这个鬼职业吗 '
		'【4】: 漂流瓶 ',
		'【5】: 瞎比唠唠嗑 '
		'【6】: 入帮/给作者提意见添加更多功能 '
		'【7】: 本次开机统计/我的状态 '
		'【8】: 给蠢蠢秃的女生节消息(几率开放/新消息)'
		'【9】: 纵月实时最高金价(5173/贴吧)'
		'【10】: 看图标猜技能']
		if get_usertype(player_id).find('VIP')>=0:
			strcache += VIPChoice
		sendlist(player_id,strcache,1,0.1,0.5)
		PlayerState[player_id] = 2
	elif state == 2: # 选择进入不同应用程序 msg:主选单选择
		if msg=="1":
			APP_ToTUTU(player_id)
		elif msg=="2":
			PlayerState[player_id] = 200
			APP_TIEBA_TOP10(player_id,200,msg)
		elif msg=="3":
			PlayerState[player_id] = 100
			APP_professiontest(player_id,100,msg)
		elif msg =="4":
			PlayerState[player_id] = 300
			PlayerState = core.floater.APP_floater_main(player_id,300,msg,userdata,PlayerState)
		elif msg=="5":
			sendstr(player_id,'来吧小伙儿~随便说说吧~我在听着呢！一定注意回复两个汉字【退出】结束该模式~')
			TalkingMode[player_id] = ""
			PlayerState[player_id] = 3
		elif msg=='6':
			sendstr(player_id,'嘿嘿嘿欢迎加入中恶六级帮会【北京大学】~入帮直接申请就好~')
			sendstr(player_id,'如果有什么建议，欢迎写信给ID【北京大学】或者直接在主菜单中选择唠嗑模式。一会儿会自动回到主菜单，我会看到的~蟹蟹大佬！')
			PlayerState[player_id] = 1
		elif msg=="7":
			dnow = datetime.datetime.now()
			totalnum = core.userinfo.database_query("SELECT count(*) FROM userdata")[0][0]
			strcache = '本次程序开始至今，共运行：' + str((dnow-core.settings.STARTTIME).seconds) + "秒，收到查询 " + str(TotalServiceTime) +" 次。数据库中共有用户： "+ str(totalnum)+" 个。这是程序的第 "+ str(core.settings.get_value("RESTARTTIME"))+" 次启动。任意键返回主菜单"
			sendstr(player_id,strcache)
			strcache = '[ '+get_usertype(player_id)+" 用户 ] " +player_id+" ，您的注册时间为 "+ userdata[player_id]['REGTIME']
			sendstr(player_id,strcache)
			PlayerState[player_id] = 1
		elif msg=='8':
			#sendstr(player_id,'回复【退出】退出聊天模式！')
			#PlayerState[player_id] = 6
			strgouliang = ['最喜欢蠢蠢秃啦！','要吃的：川军本色、高配德川家、各地驻京办、壹圣元火锅','捏~~~~~',
									'前几天刚下完金刚狼_(:з」∠)_不知道啥时候有空看啊好忙啊','心痛下周就要削大师了心塞','蠢蠢秃我们啥时候出去玩吼不吼啊！【虽说好像附近没啥好玩的',
									'其实我一直想去做蛋糕……啥玩意儿没玩过hhhhh','啊啊啊想不出来了偷偷凑个字没人发现吧= =','来本部玩啊来本部玩啊~~~','啊等这个号重新上线的时候不知道是哪天了_(:з」∠)_']
			if (player_id=='君逸')or(player_id=='若竹'):
				sendstr(player_id,random.choice(strgouliang))
			else:
				x = random.randint(1,10)
				if x<=3:
					sendstr(player_id,random.choice(strgouliang))
				else:
					sendstr(player_id,'嘿嘿嘿不给你吃~要不再试试？几率大概1/3左右')
			response(1,player_id,'from state 1,msg 8')
		elif msg=='9':
			data = core.goldprice.Get_5173Info()
			maxprice = data.GetMaxPriceNow()
			datatieba = core.tiebagold.tiebagold()
			maxpricetieba,maxtimetieba = datatieba.GetGold()
			sendstr(player_id,'当前5173最高金价为：'+str(maxprice))
			sendstr(player_id,'当前贴吧最高金价为： %s 。报价时间为 %s ' % (maxpricetieba,maxtimetieba))
			response(1,player_id,'from state 1,msg 9')
		elif msg=='10':
			PlayerState[player_id] = 10
			APP_GuessSkill(player_id,10,msg)
		elif msg.lower().find("vip1")>=0:
			if get_usertype(player_id).find('VIP')<0:
				if msg.find(core.settings.controlPWD)<0:
					sendstr(player_id,'请检查您的密码！')
					debug('密码输入错误！密码：'+str(msg)+"，来源ID："+str(player_id),'警告')
					response(1,player_id,"from vip1 state 1")
					return
			#是VIP或者密码正确：

			todayymd = time.strftime("%y-%m-%d")
			debug("程序收到强制更新贴吧十大指令，来源："+player_id,'信息')
			debug("REALTIME_TIEBA_UPDATE : START",1)
			core.settings.set_value('TIEBA_SHIDA_UPDATEING_STATE',True)
			core.jx3tieba.tiebatop_update("剑网三",todayymd,player_id)
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
			response(1,player_id,'from state 1,msg vip1')
		elif msg.lower().find("vip2")>=0:
			if get_usertype(player_id).find('VIP')<0:
				if msg.find(core.settings.controlPWD)<0:
					sendstr(player_id,'请检查您的密码！')
					debug('密码输入错误！密码：'+str(msg)+"，来源ID："+str(player_id),'警告')
					response(1,player_id,"from vip1 state 1")
					return
			#是VIP或者密码正确：
			itchat.send_file("debug.txt",PlayerSendID[player_id])
			itchat.send_file("userdb.db",PlayerSendID[player_id])
			itchat.send_file("floater_pool.txt",PlayerSendID[player_id])
			itchat.send_file("record.txt",PlayerSendID[player_id])
			response(1,player_id,'from state 1,msg vip2')
	elif (int(state)>=3)and(int(state)<=5):
		#唠嗑模式
		if state==3:
			TalkingMode[player_id] += msg +"\n"
			if msg=='退出':
				record_user(player_id,TalkingMode[player_id])
				sendstr(player_id,"嘿嘿嘿~灰常感谢~收到啦！#欣喜【任意键】返回主菜单~")
				PlayerState[player_id] = 1
				if get_usertype(player_id).find('VIP')>=0:
					#VIP直接发邮件
					sendstr(VIPID, player_id +" 的唠嗑信息" + TalkingMode[player_id])
				TalkingMode[player_id] = ""
	elif (int(state))==6:
		APP_TuLing(player_id,msg)	
				
	elif (int(state)>=10)and(int(state)<20):
		APP_GuessSkill(player_id,state,msg)
	elif (int(state)>=100)and(int(state)<200):
		APP_professiontest(player_id,state,msg)
	elif (int(state>=200)and(int(state)<300)):
		APP_TIEBA_TOP10(player_id,state,msg)
	elif (int(state>=300)and(int(state)<400)):
		PlayerState = core.floater.APP_floater_main(player_id,state,msg,userdata,PlayerState)
	elif (int(state>=400)and(int(state)<500)):
		PlayerState = core.app.vip1.APP_vip1core(player_id,state,msg,PlayerState)
		
def dict2d_construct(thedict, key_a, key_b, val):
  if key_a in thedict:
    thedict[key_a].update({key_b: val})
  else:
    thedict.update({key_a:{key_b: val}})

'''

万花 长歌 苍云 霸刀 少林 七秀 五毒 唐门 藏剑 天策 丐帮 纯阳 明教

-愿意读条吗
1: 万花 长歌 七秀 五毒 唐门 藏剑 纯阳
 -希望至少顺便玩奶吗
  1: 万花 长歌 七秀 五毒
   -一个人的时候寂寞吗
    1: 长歌 五毒
    -你真的很想玩奶吗
     1:五毒
     2:长歌
    2: 万花 七秀
    -更希望大家子弟还是轻歌曼舞
     1:万花
     2:七秀
  
  2: 唐门 藏剑 纯阳
   -一个人的时候有安全感吗
     1:唐门 纯阳
     -喜欢跑来跑去吗
      1：唐门
      2: 纯阳
     2:藏剑

2: 苍云 霸刀 少林 天策 丐帮 纯阳 明教
 -觉得阵眼怎么样
  1: 少林 丐帮
   -更倾向舍己为人还是明哲保身
    1:少林 2:丐帮
  2: 霸刀 苍云 天策 纯阳 明教
   -遇到危险的时候，你更希望
    1以攻为守: 苍云 天策
     -放大招被打断很烦躁一点也不能忍吗
      1:苍云
      2:天策
    2全身以退: 明教 纯阳 霸刀
     -更倾向攻击还是辅助？
       1:霸刀
       2:明教 纯阳
       -恋家吗
        1:纯阳
        2:明教
    3钻地底下: 明教
'''
