import uuid
import os
import Queue
import threading
import time
import ConfigParser
from time import gmtime, strftime
from ThreadManagers import *
from FTPconnection import FTPconnection
import Common


class SyncClient:

	def __init__(self):
		#system paths
		self.userProfile = os.getenv("USERPROFILE")
		self.cDrive = "C:"
		self.programFiles86 = os.getenv("programfiles(x86)")
		self.programFiles = os.getenv("ProgramW6432")
		self.userAppDataDir = os.getenv("APPDATA")

		#Appbin data
		self.rdir_config = "./config"
		self.adir_config = os.path.abspath(self.rdir_config)
		self.afile_configIni = "%s\\config.ini" % self.adir_config
		self.afile_dirsIni = "%s\\appDirs.ini" % self.adir_config

		self.rdir_appIni = self.rdir_config + "/apps"
		self.adir_appIni = self.createPath(os.path.abspath(self.rdir_appIni))

		self.rdir_temp = self.rdir_config + "/temp"
		self.adir_temp = self.createPath(os.path.abspath(self.rdir_temp))

		self.rdir_bin = "./bin"

		#temporarily adding binaries to path
		os.environ['PATH'] = "%s;%s" % (os.getenv('PATH'), os.path.abspath(self.rdir_bin))

		#loading config file
		self.cfg = ConfigParser.SafeConfigParser()
		self.cfg.read(self.afile_configIni)

		#loading values from config file
		self.server = self.cfg.get("main", "syncServer")
		self.user = self.cfg.get("main", "name")
		self.pwd = self.cfg.get("main", "pwd")
		self.apps = filter(None, self.cfg.get("main", "apps").split(";"))
		if not self.cfg.has_option("main", "machineId"):
			self.machineId = str(uuid.uuid1())
			self.cfg.set("main", "machineId", self.machineId)
			f = open(self.afile_configIni, "wb")
			self.cfg.write(f)
			#f.write()
			f.close()
		else:
			self.machineId = self.cfg.get("main", "machineId")

		#Queues
		self.printQ = Queue.Queue(0)
		self.mainQ =  Queue.Queue(0)

		#Creating FTP connection
		self.conn = FTPconnection("37.139.14.74", "chronomancer", "sachin",self.printQ)

		#objs of thread managers
		self.appT = AppThreadManager(self.mainQ,self)
		self.ftpT = FtpThreadManager(self.mainQ,self)
		self.hashT = HashThreadManager(self.mainQ,self)
		self.zipT = ZipThreadManager(self.mainQ,self)

		#app counter
		self.nTotalApps = len(self.apps)
		self.nAppsInProcess = 0

		#starting threads
		t = threading.Thread(target=self.printerThread)
		t.start()

		t = threading.Thread(target=self.mainQueueParser)
		t.start()

	def printerThread(self):
		while True:
			print
			print self.printQ.get()

	def mainQueueParser(self):
		while True:
			msg = self.mainQ.get()
			self.printQ.put(msg)
			self.newMsg(msg)

	def newMsg(self,m):
		thread = m[0]
		msg = m[1]
		payLoad = m[2]
		if thread == self.appT.name:

			if msg == Common.finishMsg:
				self.nAppsInProcess -= 1

				if self.nAppsInProcess ==0:
					#notify sync over
					#exit()
					pass
				else:
					#notify app sync finish. show remaining apps
					pass

			elif msg == Common.newMsg:
				payLoad["zipDirection"] = "up"
				self.zipT.addEntry(payLoad)

		if thread == self.zipT.name:
			if msg == Common.finishMsg:
				if payLoad["zipDirection"] == "up":
					self.hashT.addEntry(payLoad)
				else:
					self.finalizeAppIfRequired(payLoad)

		if thread == self.hashT.name:
			if msg == Common.finishMsg:
				if not payLoad["appEntry"]["appCfg"].has_section("Digest"):
					payLoad["appEntry"]["appCfg"].add_section("Digest")
					payLoad["appEntry"]["appCfg"].set("Digest","Dir%d" % payLoad["dirIndex"], ",".join(payLoad["dir"]))
					payLoad["appEntry"]["appCfg"].set("Digest","Dir%d_Hash" % payLoad["dirIndex"] , payLoad["digest"])
					self.ftpT.addEntry(payLoad)
				else:
					if (payLoad["appEntry"]["appCfg"].has_option("Digest", "Dir%d_Hash" % payLoad["dirIndex"])):
						orgDigest = payLoad["appEntry"]["appCfg"].get("Digest", "Dir%d_Hash" % payLoad["dirIndex"])
					else:
						orgDigest = ""

					payLoad["appEntry"]["appCfg"].set("Digest","Dir%d" % payLoad["dirIndex"], ",".join(payLoad["dir"]))
					payLoad["appEntry"]["appCfg"].set("Digest","Dir%d_Hash" % payLoad["dirIndex"] , payLoad["digest"])

					if not orgDigest  == payLoad["digest"]:
						self.ftpT.addEntry(payLoad)
					else:
						self.finalizeAppIfRequired(payLoad)

		if thread == self.ftpT.name:

			if msg == Common.finishMsg:
				if payLoad["appEntry"]["direction"] == "up":
				    self.finalizeAppIfRequired(payLoad)
				else:
					payLoad["zipDirection"] == "down"
					self.zipT.addEntry(payLoad)


	def finalizeAppIfRequired(self,payLoad):
		if payLoad["dirIndex"] == 0:
			self.appT.addEntry(payLoad["appEntry"],Common.finalizeMsg)

	def sync(self):
		for app in self.apps:
			self.nAppsInProcess += 1
			self.appT.addEntry(app,Common.newMsg)


	#fileSystem methods
	def dirToLocalPath(self,x):
		return (eval("self."+x[0])+"\\"+x[1]).lower()

	def createPath(self,x):
		if x == "":
			return x
		y = x
		while y[-1] == "\\":
			y = y[:-1]
		if not os.access(y, os.F_OK):
			self.createPath(y[:y.rfind("\\")])
			os.mkdir(y)

		return x

