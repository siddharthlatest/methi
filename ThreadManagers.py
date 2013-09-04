import os
import pyhash
import Common
import Queue
import threading
import time
import ConfigParser
from time import gmtime, strftime
import Common
import subprocess

class AppThreadManager:
	def __init__(self,mQ,mainObj):
		self.mainQ = mQ
		self.mainObj = mainObj
		self.printQ = mainObj.printQ

		#thread msg strings
		self.name = "App"

		self.appQ = Queue.Queue(0)
		#self.unZipQ = Queue.Queue(0)\

		t = threading.Thread(target=self.appThread)
		t.start()

	def addEntry(self,obj,msg):

		self.printQ.put("%s %s %s"%(self.name,obj,msg))
		if not isinstance(obj,dict):
			obj = {"app":obj,"temp": self.mainObj.createPath(self.adir_appTemp(obj)),"appIni":self.afile_appIni(obj)}

		#self.printQ.put(obj)
		self.appQ.put([obj,msg])

	def appThread(self):
		while True:
			x = self.appQ.get()
			appEntry = x[0]
			msg = x[1]
			if(msg == Common.newMsg):
				self.newApp(appEntry)
			elif msg == Common.finalizeMsg:
				self.finalizeApp(appEntry)
			else:
				#"Error"
				pass

	def afile_appIni(self,app):
		return "%s\\%s.ini" % (self.mainObj.adir_appIni, app)

	def newApp(self,appEntry):
		app = appEntry["app"]
		appEntry["direction"], appEntry["appCfg"] = self.decideDirection(appEntry)

		dirs = self.getAppLocalDirs(app)
		n = len(dirs)
		for i in range(n-1,-1,-1):
			x = dirs[i]
			self.printQ.put("Dir "+ str(x))
			dirEntry = {"appEntry":appEntry,"dir":x,"dirIndex":i}
			self.newDir(dirEntry)

	def finalizeApp(self,appEntry):
		f = open(appEntry["appIni"], "wb")
		appEntry["appCfg"].write(f)
		f.close()
		conn = self.mainObj.conn
		conn.uploadFile(appEntry["app"], appEntry["appIni"], "%s/%s" % (appEntry["app"], self.mainObj.rdir_remote_temp))
		self.onFinishApp(appEntry)

	def newDir(self,dirEntry):
		self.mainQ.put([self.name,Common.newMsg,dirEntry])

	def getAppLocalDirs(self, app):
		cfg = ConfigParser.SafeConfigParser()
		cfg.read(self.mainObj.afile_dirsIni)

		paths = cfg.get(app, "paths").split(";")
		paths = [path.split(",") for path in paths if path != ""]

		return paths

	def decideDirection(self, appEntry):

		appIni = appEntry["appIni"]
		self.printQ.put("ini "+appIni)

		self.getAppIni(appEntry)

		if os.path.isfile(appIni):
			cfg = ConfigParser.SafeConfigParser()
			cfg.read(appIni)

			if not cfg.has_section(self.mainObj.machineId):
				direction = "down"
				cfg.add_section(self.mainObj.machineId)
			else:
				direction = cfg.get(self.mainObj.machineId, "nextSyncDirection")
				if direction == "up":
					sections = cfg.sections()
					for s in sections:
						cfg.set(s, "nextSyncDirection", "down")

		else:
			cfg = ConfigParser.SafeConfigParser()
			cfg.add_section(self.mainObj.machineId)
			direction = "up"

		#finalizing machine data in appini
		time = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " GMT"
		cfg.set(self.mainObj.machineId, "lastSyncStartTime", time)
		cfg.set(self.mainObj.machineId, "lastSyncDirection", direction)
		cfg.set(self.mainObj.machineId, "nextSyncDirection", "up")

		return direction,cfg

	def getAppIni(self,appEntry):
		filename = appEntry["app"] + ".ini"
		self.mainObj.conn.download(filename,appEntry["appIni"],appEntry["app"])

	def adir_appTemp(self, app):
		return self.mainObj.adir_temp + "\\" + app

	def onFinishApp(self,appEntry):
		self.mainQ.put([self.name,Common.finishMsg,appEntry])


class ZipThreadManager:

	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.mainObj = mO
		self.printQ = mO.printQ

		#thread msg strings
		self.name = "Zipper"

		self.zipQ = Queue.Queue(0)
		#self.unZipQ = Queue.Queue(0)\

		t = threading.Thread(target=self.zipperThread)
		t.start()


	def addEntry(self,dirEntry):
		#self.printQ.put("%s %s" % (self.name,dirEntry))
		adir_local = self.mainObj.dirToLocalPath(dirEntry["dir"])
		azip_name = "dir%d.7z" % dirEntry["dirIndex"]
		azip_local = "%s\\%s" % (dirEntry["appEntry"]["temp"] , azip_name)

		dirEntry["adir_local"] = adir_local
		dirEntry["azip_name"] = azip_name
		dirEntry["azip_local"] = azip_local

		if(dirEntry["zipDirection"] == "up"): #dir -> 7zip
			zipCmd = "7za a -t7z \"%s\" \"%s\" -mx3" % (azip_local, adir_local)
			dirEntry["zipCmd"] = zipCmd
		else:
			zipCmd = "7za x \"%s\" -o\"%s\"" % (azip_local, adir_local)
			dirEntry["zipCmd"] = zipCmd

		self.printQ.put("%s"%zipCmd)
		self.zipQ.put(dirEntry)

	def zipperThread(self):
		while True:
			dirEntry = self.zipQ.get()
			subprocess.call(dirEntry["zipCmd"])
			self.onFinishEntry(dirEntry)

	def onFinishEntry(self,dirEntry):
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])








class HashThreadManager:

	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.printQ = mO.printQ
		self.mainObj = mO

		#Creating hasher
		self.hasher = pyhash.murmur3_32()
		#self.hasher = pyhash.fnv1a_32()

        #thread msg strings
		self.name = "Hasher"
		self.hashQ = Queue.Queue(0)

		t = threading.Thread(target=self.hashThread)
		t.start()

	def addEntry(self,dirEntry):
		self.printQ.put("%s %s" % (self.name,dirEntry))
		self.hashQ.put(dirEntry)

	def hashThread(self):
		while True:
			dirEntry = self.hashQ.get()
			f = open(dirEntry["azip_local"],"r")
			dirEntry["digest"] = str(self.hasher(f.read()))
			f.close()
			self.onFinishEntry(dirEntry)

	def onFinishEntry(self,dirEntry):
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])









class FtpThreadManager:
	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.mainObj = mO
		self.printQ = mO.printQ

		#thread msg strings
		self.name = "Ftp"

		self.ftpQ = Queue.Queue(0)

		t = threading.Thread(target=self.ftpThread)
		t.start()

	def addEntry(self,dirEntry):
		self.printQ.put("%s %s" % (self.name,dirEntry))
		self.ftpQ.put(dirEntry)

	def ftpThread(self):
		while True:
			dirEntry = self.ftpQ.get()
			dirEntry["adir_remote"] = "%s/%s" % (dirEntry["appEntry"]["app"], mainObj.rdir_remote_temp)
			if (dirEntry["appEntry"]["direction"] == "up"):
				self.mainObj.conn.uploadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])
			else:
				self.mainObj.conn.downloadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])
			self.onFinishEntry(dirEntry)

	def uploadZip(self,dirEntry):
		dirEntry["adir_remote"] = "%s/%s" % (dirEntry["appEntry"]["app"],mainObj.rdir_remote_temp)
		self.mainObj.conn.uploadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])

	def onFinishEntry(self,dirEntry):
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])
