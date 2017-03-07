# -*- coding:utf8 -*-  
import re
import urllib.request
import time
import datetime


class Get_5173Info:
	url = "http://s.5173.com/jx3-5ootfk-1bk5qc-jjvp1o-0-kb0ewi-0-0-0-a-a-a-a-a-0-itemprice_asc-0-0.shtml" #纵月
	html = ""
	
	def __init__(self, url = ""):
		if url != "":
			self.url = url
	def __Get5173Html(self):
		response = urllib.request.urlopen(self.url)
		page = response.read()
		self.html = page.decode('gbk')
	def GetInfoNow(self):
		self.__Get5173Html()
		pattern = re.compile("1元=(.*?)<")
		pattern2 = re.compile('<li class="pr"><strong>(.*?)<')
		lgoldprice = pattern.findall(self.html)
		ltotal = pattern2.findall(self.html)
		return lgoldprice,ltotal
	def GetMaxPriceNow(self):
		lgoldprice,ltotal = self.GetInfoNow()
		return float(lgoldprice[0])
		
	def GetAveragePriceNow(self, load = 1000):
		lgoldprice,ltotal = self.GetInfoNow()
		sum = 0
		i = 0
		totalprice = 0
		while (sum<=load):
			if sum+float(ltotal[i])>load:
				totalprice += (load-sum) * float(lgoldprice[i])
			else:
				totalprice += float(ltotal[i]) * float(lgoldprice[i])
			sum += float(ltotal[i])
			i += 1
		return totalprice/load
	'''
class Drawing_5173Info:
	pricedatas = []
	xdate = []
	lines = []
	data = None
	fig = None
	Savedata = True
	filename = "SavePrice.tab"
	fileobj = None
	
	def erase(self):
		self.pricedatas=[[],[]]
		self.xdate=[]
	
	def __init__(self,data,aprice=[],mprice=[],xdate=[]):
		self.pricedatas.append(aprice)
		self.pricedatas.append(mprice)
		self.xdate = xdate
		self.data = data
		self.fig = plt.figure()
		self.updatedata()
		self.__Initfig()
		
		
	def Save(self,timenow,apnow,mpnow):
		self.fileobj = open(self.filename,'a')
		self.fileobj.write(time.ctime()+"\t"+str(apnow)+"\t"+str(mpnow)+"\n")
		self.fileobj.close() #save on time
		
	def updatedata(self):
		aprice = self.data.GetAveragePriceNow()
		mprice = self.data.GetMaxPriceNow()
		timenow = time.strftime('%H-%M-%S')
		if self.Savedata == True:
			self.Save(timenow,aprice,mprice)
		self.pricedatas[0].append(aprice)
		self.pricedatas[1].append(mprice)
		self.xdate.append(timenow)

	def __Initfig(self):

		#self.fig.autoscale(True,'both',None)
		#self.fig.rc('axes',grid = True)
		#self.fig.plot(range(len(date)),self.aprice)
		#self.fig.plot(range(len(date)),self.mprice)
		##self.fig.xlabel('Time')
		#self.fig.xticks(range(len(date)), date, rotation=45)
		#self.fig.ylabel('Price')

		self.lines.append(plt.plot(range(len(self.xdate)),self.pricedatas[0],'rx-',label='AveragePrice')[0])
		self.lines.append(plt.plot(range(len(self.xdate)),self.pricedatas[1],'b+-',label='MaxPrice')[0])
		
		plt.grid(True)
		plt.xlabel('Time')
		plt.ylabel('Price')
		plt.xticks(range(len(self.xdate)), self.xdate, rotation=45)
		plt.autoscale(True,'both',None)
		
	def updatefig(self,index):
		self.lines[index].set_data(range(len(self.xdate)),self.pricedatas[index])
		print(time.ctime(),self.xdate)
		plt.autoscale(True,'both',None)
		plt.xticks(range(len(self.xdate)), self.xdate, rotation=45)
		plt.autoscale(True,'both',None)
		return self.lines[index]
	
	def show(self):
		plt.show()

#FuncAnimation should not be setted in the Object		
def updatefigs(frame,drawingobject):
	drawingobject.updatedata()
	
	return [drawingobject.updatefig(0),drawingobject.updatefig(1)]
'''
'''
data = Get_5173Info()
TICK = 3600 #隔多久清空面板并保存一次(s)
STICK = 60 #隔多久监控金价(s)
stimepast = 0
timepast = 0
while (1):
	if (time.time()-timepast)>TICK:
		print(time.ctime()+" : Starting Stage-Save")
		if timepast!=0:
			oldtime = time.strftime("%H-%M-%S",time.gmtime(timepast))
			nowtime = time.strftime("%H-%M-%S",time.gmtime(time.time()))
			plt.savefig(oldtime+"to"+nowtime+".png")
			draw.erase()
		else:
			draw = Drawing_5173Info(data)
		timepast = time.time()
	if (time.time()-stimepast)>STICK:
		draw.updatedata()
		draw.updatefig(0)
		draw.updatefig(1)
		stimepast = time.time()
	time.sleep(1)
'''