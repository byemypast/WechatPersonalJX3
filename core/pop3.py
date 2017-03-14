#-*- encoding: utf-8 -*-
#-*- encoding: gbk -*-
import poplib
import base64
class POP3Receive(object):
	def __init__(self,host,username,pwd):
		self.host = host
		self.user = username
		self.pwd = pwd
		
		self.pop3 = poplib.POP3(host)
		self.pop3.user(username)
		self.pop3.pass_(pwd)
		ret = self.pop3.stat()
		print(ret)
		down = self.pop3.retr(1)
		strs = ""
		for index,line in enumerate(down[1]):
			if index>50:
				strs += line.decode('gbk')
		print(base64.b64decode(strs).decode('gbk'))

	def GetFirstMail(self):
		newestid = (self.imap.search(None,'ALL')[1][0].decode('utf-8').split(" ")[-1])
		resp,maildata = self.imap.fetch(str(newestid),"BODY[TEXT]")
		mailtext = maildata[0][1]
		print(mailtext)
		#msg = email.message_from_bytes(mailtext)
		#subject = email.header.decode_header(msg['Subject'])[0][0].decode('utf-8')
		#content = msg.get_payload(decode=True)
		#print(content)


m = POP3Receive("imap.sina.com","jx3trader@sina.com","pkucoe2016")