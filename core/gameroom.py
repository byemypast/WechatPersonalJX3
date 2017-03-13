import itchat
from core.debug import debug
class gameroomhelper(object):
	'''游戏房间管理号'''
	def __init__(self):
		self.TotalRoom = 0
		self.RoomNameList = []
		self.RoomList = {}
	def NewRoom(self,name,attrib):
		if name in self.RoomList:
			return -1
		self.RoomNameList.append(name)
		self.TotalRoom += 1
		self.RoomList[name] = gameroom(name,attrib)
		return self.RoomList[name]
	def DelRoom(self,name):
		if (not(name in self.RoomList)):
			return -1
		self.TotalRoom += -1
		self.RoomList.pop(name)
		self.RoomNameList.remove(name)
		return 1

		

class gameroom(object):
	strwelcome = "欢迎 %s 来到房间 %s。当前房间玩家人数： %s，玩家列表： %s"
	strovermax = "对不起，本房间超过了最大人数！"
	strroominfo = "【%s】 房名： %s, ( %s / %s )"
	strleave =  "%s 离开了房间。"
	def sendstr(self,msg,player):
		itchat.send_msg(msg,self.PlayerID[player])
		debug("发送信息到 %s : %s" %(player,msg))
	def sendtoall(self,msg):
		for player in self.PlayerName:
			self.sendstr(msg,player)
	def __init__(self,name,attrib):
		'''name:房间名；attrib:字典 属性game:进入哪个游戏/maxpeople:几人间'''
		self.roomname = name
		self.roommax = attrib[maxpeople]
		self.roomgame = attrib[game]
		self.PlayerName = []
		self.PlayerID = {}
	def PlayerAddIn(self,player,playerid):
		if len(self.PlayerName)<self.roommax:
			self.PlayerName.append(player)
			self.PlayerID[player] = playerid
			self.sendtoall(self.strwelcome %(player,self.roomname,len(self.PlayerName),str(self.PlayerName)))
			return 1
		else:
			itchat.send_msg(self.strovermax,playerid)
			return -1
	def GetRoomInfo(self):
		return self.strroominfo % (self.roomgame,self.roomname,len(self.PlayerName),self.roommax)
	def GetRoomEnterInfo(self):
		'''返回playername与playerid两个进入游戏的关键信息'''
		return self.PlayerName,self.PlayerID
	def PlayerLeave(self,player):
		if (not(player in self.PlayerName)):
			return -1 #用户不在该房间
		else:
			self.PlayerName.remove(player)
			self.PlayerID.pop(player)
			self.sendtoall(strleave % player)
