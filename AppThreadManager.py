import Common

class AppThreadManager:
	def __init__(self,mQ,mainObj):
		self.mainQ = mQ
		self.mainObj = mainObj

		#thread msg strings
		self.name = "App"

		self.appQ = Queue.Queue(0)
		#self.unZipQ = Queue.Queue(0)\

		t = threading.Thread(target=appThread)
		t.start()

	def appThread(self):
		while True:
			appEntry = appQ.get()
			app = appEntry["app"]
			msg = appEntry["msg"]
			if(msg == Common.newMsg):
				newApp(app)
			elif msg == Common.finishMsg:
				finishApp(app)
			else:
				#"Error"
				pass

	def afile_appIni(self,app):
		afile_appIni = "%s\\%s.ini" % mainObj.adir_appIni, app


	def newApp(app):
		direction, cfg = decideDirection(app)
		dirs ,cfg = self.getAppLocalDirs(app)
		n = len(dirs)
		for i in range(n-1,-1):
			x = dirs[i]
			dirEntry = {"app":app,"dir":x,"dirIndex":i,"direction":direction,"appCfg":cfg,"temp":adir_appTemp(app)}
			self.newDir(dirEntry)

	def finishApp(app):
		f = open(appIni, "wb")
		cfg.write(f)
		f.write()
		f.close()
		#upload appIni
		pass

	def newDir(dirEntry):
		self.mainQ.put(self.name,Common.newMsg,dirEntry)

	def getAppLocalDirs(self, app):
		cfg = ConfigParser.SafeConfigParser()
		cfg.read(mainObj.afile_dirsIni)

		paths = cfg.get(app, "paths").split(";")
		paths = [path.split(",") for path in paths if path != ""]

		return paths

	def dirToLocalPath(x):
		return (eval("self.mainObj"+x[0])+"\\"+x[1]).lower()

	def decideDirection(self, app):
		appIni = afile_appIni(app)
		self.getAppIni(app, appIni)

		if os.path.isfile(appIni ):
			cfg = ConfigParser.SafeConfigParser()
			cfg.read(appIni)

			if not cfg.has_section(mainObj.machineId):
				direction = "down"
			else:
				direction = cfg.get(mainObj.machineId, "nextSyncDirection")
				if direction == "up":
					sections = cfg.sections()
					for s in sections:
						cfg.set(s, "nextSyncDirection", "down")

		else:
			cfg = ConfigParser.SafeConfigParser()
			direction = "up"

		#finalizing machine data in appini
		time = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " GMT"
		cfg.set(mainObj.machineId, "lastSyncStartTime", time)
		cfg.set(mainObj.machineId, "lastSyncDirection", direction)
		cfg.set(mainObj.machineId, "nextSyncDirection", "up")

		#f = open(appIni, "wb")
		#cfg.write(f)
		#f.write()
		#f.close()

		return direction, cfg

	def getAppIni(self,app,appIni):
		filename = app + ".ini"
		mainObj.conn.download(filename, appIni, app)

	def adir_appTemp(self, app):
		return mainObj.adir_temp + "\\" + app


