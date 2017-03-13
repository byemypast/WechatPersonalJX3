import requests
import re
class tiebagold(object):
	url = "http://m.tieba.com/m?kz=4968747832&pn=9999"
	maxthresload = 899
	minthresload = 501
	keywords = ['出']
	def __init__(self):
		pass
	def GetGold(self):
		r = requests.get(self.url).text
		p1 = re.compile('<div class="i">(.*?)<br/><table>')
		p2 = re.compile('<span class="b">(.*?)</span></td>')
		lp1 = p1.findall(r)
		maxprice = 0
		maxtime = ""
		lp2 = p2.findall(r)
		for index,msg in enumerate(lp1):
			l = msg.replace("<br/>",'').replace("&#160;",'')
			m = l.find('楼. ')
			if m>=0:
				l = l[m+len("楼. "):]
			isfind = False
			for key in self.keywords:
				if l.find(key)>=0:
					isfind = True
			if isfind == True:
				p3 = re.compile('\d+')
				prices = p3.findall(l)
				for price in prices:
					if int(price)<self.maxthresload and int(price)>self.minthresload:
						if int(price)>maxprice:
							maxprice = int(price)
							maxtime = lp2[index]
		return maxprice,maxtime
		
