import uuid
import os
import Queue
import threading
import time
import ConfigParser
from time import gmtime, strftime

import FTPconnection
import AppThreadManager
import FtpThreadManager
import HashThreadManager
import ZipThreadManager

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
		printQ = Queue.Queue(0)
		mainQ =  Queue.Queue(0)

		#Creating FTP connection
		conn = FTPconnection("37.139.14.74", "chronomancer", "password")

		#objs of thread managers
		appT = AppThreadManager(mainQ,self)
		ftpT = FtpThreadManager(mainQ,self)
		hashT = HashThreadManager(mainQ)
		zipT = ZipThreadManager(mainQ)



	def sync(self):
		for app in self.apps:
				self.appQ.put(app)

