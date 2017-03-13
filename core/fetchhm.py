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
			r = requests.get(self.url % skillname)
			p = re.compile('<img class="wx-share" src="(.*?)" alt')
			p2 = re.compile('<span class="font-106">(.*?)</span>')
			p3 = re.compile('<span class="font-100">(.*?)</span>')
			p4 = re.compile('<div class="line">(.*?)</div>')
			icon = p.findall(r.text)
			iconimg = BytesIO(requests.get(icon[0]).content)
			iconobj = Image.open(iconimg)
			describe_1 = p2.findall(r.text)
			describe_2 = p3.findall(r.text)
			return iconobj,list(zip(describe_1,describe_2))
		except Exception as err:
			debug("获取技能信息错误！信息："+str(err),'错误')
			return None,None