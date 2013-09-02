import uuid
import os
import Queue
import threading
import time
import ConfigParser
from time import gmtime, strftime

import FTPconnection
import DataManager

class SyncClient:

	def __init__(self):
		#system paths
		userProfile = os.getenv("USERPROFILE")
		cDrive = "C:"
		programFiles86 = os.getenv("programfiles(x86)")
		programFiles = os.getenv("ProgramW6432")
		userAppDataDir = os.getenv("APPDATA")

		#Appbin data
		rdir_config = "./config"
		adir_config = os.path.abspath(rdir_config)
		afile_configIni = "%s\\config.ini" % adir_config
		afile_dirsIni = "%s\\appDirs.ini" % adir_config

		rdir_appIni = rdir_config + "/apps"
		adir_appIni = os.path.abspath(rdir_appIni)

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

		#starting required Queues for multithreading
		initQ = Queue.Queue(0)		
		printQ = Queue.Queue(0)

		#initiating variable for multithread control
		isAppQRunning = False
		isPrintQRunning = False

		#Number of threads
		initThreads = 4

		#Creating FTP connection
		conn = FTPconnection("37.139.14.74", "chronomancer", "password")

		#Creating Data Manager
		dataManager = DataManager(conn)

	def getAppIni(self, app, afile_appIni):
		filename = app + ".ini"
		self.conn.download(filename, afile_appIni, app)

	def decideDirection(self, app):
		if not os.path.exists(self.adir_appIni):
			os.mkdir(os.path.abspath("./config/apps"))
		afile_appIni = "%s\\%s.ini" % self.adir_appIni, app

		self.getAppIni(app, afile_appIni)

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

	def adir_appTemp(self, app):
		return self.adir_temp + "\\" + app

	def dirToLocalPath(x):
    	return (eval("self."+x[0])+"\\"+x[1]).lower()

	def processDir(self, dirEntry, command):
		dirEntry["zipDirection"] = command
		dirEntry["dir"] = self.dirToLocalPath(dirEntry["dir"])
		self.DataManager.syncDirWithZip(dirEntry)

	def syncApp(self, app):
		printQ(app+" : Init Sync...")
		self.nAppsInProcess += 1
		direction, appCfg = self.decideDirection(app)
		printQ( app+" : Direction - "+direction)

		dirs = self.getAppLocalDirs(app)
		n = len(dirs)
		for i in range(n-1,-1):
			x = dirs[i]
			dirEntry = {"app":app,"dir":x,"dirIndex":i,"direction":direction,"appCfg":appCfg,"temp":adir_appTemp(app)}
			processDir(dirEntry, direction)

	def syncZipWithRemote(dirEntry):
		if not dirEntry["appCfg"].has_section("Hash"):
			dirEntry["appCfg"].set("Hash","Dir%d" % dirEntry["dirIndex"], ",".join(dirEntry["dir"]))
			dirEntry["appCfg"].set("Hash","Dir%d_Hash" % dirEntry["dirIndex"] , dirEntry["hash"])

		else:
			if not dirEntry["appCfg"].get("Hash", "Dir%d_Hash" % dirEntry["dirIndex"]) == dirEntry["hash"]
				if direction == "up":
					# upload dirEntry["azip_local"] to ftp://user@server/user/app/dirEntry["azip_name"]
				else:
					# download ftp://user@server/user/app/dirEntry["azip_name"] to  dirEntry["azip_local"]
					dirEntry["zipDirection"] = "down"
					syncDirWithZip(dirEntry)

	def newAppProcess(self):
		while not self.appQ.empty():
			app = appQ.get()
			syncApp(app)
		self.isAppQRunning = False

	def startAppQ(self):
		self.isAppQRunning = True
		for i in range(iniThreads):
			t = threading.Thread(target=newAppProcess)
			t.start()

	def sync(self):
		for app in self.apps:
			if self.isAppQRunning:
				self.appQ.put(app)
			else:
				self.appQ.put(app)
				self.startAppQ()