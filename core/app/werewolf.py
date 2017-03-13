import itchat
import time
import random
from core.debug import debug
class werewolf(object):
	"""
	开启一局新的狼人杀
	参数：PlayerName[] 游戏者昵称
				PlayerID[]   游戏者微信ID（若为空，则电脑托管）
	"""
	def __init__(self,PlayerName,PlayerID):
		self.PlayerName = PlayerName
		self.PlayerID = PlayerID
		self.strwords = werewolfstrs()
		self.PlayerState = dict.fromkeys(self.PlayerName,'存活') #游戏状态
		self.PlayerStateID = dict.fromkeys(self.PlayerName,600) #600: 狼人杀默认状态
		self.PlayerCouple = [] #狼人杀情侣
		self.PlayerDefended = [] #狼人杀每局守卫对象
		self.PlayerWolfChoose = "" #狼人杀狼人选择对象
		self.PlayerWolfState = {} #狼人杀狼人状态
		self.PlayerDayState = {} #白天玩家状态
		self.PlayerDayChoose = "" #白天投票目标
		self._assigncharacter() #分配角色
		self.PlayerWitchProtect = "" #狼人杀女巫选择保护对象
		self.PlayerWitchProtectTime = 1 #保护次数
		self.PlayerWitchKill  = "" #狼人杀女巫选择杀人对象
		self.PlayerWitchKillTime = 1 #杀人次数
		self._nightinit(True) #开始第一天夜晚
	def _sendstr(self,sendstr,tolist):
		'''向某人发送消息，tolist为目标name对象,也可以为一个玩家的str'''
		if type(tolist)!=list:
			tolist = [tolist]
		for player in tolist:
			if self.PlayerID[player]!='':
				itchat.send_msg(sendstr,self.PlayerID[player])
				debug("向 %s 发送消息：%s" %(player,sendstr),'狼人杀')
	def _sendtoall(self,sendstr):
		'''向所有人发送消息'''
		self._sendstr(sendstr,self.PlayerName)
	def _assigncharacter(self):
		'''向所有人分配角色'''
		t_character = self.strwords.settings_character[len(self.PlayerID)].copy()
		random.shuffle(t_character)
		self.PlayerCharacter = dict(zip(self.PlayerID,t_character))
		#向所有人介绍局势
		self._sendtoall(self.strwords.settings_charaintro[len(self.PlayerID)])
		#向玩家介绍角色
		for player in self.PlayerName:
			self._sendstr(self.strwords.strs_charayours + self.PlayerCharacter[player],player)
	def _getplayerfromstate(self,state = '存活',exclude = [],optionlist = False):
		'''得到在场的玩家列表, state = 玩家状态,exclude = 除了某个人 optionlist: 是否返回菜单格式的字符串，如果不是则只返回列表'''
		if type(exclude)!=list:
			exclude = [exclude]
		if optionlist == False:
			returnlist = []
			for player in self.PlayerName:
				if (self.PlayerState[player] == state)and(not(player in exclude)):
					returnlist.append(player)
			return returnlist
		else:
			returnstr = ""
			for index,player in enumerate(self.PlayerName):
				if (self.PlayerState[player] == state)and(not(player in exclude)):
					returnstr += "【%d】 %s" % (index,player)
			return returnstr
	def _getplayerfromchara(self,chara,exclude = [],optionlist = False,excludedead = True):
		'''得到在场的玩家列表, chara = 玩家身份,exclude = 除了某个人 optionlist: 是否返回菜单格式的字符串，如果不是则只返回列表'''
		if type(exclude)!=list:
			exclude = [exclude]
		if excludedead ==True:
			exclude += self._getplayerfromstate('死亡')
		if optionlist==False:
			returnlist = []
			for player in self.PlayerName:
				if (self.PlayerCharacter[player] == chara)and(not(player in exclude)):
					returnlist.append(player)
			return returnlist
		else:
			returnstr = ""
			for index,player in enumerate(self.PlayerName):
				if (self.PlayerCharacter[player] == chara)and(not (player in exclude)):
					returnstr += "【%d】 %s" % (index,player)
			return returnstr
	def _getplayernotbot(self):
		'''得到非机器人的玩家列表'''
		returnlist = []
		for player in self.PlayerID:
			if self.PlayerID[player]==0:
				returnlist.append(player)
		return returnlist
	def _changestate(self,playerlist,tostate):
		'''改变playerlist(/player str)的state值'''
		if type(playerlist)!=list:
			playerlist = [playerlist]
		for player in playerlist:
			self.PlayerStateID[player] = tostate
	def _fakesleep(self,floatsec = None):
		'''假死，避免用户通过时间作弊。但目前为真死。待改进。若None则默认改为words中的settings'''
		if floatsec == None:
			floatsec = self.strwords.settings_fakesleep
		time.sleep(floatsec)
	def _killandcalc(self,killlist):
		'''杀指定对象并判断胜负'''
		if type(killlist)!=list:
			killlist = [killlist]
		self._changestate(killlist,'死亡')
		self._sendstr(self.strwords.strs_killtips,killlist)
		if self._getplayerfromchara("民")==[]:
			return "狼胜"
		elif self._getplayerfromchara("狼")==[]:
			return "民胜"
		elif self._getplayerfromstate()==self.PlayerCouple:
			return "情侣胜"
		else:
			return "继续"
			

	def _IsVaildResponse(self,msg,player,couldzero = False):
		'''通用合法性回复检查（仅限于回复123的情况）.couldzero = True时可以等于0（如女巫）'''
		try:
			error = False #合法性检查
			indexid = int(msg)
			if (indexid>len(self.PlayerName))or(self.PlayerState[indexid]=='死亡')or(indexid<0):
				error = True
			else:
				if (couldzero ==False)and(indexid == 0):
					error = True
		except:
			error = True
		if error ==True: 
			self._sendstr('格式错误！请重试',player)
			return False
		else:
			return True
	def _nightinit(self,FirstNight = False):
		'''夜晚初始化'''
		self.PlayerDefended = [] #狼人杀每局守卫对象
		self.PlayerWolfChoose = "" #狼人杀狼人选择对象
		self.PlayerWolfState = {} #狼人杀狼人状态
		self.PlayerWitchProtect = "" #狼人杀女巫选择保护对象
		self.PlayerWitchKill  = "" #狼人杀女巫选择杀人对象
		self._sendtoall(self.strwords.strs_start) #夜晚开始
		if FirstNight==True:
			return self._nightstart1()
		else:
			return self._nightstart2()
		pass #初始化结束
	def _dayinit(self): 
		'''白天初始化'''
		self.PlayerDayState = dict.fromkeys(list(set(self._getplayerfromstate()).intersection(set(self._getplayernotbot))),'未准备') #存活的非机器人玩家
		return self._daystart1()
	def _nightstart1(self):
		'''狼人杀夜间模式_1: 丘比特睁眼-丘比特射人'''
		self._sendtoall(self.strwords.strs_opencupid) #丘比特睁眼
		if self._getplayerfromchara('丘比特')!=[]: #场上还有丘比特
			self._sendstr(self.strwords.str_cupiding % self._getplayerfromstate(optionlist = True),self._getplayerfromchara('丘比特')) #向丘比特发送消息
			self._changestate(self._getplayerfromchara("丘比特"),601) #601：丘比特选择
		else:
			self._fakesleep()
			self._sendtoall(self.strwords.strs_closecupid) #丘比特结束
			self._sendstr(self.strwords.strs_couple % str(self.PlayerCouple),self.PlayerCouple) #本局游戏情侣
			return self._nightstart2()
	def _nightstart2(self):
		'''狼人杀夜间模式_2: 守卫睁眼-守卫选择'''
		self.PlayerDefended = [] #清空上一句守护
		self._sendtoall(self.strwords.strs_defend_open) #守卫睁眼
		if self._getplayerfromchara('守卫')!=[]: #场上还有守卫
			self._sendstr(self.strwords.strs_defending % self._getplayerfromstate(optionlist = True),self._getplayerfromchara('守卫')) #向丘比特发送消息
			self._changestate(self._getplayerfromchara("守卫"),602) #602：守卫选择
		else:
			self._fakesleep()
			self._sendtoall(self.strwords.strs_defend_over) #守卫结束
			return self._nightstart3()
	def weighted_choice(self,weights):
		'''加权随机数。返回权重数组的下标'''
		rnd = random.random() * sum(weights)
		for i, w in enumerate(weights):
			rnd -= w
			if(rnd < 0):
				return i
	def _nightstart3(self):
		'''狼人杀夜间模式_3: 预言家睁眼-预言家选择'''
		self._sendtoall(self.strwords.strs_openpredict) #预言家睁眼
		if self._getplayerfromchara('预言家')!=[]: #场上还有预言家
			self._sendstr(self.strwords.strs_predicting % self._getplayerfromstate(optionlist = True),self._getplayerfromchara('预言家')) #向预言家发送消息
			self._changestate(self._getplayerfromchara("预言家"),603) #603：预言家选择
		else:
			self._fakesleep()
			self._sendtoall(self.strwords.strs_closepredict) #预言家结束
			return self._nightstart4()
	def _nightstart4(self): 
		'''狼人杀夜间模式_3: 狼人睁眼-狼人选择'''
		self.PlayerWolfChoose = "" #狼人最终选择
		self.PlayerWolfState = dict.fromkeys(self._getplayerfromchara("狼人"),"准备中") #狼人选择状态
		self._sendtoall(self.strwords.strs_openrecwolf) #狼人睁眼
		self._sendstr(self.strwords.strs_openrecwolfappend + str(self._getplayerfromchara("狼人")),self._getplayerfromchara("狼人")) #本场剩余狼人
		self._sendstr(self.strwords.strs_killwolf_choose % self._getplayerfromstate(exclude = self._getplayerfromchara("狼人"),optionlist = True),self._getplayerfromchara('狼人')) #向狼人发送消息。选择非狼人的玩家
		self._changestate(self._getplayerfromchara("预言家"),604) #604：狼人选择。不可能存在狼人死光的情况
		return self._nightstart5()
	def _nightstart5(self):
		'''狼人杀夜间模式_3: 女巫睁眼-女巫选择'''
		self._sendtoall(self.strwords.strs_openwitch) #女巫睁眼
		deadlist = self._nightcalc()
		if deadlist == []:
			strnodead = self.strwords.strs_openwitch % self.strwords.strs_openwitch_nodead
			self._sendtoall(strnodead) #向所有人公布今晚没死人
		else:
			strdead = self.strwords.strs_openwitch %(self.strwords.strs_openwitch_dead %(str(deadlist)))
			strdeadtoall = self.strwords.strs_openwitch %(self.strwords.strs_openwitch_dead %("【"+str(len(deadlist)))+"个人】")
			self._sendstr(strdead,self._getplayerfromchara("女巫")) #告诉女巫今晚的死讯
			self._sendstr(strdeadtoall,self._getplayerfromstate(state='存活',exclude=self._getplayerfromchara("女巫"))) #向除了女巫之外的人告诉今晚的死亡人数
		if self._getplayerfromchara('女巫')!=[]: #场上还有女巫
			self._sendstr(self.strwords.strs_openwitch_helpnotice ,self._getplayerfromchara('女巫')) #询问女巫救不救 
			self._changestate(self._getplayerfromchara("女巫"),605) #605：女巫救人选择
		else:
			self._fakesleep()
			self._sendtoall(self.strwords.strs_openwitch_poison) #向所有人提示是否杀人
			self._fakesleep()
			self._sendtoall(self.strwords.strs_closewitch,self._getplayerfromstate()) #女巫闭眼
			return self._dayinit()
	def _nightcalc(self,addwitch = True,couple = True):
		'''夜间清算 addwitch=false时仅计算守卫/狼人 =True时加入女巫。 couple=false时不考虑情侣'''
		deadlist = [self.PlayerWolfChoose] #本局狼人选择
		for guard in self.PlayerDefended: #守卫保护
			if guard in deadlist:
				deadlist.remove(guard)
		if addwitch==True:
			if (self.PlayerWitchProtectTime>=0)and(self.PlayerWitchProtect in deadlist): #女巫守护
				deadlist.remove(self.PlayerWitchProtect)
			if (self.PlayerWitchKillTime>=0)and(self.PlayerWitchKill!='')and(not(self.PlayerWitchKill in deadlist)): #女巫杀人.杀人剩余次数>0 + 非空 + 前面没有杀
				deadlist.append(self.PlayerWitchKill)
		if couple==True:
			addcouple = False
			for dead in deadlist:
				for couplepeo in self.PlayerCouple:
					if (dead==couplepeo):
						addcouple = True
			if addcouple == True:
				for couplepeo in self.PlayerCouple:
					if (not(couplepeo in deadlist)):
						deadlist.append(couplepeo)
		return deadlist
	def _daystart1(self):
		deadlist = self._nightcalc()
		result = self._killandcalc(deadlist)
		if deadlist == []:
			self._sendtoall(self.strwords.strs_nightpeave) #平安夜提示
		else:
			self._sendtoall(self.strwords.strs_nightover %(str(deadlist),str(deadlist))) #死人提示
		if result=='继续':
			self._sendtoall(self.strwords.strs_daynotice) #白天讨论提示
			self._changestate(self._getplayerfromstate(),607)
		else:
			return result



	def response_core(self,player,msg):
		'''
		601:丘比特选择
		602:守卫选择  
		603:预言家选择
		604:狼人选择
		605:女巫救人
		606:女巫杀人
		607:白天玩家讨论
		608:白天杀人投票
		609:观察者模式
		'''
		state = self.PlayerStateID[player]
		if state==601:
			try:
				error = False #合法性检查
				info = msg.strip("\n").split("-")
				for indexid in info:
					if (indexid>len(self.PlayerName))or(self.PlayerState[indexid]=='死亡')or(indexid<=0):
						error = True
			except:
				error = True
			if error ==True: 
				self._sendstr('格式错误！请重试',player)
				return
			for indexid in info: #添加游戏情侣
				self.PlayerCouple.append(PlayerName[indexid])
			self._changestate(player,600) #恢复正常状态
			self._sendtoall(self.strwords.strs_closecupid) #丘比特结束
			self._sendstr(self.strwords.strs_couple % str(self.PlayerCouple),self.PlayerCouple) #本局游戏情侣
			return self._nightstart2()
		elif state==602:
			if self._IsVaildResponse(msg,player)==False:
				return
			indexid = int(msg)
			self.PlayerDefended.append(self.PlayerName(indexid))
			self._changestate(player,600) #恢复正常状态
			self._sendtoall(self.strwords.strs_defend_over) #守卫结束
			return self._nightstart3()
		elif state==603:
			if self._IsVaildResponse(msg,player)==False:
				return
			indexid = int(msg)
			self._sendstr(self.strwords.strs_predictok %(self.PlayerName[indexid],self.PlayerState[self.PlayerName[indexid]]),player) #向预言家告诉他选择人的身份
			self._changestate(player,600) #恢复正常状态
			self._sendtoall(self.strwords.strs_closepredict) #预言家结束
			return self._nightstart4()
		elif state==604:
			if msg!='确认':
				if self._IsVaildResponse(msg,player)==False:
					return
				indexid = int(msg)
				self.PlayerWolfState[player] = self.PlayerName(indexid)+"（未确认）" #更新自己的选择状态
				self._sendstr(self.strwords.strs_killwolf_chooseother%(player,self.PlayerName(indexid)+"（未确认）"),self._getplayerfromchara("狼人")) #向其他狼人广播自己的选择
			else:
				self.PlayerWolfState[player] = self.PlayerWolfState[player].replace("（未确认）","")
				self._sendstr(self.strwords.strs_killwolf_chooseother%(player,self.PlayerWolfState[player]+"【确认】"),self._getplayerfromchara("狼人")) #向其他狼人广播自己的选择
				ready_result = True #是否准备好结果
				for t_player in self._getplayerfromchara("狼人"):
					if self.PlayerWolfState[t_player].find("未确认")>0:
						ready_result = False #还有人等待确认
						return
				if ready_result==True:
					t_choice = dict.fromkeys(self.PlayerWolfState.values(),0)
					for t_player in self.PlayerWolfState:
						t_choice[self.PlayerWolfState[t_player]] += 1 #投票
					result_id = self.weighted_choice(list(t_choice.keys()))
					result_name = self.PlayerName[result_id]
					self._sendstr(self.strwords.strs_killwolf_final % str(t_choice),self._getplayerfromchara("狼人"))
					self._sendstr(self.strwords.strs_killwolf_finalresult % result_name,self._getplayerfromchara("狼人"))
					self.PlayerWolfChoose = result_name
					self._changestate(self._getplayerfromchara("狼人"),600) #恢复状态
					self._sendtoall(self.strwords.strs_closerecwolf) #狼人结束
					return self._nightstart5()
		elif state==605:
			if msg=="1":
				if self.PlayerWitchProtectTime>0:#救人剩余次数
					self.PlayerWitchProtect = self.PlayerWolfChoose
					self.PlayerWitchProtectTime += -1
					self._changestate(player,606) #进入下一环节
				else:
					self._sendtoall(self.strwords.strs_openwitch_fail) #向所有人公布救人失败
			elif msg=="2": #不救
				self._changestate(player,606) #进入下一环节
			else:
				return #其他字符
			self._sendtoall(self.strwords.strs_openwitch_poison) #向所有人提示是否杀人
			self._sendstr(self.strwords.strs_openwitch_choice % (self._getplayerfromstate(optionlist=True)),player) #询问女巫救人环节结束，等待女巫杀人回答
		elif state==606:
			if self._IsVaildResponse(msg,player,True)==False:
				return
			indexid = int(msg)
			if indexid == 0 :
				#不杀人
				pass
			else:
				if self.PlayerWitchKillTime<=0:
					self._sendtoall(self.strwords.strs_openwitch_fail) #向所有人公布女巫次数不足
				else:
					self.PlayerWitchKillTime += -1
					self.PlayerWitchKill = self.PlayerName[indexid]
			self._sendtoall(self.strwords.strs_closewitch,self._getplayerfromstate()) #女巫闭眼
			self._changestate(player,600) #女巫杀人阶段结束
			return self._dayinit() #开始白天
		elif state==607:
			isready = False
			notready = []
			for t_player in PlayerDayState: #未准备好的玩家
				if PlayerDayState[t_player] != '准备':
					notready.append(t_player)
			for exitmsg in self.strwords.strs_exitlist:
				if msg==exitmsg:
					self.PlayerDayState[player]='准备'
					isready = True
					if player in notready:
						notready.remove(player)
					self._sendtoall(self.strwords.strs_daytalkover % (str(player),str(notready))) #向所有玩家广告该玩家准备好了
			if isready == False:
				self._sendtoall("[ %s ] : %s" %(player,msg)) #转发玩家发言
			if notready == []:
				#所有人都准备好
				self._sendtoall(self.strwords.strs_dayvote % self._getplayerfromstate(optionlist = True))
				self._changestate(self._getplayerfromstate(),608)
			#玩家讨论结束
		elif state==608:
			if self._IsVaildResponse(msg,player)==False:
				self._sendtoall("[ %s ] : %s" %(player,msg)) #转发玩家发言
				return #非法投票
			else:
				indexid = int(msg)
				t_player = self.PlayerName[indexid]
				self.PlayerDayState[player] = t_player
				self._sendtoall(self.strwords.strs_dayvotedecide %(player,t_player))
			allvoted = True
			for t_player in self.PlayerDayState:
				if self.PlayerDayState[player]=='准备':
					#还没投票
					allvoted = False
			if allvoted ==True:
				maxchoice = []
				t_choice = dict.fromkeys(list(self.PlayerDayState.values()),0)
				for t_player in self.PlayerDayState:
					t_choice[self.PlayerDayState[t_player]] += 1
				for t_player in t_choice:
					if t_choice[t_player] == max(t_choice.values()):
						maxchoice.append(t_player)
				t_player = random.choice(maxchoice) #随机抽取最大投票的人
				self._sendtoall(self.strwords.daykill %(str(t_choice),t_player)) #向大家广播杀人结果
				result = self._killandcalc(t_player)
				if result=='狼胜':
					self._sendtoall(self.strwords.strs_gameover % "狼人")
					return result 
				elif result=='民胜':
					self._sendtoall(self.strwords.strs_gameover % "民胜")
					return result
				elif result=='情侣胜':
					self._sendtoall(self.strwords.strs_gameover % "情侣胜")
					return result
				elif result=='继续':
					self._nightinit()
		elif state==609:
			#观察者模式讨论转发
			self._sendstr("[观察者模式][%s] %s " % (player,msg),self._getplayerfromstate("死亡"))






