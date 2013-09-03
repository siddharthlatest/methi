import uuid
import os
import Queue
import threading
import time
import ConfigParser
from time import gmtime, strftime

from ThreadManagers import *
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
		self.adir_config = os.path.abspath(rdir_config)
		self.afile_configIni = "%s\\config.ini" % adir_config
		self.afile_dirsIni = "%s\\appDirs.ini" % adir_config

		self.rdir_appIni = rdir_config + "/apps"
		self.adir_appIni = os.path.abspath(rdir_appIni)

		self.rdir_temp = rdir_config + "/temp"
		self.adir_temp = os.path.abspath(rdir_temp)

		self.rdir_bin = "./bin"

		#temporarily adding binaries to path
		self.os.environ['PATH'] = "%s;%s" % os.getenv('PATH'), os.path.abspath(rdir_bin)

		#loading config file
		self.cfg = ConfigParser.SafeConfigParser()
		self.cfg.read(afile_configIni)

		#loading values from config file
		self.server = cfg.get("main", "syncServer")
		self.user = cfg.get("main", "name")
		self.pwd = cfg.get("main", "pwd")
		self.apps = filter(None, cfg.get("main", "apps").split(";"))
		if not cfg.has_option("main", "machineId"):
			machineId = str(uuid.uuid1())
			cfg.set("main", "machineId", machineId)
			f = open(afile_configIni, "wb")
			cfg.write(f)
			f.write()
			f.close()
		else:
			machineid = cfg.get("main", "machineId")

		#Queues
		self.printQ = Queue.Queue(0)
		self.mainQ =  Queue.Queue(0)

		#Creating FTP connection
		self.conn = FTPconnection("37.139.14.74", "chronomancer", "sachin")

		#objs of thread managers
		self.appT = AppThreadManager(mainQ,self)
		self.ftpT = FtpThreadManager(mainQ,self)
		self.hashT = HashThreadManager(mainQ)
		self.zipT = ZipThreadManager(mainQ)

		#app counter
		self.nTotalApps = len(self.apps)
		self.nAppsInProcess = 0


	def mainQueueParser(self):
		while True:
			msg = self.mainQ.get()
			newMsg(msg)

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
				zipT.addEntry(payLoad)

		if thread == self.zipT.name:
			if msg == Common.finishMsg:
				if payLoad["zipDirection"] == "up":
					hashT.addEntry(payLoad)
				else:
					finalizeAppIfRequired(payLoad)

		if thread == self.hashT.name:
			if msg == Common.finishMsg:
				if not payLoad["appEntry"]["appCfg"].has_section("Digest"):
					payLoad["appEntry"]["appCfg"].set("Digest","Dir%d" % payLoad["dirIndex"], ",".join(payLoad["dir"]))
					payLoad["appEntry"]["appCfg"].set("Digest","Dir%d_Hash" % payLoad["dirIndex"] , payLoad["digest"])
					ftpT.addEntry(payLoad)
				else:

					if not payLoad["appEntry"]["appCfg"].get("Digest", "Dir%d_Hash" % payLoad["dirIndex"]) == payLoad["digest"]:
						ftpT.addEntry(payLoad)
					else:
						finalizeAppIfRequired(payLoad)

		if thread == self.ftpT.name:

			if msg == Common.finishMsg:
				if payLoad["appEntry"]["direction"] == "up":
				    finalizeAppIfRequired(payLoad)
				else:
					payLoad["zipDirection"] == "down"
					zipT.addEntry(payLoad)


	def finalizeAppIfRequired(self,payLoad):
		if payLoad["dirIndex"] == 0:
			appT.addEntry(payLoad["appEntry"],Common.finalizeMsg)


	def sync(self):
		for app in self.apps:
			nAppsInProcess += 1
			appT.addEntry(app,Common.newMsg)

