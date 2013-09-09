import uuid
import os
import sys
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
		self.name = "Main" #thread name
		self.digestCheck = False

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

		self.rdir_temp = self.rdir_config + "/temp"
		self.adir_temp = self.createPath(os.path.abspath(self.rdir_temp))

		self.rdir_bin = "./bin"

		self.rdir_remote_temp = "inprocess"
		self.rdir_remote_current = "current"
		self.rdir_remote_old = "old"

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
			f.close()
		else:
			self.machineId = self.cfg.get("main", "machineId")

		#Queues
		self.Qs = []
		self.printQ = self.newQ()
		self.mainQ =  self.newQ()
		self.stateQ = self.newQ()
		self.isReadyToExit = False

		#Creating FTP connection
		#get cedentials from database
		self.conn = FTPconnection("192.3.29.173", "user1", "secret",self.printQ)
		#self.conn = FTPconnection("37.139.14.74", "chronomancer", "sachin",self.printQ)

		#objs of thread managers
		self.appT = AppThreadManager(self.mainQ,self)
		self.ftpT = FtpThreadManager(self.mainQ,self)
		self.hashT = HashThreadManager(self.mainQ,self)
		self.zipT = ZipThreadManager(self.mainQ,self)
		#app counter
		self.nTotalApps = len(self.apps)
		self.nAppsInProcess = 0

		#starting threads
		self.t = threading.Thread(target=self.printerThread)
		self.t.start()

	def newQ(self):
		q = Queue.Queue(0)
		self.Qs.append(q)
		return q

	def printerThread(self):
		while True:
			x = self.printQ.get()
			if Common.isExitMsg(x):
				break

			print
			print x

	def mainQueueParser(self):
		while True:
			msg = self.mainQ.get()
			self.printQ.put(msg)

			if Common.isExitMsg(msg):
				break
			self.newMsg(msg)

	def newMsg(self,m):
		thread = m[0]
		msg = m[1]
		payLoad = m[2]

		if thread == self.name:
			if msg == Common.startMsg:
				for app in self.apps:
					self.nAppsInProcess += 1
					self.appT.addEntry(app,Common.newMsg)



		if thread == self.appT.name:

			if msg == Common.finishMsg:
				self.nAppsInProcess -= 1

				if self.nAppsInProcess ==0:
					self.printQ.put("Sync Over.")
					self.prepareToExit()
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
				elif payLoad["zipDirection"] == "down":
					self.appT.notifyDirFinish(payLoad)

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

					if not (orgDigest  == payLoad["digest"] and self.digestCheck):
						self.ftpT.addEntry(payLoad)
					else:
						self.appT.notifyDirFinish(payLoad)

		if thread == self.ftpT.name:

			if msg == Common.finishMsg:
				if payLoad["appEntry"]["direction"] == "up":
				    self.appT.notifyDirFinish(payLoad)
				else:
					payLoad["zipDirection"] = "down"
					self.zipT.addEntry(payLoad)

	def sync(self):
		self.mainQ.put([self.name,Common.startMsg,""])

		# start msg parsing
		self.mainQueueParser()



	#fileSystem methods
	def dirToLocalPath(self,x):
		return (eval("self."+x[0])+"\\"+x[1]).lower()

	def prepareToExit(self):
		#self.isReadyToExit = True


		for q in self.Qs:
			q.put(Common.exitMsg)

		"""
        #assuming followig treads can be killed: Main, App , Ftp, Zip, Hash
		while True:


			if self.printQ.empty() and self.stateQ.empty() and self.mainQ.empty():
				self.appT
				os._exit(0)
			else:
				time.sleep(0.5)"""


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