class werewolfstrs(object):
	strs_gameover = '[法官]本局 % 胜！游戏结束！'
	strs_killtips = '[系统]你被杀死了。现在自动进入观察者模式'

	strs_daykill = '[法官]投票结果： %s 。本轮被驱逐出境的是： %s'
	strs_dayvotedecide = '[系统]玩家 %s 选择投死 %s'
	strs_dayvote = "[法官]发言环节结束。下面进行投票。请输入希望投死的玩家序号。玩家列表: %s"
	strs_daytalkover = "[系统] %s 已准备好投票。还没有准备好的玩家有： %s"
	strs_exitlist = ['退出','结束','准备好']
	strs_daynotice = '[系统]已开启白天讨论模式（不分顺序）。请在结束发言后回复“结束”或“退出”或“准备好”。所有玩家准备好后进入投票环节。系统将实时更新非机器人玩家的发言及发言状态。'
	strs_charayours = '[法官]您分配到的角色是：'

	strs_openrecwolf = '[法官]狼人请睁眼。'
	strs_openrecwolfappend = '[系统]本场剩余狼人为：'
	strs_killwolf_choose = '[法官]请选择杀一个人。玩家列表：%s'
	strs_killwolf_chooseother = '[系统]非机器人狼人【%s】的选择是： %s ，你的狼人队友更改选项后会自动告诉你。回复【确认】不再更改，回复其他数字改变选择。如果仍有歧义系统将按票数加权抽签。'
	strs_killwolf_final = '[系统]票数信息： %s'
	strs_killwolf_finalresult = '[系统]投票结果：经过加权平均，最终选择对象为 %s'
	strs_closerecwolf = '[法官]狼人请闭眼。'

	strs_openpredict = '[法官]预言家请睁眼，请预言你的对象'
	strs_predicting = '[法官]请选择一位玩家。玩家列表： %s'
	strs_predictok = '[系统] %s 的身份牌是 $s'
	strs_closepredict = '[法官]预言家请闭眼。'

	strs_opencupid = '[法官]丘比特请睁眼，连线情侣。'
	str_cupiding = '[系统]请选择你要连线的情侣。玩家列表：%s。（回复格式举例： 1-3 代表连接第1位和第3位玩家）'
	strs_closecupid = '[法官]连线完成，丘比特请闭眼。情侣相互指认结束。'

	strs_openwitch = '[法官]女巫请睁眼。今晚 %s '
	strs_openwitch_nodead = '没有死人。'
	strs_openwitch_dead = '死的人是 %s ，你要救他吗？'
	strs_openwitch_helpnotice = '回复【1】救他；【2】不救。'
	strs_openwitch_fail = '失败！您没有可用的次数。'
	strs_openwitch_poison = '[法官]女巫你要杀人吗？'
	strs_openwitch_choice = '[系统]请选择玩家，回复0不杀人。 玩家列表：%s'
	strs_closewitch = '[法官]女巫请闭眼'

	strs_defend_open = '[法官]守卫请睁眼。请守卫守护一个人。'
	strs_defending = '[系统]请选择守护一个玩家。 玩家列表： %s'
	strs_defend_over = '[法官]守卫请闭眼。'

	strs_nightpeave = '[法官]天亮了。奇怪，混入柯南的村庄竟然渡过了一个平安夜！ 下面将组织发言。'
	strs_nightover = '[法官]天亮了。一大早醒来，伟大的无产阶级战士 %s 永远地离开了我们， %s 将自动成为游荡在资本主义小村庄上空的幽灵，进入观察者模式。下面将组织发言。'
	strs_couple = '[系统]【您被选为情侣】本局游戏的情侣是： %s'

	strs_start = '[法官]天色越来越暗。终于，最后一丝残阳也渐渐消失，又一个晚上开始了。天黑，请闭眼。'

	settings_fakesleep = 3
	def __init__(self):
		self.settings_character = {}
		self.settings_charaintro = {}
		self.settings_character[8] = ['狼','狼','民','民','民','预言家','女巫','丘比特']
		self.settings_character[9] =  ['狼','狼','狼','民','民','民','预言家','女巫','丘比特']
		self.settings_character[10] = ['狼','狼','狼','民','民','民','民','预言家','女巫','丘比特']
		self.settings_character[11] = ['狼','狼','狼','狼','民','民','民','预言家','女巫','丘比特','守卫']
		self.settings_character[12] = ['狼','狼','狼','狼','民','民','民','民','预言家','女巫','丘比特','守卫']
		for i in self.settings_character:
			int_wolf = self.settings_character[i].count("狼")
			int_peo = self.settings_character[i].count("民")
			int_other = i - str_wolf - str_peo
			str_otherchara = " ".join(self.settings_character).replace("狼 ").replace("民 ")
			self.settings_charaintro[i] = "[法官] %d 个玩家的配置为： %d 位狼人， %d 位村民， %d 位神民。神民的角色为 %s" % (i,int_wolf,int_peo,int_other,str_otherchara)


class werewolfrobot(object):
