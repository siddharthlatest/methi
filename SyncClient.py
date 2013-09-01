import uuid
import os
import subprocess
import sys
import Queue
import thread
import threading
import time
import ConfigParser
import tempfile
from time import gmtime, strftime

import FTPconnection

class SyncClient:

	def __init__(self):
		#Creating FTP connection
		conn = FTPconnection("37.139.14.74", "chronomancer", "password")

		#system paths
		userProfile = os.getenv("USERPROFILE")
		cDrive = "C:"
		programFiles86 = os.getenv("programfiles(x86)")
		programFiles = os.getenv("ProgramW6432")
		userAppDataDir = os.getenv("APPDATA")

		#Appbin data
		rdir_config = "./config"
		adir_config = os.path.abspath(rdir_config)
		afile_configIni = "%s/config.ini" % adir_config
		afile_dirsIni = "%s/appDirs.ini" % adir_config
		
		rdir_appIni = dir_config + "/apps"
		adir_appIni =  os.path.abspath(rdir_appIni)

		rdir_temp = rdir_config + "/temp"
		adir_temp = os.path.abspath(rdir_temp)

		rdir_bin = "./bin"

		#temporarily adding binaries to path
		os.environ['PATH'] = "%s;%s" % os.getenv('PATH'), os.path.abspath(rdir_bin)

		#loading config file
		cfg = ConfigParser.SafeConfigParser()
		cfg.read(afile_configIni)

		#loading values from config file
		server = cfg.get("main", "syncServer")
		user = cfg.get("main", "name")
		pwd = cfg.get("main", "pwd")
		apps = filter(None, cfg.get("main", "apps").split(";"))
		if not cfg.has_option("main", "machineId"):
			machineId = str(uuid.uuid1())
			cfg.set("main", "machineId", machineId)
			f = open(afile_configIni, "wb")
			cfg.write(f)
			f.write()
			f.close()
		else:
			machineid = cfg.get("main", "machineId")

		#counters
		nAppsTotalInSync = len(self.apps)
		nAppsInProcess = 0

		#starting required Queues for multithreading
		initQ = Queue.Queue(0)		
		printQ = Queue.Queue(0)

		zipQ = Queue.Queue(0)
		nZipThreads = 1
		
		ftpQ = Queue.Queue(0)
		nFtpThreads = 1

		hashQ = Queue.Queue(0)
		nHashThreads = 1

		#initiating variable for multithread control
		isAppQRunning = False
		isZipQRunning = False
		isPrintQRunning = False

	def getAppIni(self, app, afile_appIni):
		filename = app + ".ini"
		self.conn.download(filename, afile_appIni, app)

	def decideDirection(self, app):
		if not os.path.exists(self.adir_appIni):
			os.mkdir(os.path.abspath("./config/apps"))
		afile_appIni = "%s\\%s.ini" % self.adir_appIni, app

		getAppIni(app, afile_appIni)

		if os.path.isfile(afile_appIni):
			cfg = ConfigParser.SafeConfigParser()
			cfg.read(afile_appIni)

			if not cfg.has_section(machineId):
				direction = "down"
			else:
				direction = cfg.get(machineId, "nextSyncDirection")
				if direction == "up":
					sections = cfg.sections()
					for s in sections:
						cfg.set(s, "nextSyncDirection", "down")

		else:
			cfg = ConfigParser.SafeConfigParser()
			direction = "up"

		#finalizing machine data in appini
		time = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " GMT"
		cfg.set(machineId, "lastSyncStartTime", time)
		cfg.set(machineId, "lastSyncDirection", direction)
		cfg.set(machineId, "nextSyncDirection", "up")

		f = open(afile_appIni, "wb")
		cfg.write(f)
		f.write()
		f.close()

		return direction, cfg

	def getAppLocalDirs(self, app):
		cfg = ConfigParser.SafeConfigParser()
		cfg.read(afile_dirsIni)

		paths = cfg.get(app, "paths").split(";")
		paths = [path.split(",") for path in paths if path != ""]

		return paths

	def syncApp(self, app):
		printQ(app+" : Init Sync...")
		self.nAppsInProcess += 1
		direction, appCfg = self.decideDirection(app)
		printQ( app+" : Direction - "+direction)

		dirs = self.getAppLocalDirs(app)
		n = len(dirs)
		for i in range(n-1,-1):
			x = dirs[i]
			dirEntry = {"app":app,"dir":x,"dirI":dirI,"direction":direction,"appCfg":appCfg,"temp":adir_appTemp(app)}
			processDir(dirEntry)
			
	def adir_appTemp(app):
		return self.adir_temp + "\\" + app

	def processDir(dirEntry,command):
		dirEntry["zipDirection"] = "up"
		syncDirWithZip(dirEntry)

	def syncDirWithZip(dirEntry):
		adir_local = dirToLocalPath(dirEntry["dir"])
		azip_name = "dir%d.7z" % dirEntry["dirI"])
		azip_local = "%s\\%s" % dirEntry["temp"] , azip_name

		dirEntry["adir_local"] = adir_local
		dirEntry["azip_name"] = azip_name
		dirEntry["azip_local"] = azip_local

		if(dirEntry["zipDirection"] == "up"): #dir -> 7zip
			zipCmd = "7za a -t7z %s %s -mx3" % azip_local, adir_local
			dirEntry["zipCmd"] = zipCmd
			addToZipQ(dirEntry)
		else: # zip to dir
			zipCmd = "balh"
			dirEntry["zipCmd"] = zipCmd
			addToZipQ(dirEntry)
			pass

		def addToZipQ(dirEntry):
			self.zipQ.put(dirEntry)

			if not (self.isZipQRunning):
					self.isZipQRunning = True
					for i in range(self.nZipThreads):
						#thread.start_new_thread(newProcess,(i,))
						t = threading.Thread(target=zipThread)
						t.setDaemon(True)
						t.start()

			def zipThread():
				while not (self.zipQ.empty()):
					dirEntry = zipQ.get()
					subprocess.call(dirEntry["zipCmd"])
					zipFinish(dirEntry)

				self.isZipQRunning = False

			def zipFinish(dirEntry):
				if dirEntry["zipDirection"] == "up":
					hashDir(dirEntry)
				else:
					if dirEntry["dirI"] == 0: # this is the last directory of the app
						syncAppFinish(dirEntry)

	def hashDir(dirEntry):
		hashCmd = "blah blah"
		dirEntry["hashCmd"] = hashCmd
		addToZipQ(dirEntry)

		def addToHashQ(cmd):
			self.hashQ.put(dirEntry)

			if not (self.isHashQRunning):
					self.isHashQRunning = True
					for i in range(self.nHashThreads):
						#thread.start_new_thread(newProcess,(i,))
						t = threading.Thread(target=hashThread)
						t.setDaemon(True)
						t.start()

			def hashThread():
				while not (self.hashQ.empty()):
					dirEntry = hashQ.get()
					#do hash
					hash = "as" # hash of dirEntry["azip_local"]
					dirEntry["hash"] = hash
					hashFinish(dirEntry)

				self.isHashQRunning = False

			def hashFinish(dirEntry):
				syncZipWithRemote(dirEntry)

	def syncZipWithRemote(dirEntry):
		if not dirEntry["appCfg"].has_section("Hash"):
			dirEntry["appCfg"].set("Hash","Dir%d" % dirEntry["dirI"], ",".join(dirEntry["dir"]))
			dirEntry["appCfg"].set("Hash","Dir%d_Hash" % dirEntry["dirI"] , dirEntry["hash"])

		else:
			if not dirEntry["appCfg"].get("Hash", "Dir%d_Hash" % dirEntry["dirI"]) == dirEntry["hash"]
				if direction == "up":
					# upload dirEntry["azip_local"] to ftp://user@server/user/app/dirEntry["azip_name"]
				else:
					# download ftp://user@server/user/app/dirEntry["azip_name"] to  dirEntry["azip_local"]
					dirEntry["zipDirection"] = "down"
					syncDirWithZip(dirEntry)


	def dirToLocalPath(x):
    return (eval("self."+x[0])+"\\"+x[1]).lower()

	def newAppProcess(self):
		while not self.appQ.empty():
			app = appQ.get()
			syncApp(app)
		self.isAppQRunning = False

	def startAppQ(self):
		self.isAppQRunning = True
		for i in range(2):
			t = threading.Thread(target=newAppProcess)
			t.start()

	def sync(self):
		for app in self.apps:
			if self.isAppQRunning:
				self.appQ.put(app)
			else:
				self.appQ.put(app)
				self.startAppQ()