import imaplib
import email.header
class imapgame(object):
	def __init__(self,host,username,pwd):
		self.host = host
		self.user = username
		self.pwd = pwd
		
		self.imap = imaplib.IMAP4(host)
		self.imap.login(username,pwd)
		self.imap.select()
	def GetFirstMail(self):
		newestid = (self.imap.search(None,'ALL')[1][0].decode('utf-8').split(" ")[-1])
		resp,maildata = self.imap.fetch(str(newestid),"(RFC822)")
		mailtext = maildata[0][1]
		msg = email.message_from_bytes(mailtext)
		subject = email.header.decode_header(msg['Subject'])[0][0].decode('utf-8')
		content = msg.get_payload(decode=True)
		print(content)


m = imapgame("imap.sina.com","jx3trader@sina.com","pkucoe2016")
m.GetFirstMail()