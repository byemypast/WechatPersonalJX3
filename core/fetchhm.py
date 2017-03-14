# -*- coding: utf-8 -*-
import requests
import re
from PIL import Image
from io import BytesIO
from core.debug import debug
class GetHMInfo(object):
	url = "https://haimanchajian.com/data/jx3/search?table=skill&q=%s&refresh=yes"
	def __init__(self):
		pass
	def GetSkill(self,skillname):
		try:	
			returnlist = []
			r = requests.get(self.url % skillname)
			p = re.compile('<img class="wx-share" src="(.*?)" alt') #icon
			p2 = re.compile('<span class="font-106">(.*?)</span>') #距离等
			p3 = re.compile('<span class="font-100">(.*?)</span>') #具体描述
			p4 = re.compile('<span class="font-31">(.*?)</span>') #技能名称
			icon = p.findall(r.text)
			iconimg = BytesIO(requests.get(icon[0]).content)
			iconobj = Image.open(iconimg)
			describe_1 = p2.findall(r.text)
			describe_2 = p3.findall(r.text)
			skillnames = p4.findall(r.text)
			for index,name in enumerate(skillnames):
				if name == skillname:
					returnlist.append((describe_1[index],describe_2[index]))
				else:
					print(name,skillname)
			return iconobj,returnlist
		except Exception as err:
			debug("获取技能信息错误！信息："+str(err),'错误')
			return None,None