import core.settings
import time

def debug(strs,level = '默认'):
	DEBUGF = open(core.settings.debugname,'a')
	DEBUGF.write(str(time.ctime())+" ["+str(level)+"]: "+strs+"\n")
	print((str(time.ctime())+" ["+str(level)+"]: "+strs+"\n"))
	DEBUGF.close()