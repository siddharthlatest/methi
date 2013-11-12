import uuid
import os
import shutil
import sys
import Queue
import time
import ConfigParser
from time import gmtime, strftime
import urllib2
import urllib
import logging

from ThreadManagers import *
from FTPconnection import FTPconnection
import Common


class SyncClient:
	
	def initBuildParams(self):
		self.digestCheck = False
		#down disable option while app is running
		self.isDownDisabled = False
		self.isAppsOverridden = False
		self.appsOverride = ["allapps"]
		self.appsDir = {"allapps":["userAppDataRoot,appsdata"]}
		self.isOnlyWebApps = True


	def __init__(self,isAR, failNotify, changeIcon, analytics):
		self.isAppRunning = isAR
		self.name = "Main" #thread name
		self.failNotify = failNotify
		self.changeIcon = changeIcon
		self.initBuildParams()

		self.successState = True

		#setup logger
		self.logger = logging.getLogger("daemon.syncclient")

		try:
			#system paths
			self.appbinRoot = os.path.abspath("../")

			#Appbin data
			self.rdir_config = "../data"
			self.adir_config = Common.createPath(os.path.abspath(self.rdir_config))
			self.afile_configIni = "%s/config.ini" % self.adir_config
			self.afile_machineIni = "%s/machine.ini" % self.adir_config
			self.afile_dirsIni = "%s/appDirs.ini" % self.adir_config

			self.rdir_temp = self.rdir_config + "/temp"
			self.adir_temp = Common.createPath(os.path.abspath(self.rdir_temp))

			self.rdir_bin = "./bin"

			self.rdir_remote_temp = "current"
			self.rdir_remote_current = "current"
			self.rdir_remote_old = "old"
		except:
			self.failNotify()
			self.logger.exception("exception in creating synclient init")
			return

		#temporarily adding binaries to path
		os.environ['PATH'] = "%s;%s" % (os.getenv('PATH'), os.path.abspath(self.rdir_bin))

		#loading config file
		self.isConfigIniOk = self.loadConfig()
		#if self.isConfigIniOk and not self.isAppRunning:
		if self.isConfigIniOk:
			self.logger.info("begin sync")
			
			#Identifying User
			##Change this unknown to username read from config file IMPORTANT
			props = { "numOfApps":len(self.apps) }
			analytics.identify(self.username, self.full_name, properties=props)
			###
			
			netStatus = self.initQnThread()
			if(netStatus < 0):
				return
			self.syncNow()
			

		
			
	def initQnThread(self):
		#Queues
		self.Qs = []
		self.mainQ =  self.newQ()
		self.stateQ = self.newQ()
		self.isReadyToExit = False

		#Creating FTP connection
		#get cedentials from database
		server, password = self.getServerData(self.username)
		if(server=="error" and password=="error"):
			return -1
		self.conn = FTPconnection(server, self.username, password, self.failNotify)

		#objs of thread managers
		self.appT = AppThreadManager(self.mainQ,self)
		self.ftpT = FtpThreadManager(self.mainQ,self)
		self.hashT = HashThreadManager(self.mainQ,self)
		self.zipT = ZipThreadManager(self.mainQ,self)
		#app counter
		self.nTotalApps = len(self.apps)
		self.nAppsInProcess = 0
		return 1
			
	
	def loadConfig(self):
		try:
			if os.path.isfile(self.afile_configIni):
				isConfigIniOk = True
			else:
				isConfigIniOk = False
			
			if isConfigIniOk:
				self.cfg = ConfigParser.SafeConfigParser()
				self.cfg.read(self.afile_configIni)
				
				if self.cfg.has_option("main", "email") and self.cfg.has_option("main", "name") and  len(self.cfg.get("main", "email")) > 4  : # assuming email > 4 chars
					self.username = self.cfg.get("main", "email")
					self.full_name  = self.cfg.get("main", "name")
					self.logger.info("current user is %s, %s" %(self.full_name,self.username))
					self.userAppDataRoot= self.appbinRoot + "/data/" + self.username + "/appsdata"
				else:
					self.logger.warning("no username in config")
					isConfigIniOk = False
							
			else:
				self.logger.warning("ini not found")
			
			if isConfigIniOk:
				if not self.isAppsOverridden:
					self.apps = filter(None, self.cfg.get("main", "apps").split(";"))
				else:
					self.logger.info("overridden apps:"+str(self.appsOverride))
					self.apps = self.appsOverride

				#yashness chudap begins
				m = False
				cfgm = ConfigParser.SafeConfigParser()
				if os.path.isfile(self.afile_machineIni):
					m = True
					
					cfgm.read(self.afile_machineIni)
					if ((not cfgm.has_option("main", "machineId")) or cfgm.get("main", "machineId") == ""):
					#print("machine id not found in config"+ str(cfgm.has_option("main", "machineId"))+ str(cfgm.get("main", "machineId") == "") )
						m = False
					else:
						self.machineId = cfgm.get("main", "machineId")
				
				if not m:
					self.machineId = str(uuid.uuid1())
					cfgm.add_section("main")
					cfgm.set("main", "machineId", self.machineId)
					f = open(self.afile_machineIni, "wb")
					cfgm.write(f)
					f.close()
				#yashness chudap over
				
				"""if ((not self.cfg.has_option("main", "machineId")) or self.cfg.get("main", "machineId") == ""):
					print("machine id not found in config"+ str(self.cfg.has_option("main", "machineId"))+ str(self.cfg.get("main", "machineId") == "") )
					self.machineId = str(uuid.uuid1())
					self.cfg.set("main", "machineId", self.machineId)
					f = open(self.afile_configIni, "wb")
					self.cfg.write(f)
					f.close()
				else:
					self.machineId = self.cfg.get("main", "machineId")"""

			return isConfigIniOk

		except:
			self.failNotify()
			self.logger.exception("problem in loading config")
			return False
		

	def getServerData(self, username):
		try:
			upData = urllib.urlencode({"id":username},{"hash":"thisishash"})
			page = urllib2.urlopen("http://getappbin.com/loadapp/userdetails.php",upData)
			downData = page.read()
			data = downData.split(",")
			server = data[0]
			password = data[1]

			return server, password
		except:
			self.failNotify()
			self.logger.warning("getting data from server failed")
			return "error", "error"


	def newQ(self):
		q = Queue.Queue(0)
		self.Qs.append(q)
		return q

	def mainQueueParser(self):
		while True:
			msg = self.mainQ.get()
			#self.logger.info(msg)

			if Common.isExitMsg(msg):
				if self.successState:
					self.changeIcon("0")
				break
			self.newMsg(msg)

	def newMsg(self,m):
		thread = m[0]
		msg = m[1]
		payLoad = m[2]

		if thread == self.name:
			if msg == Common.startMsg:
				shutil.rmtree("../data/temp",True)
				for app in self.apps:
					self.nAppsInProcess += 1
					self.appT.addEntry(app,Common.newMsg)



		if thread == self.appT.name:

			if msg == Common.finishMsg:
				self.nAppsInProcess -= 1
				print "apps remaining", self.nAppsInProcess
				if not payLoad["isSuccessful"]:
					self.successState = False

				if self.nAppsInProcess ==0:
					self.prepareToExit()
				else:
					#notify app sync finish. show remaining apps
					pass

			elif msg == Common.newMsg:
				if self.isAppRunning and self.isDownDisabled and payLoad["appEntry"]["direction"] == "down":
					self.logger.info("Down disabled when nw active")
					payLoad["appEntry"]["isDownStopped"] = True
					self.appT.notifyDirFinish(payLoad)
				else:
					payLoad["zipDirection"] = "up"
					self.zipT.addEntry(payLoad)

		if thread == self.zipT.name:
			if msg == Common.finishMsg:
				if payLoad["zipDirection"] == "up":
					if(self.digestCheck):
						self.hashT.addEntry(payLoad)
					else:
						self.ftpT.addEntry(payLoad)
						
				elif payLoad["zipDirection"] == "down":
					self.appT.notifyDirFinish(payLoad)

		if thread == self.hashT.name:
			if msg == Common.finishMsg:
				if not payLoad["appEntry"]["appCfg"].has_section("Digest"):
					payLoad["appEntry"]["appCfg"].add_section("Digest")

				if (payLoad["appEntry"]["appCfg"].has_option("Digest", "Dir%d_Hash" % payLoad["dirIndex"])):
					orgDigest = payLoad["appEntry"]["appCfg"].get("Digest", "Dir%d_Hash" % payLoad["dirIndex"])
				else:
					orgDigest = ""

				payLoad["appEntry"]["appCfg"].set("Digest","Dir%d" % payLoad["dirIndex"], ",".join(payLoad["dir"]))
				payLoad["appEntry"]["appCfg"].set("Digest","Dir%d_Hash" % payLoad["dirIndex"] , payLoad["digest"])

				if orgDigest != payLoad["digest"]:
					payLoad["appEntry"]["isHashChanged"] = True
					self.logger.info("%s %d %s %s %s digest has changed" % (payLoad["appEntry"]["app"],payLoad["dirIndex"],payLoad["dir"],orgDigest,payLoad["digest"]) )
					self.ftpT.addEntry(payLoad)
				else:
					self.logger.info("%s %d %s %s %s digest has not changed" % (payLoad["appEntry"]["app"],payLoad["dirIndex"],payLoad["dir"],orgDigest,payLoad["digest"]) )
					self.appT.notifyDirFinish(payLoad)

		if thread == self.ftpT.name:

			if msg == Common.finishMsg:
				if payLoad["appEntry"]["direction"] == "up":
				    self.appT.notifyDirFinish(payLoad)
				else:
					payLoad["zipDirection"] = "down"
					self.zipT.addEntry(payLoad)

	def syncNow(self):
		
		self.mainQ.put([self.name,Common.startMsg,""])
		# start msg parsing
		self.logger.info("Sync started")
		self.mainQueueParser()
		self.logger.info("Sync finished")



	#fileSystem methods
	def dirToLocalPath(self,x):
		return (eval("self."+x[0])+"/"+x[1]).replace("\\","/")

	def prepareToExit(self):
		#self.isReadyToExit = True

		self.logger.info("Sync Over.")
		for q in self.Qs:
			q.put(Common.exitMsg)

