import pyhash
import Common.Common

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

	def addEntry(self,obj,msg):
		if not isinstance(obj,dict):
			obj = {"app":app,"temp":adir_appTemp(app),"appIni":afile_appIni(app)}
		self.appQ.put(obj,msg)


	def appThread(self):
		while True:
			x = appQ.get()
			appEntry = x[0]
			msg = x[1]
			if(msg == Common.newMsg):
				newApp(appEntry)
			elif msg == Common.finalizeMsg:
				finalizeApp(appEntry)
			else:
				#"Error"
				pass

	def afile_appIni(self,app):
		afile_appIni = "%s\\%s.ini" % mainObj.adir_appIni, app

	def newApp(appEntry):
		app = appEntry["app"]
		appEntry["direction"], appEntry["appCfg"] = decideDirection(app)

		dirs = self.getAppLocalDirs(app)
		n = len(dirs)
		for i in range(n-1,-1):
			x = dirs[i]
			dirEntry = {"appEntry":appEntry,"dir":x,"dirIndex":i}
			self.newDir(dirEntry)

	def finalizeApp(appEntry):
		f = open(appEntry["appIni"], "wb")
		appEntry["appCfg"].write(f)
		f.write()
		f.close()

		#upload appIni
		#ftp move inProcess to main folder

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

	def decideDirection(self, appEntry):
		appIni = appEntry["appIni"]
		self.getAppIni(appEntry)

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

		return direction,cfg

	def getAppIni(self,appEntry):
		filename = appEntry["app"] + ".ini"
		mainObj.conn.download(filename, appIni, appEntry["appIni"])

	def adir_appTemp(self, app):
		return mainObj.adir_temp + "\\" + app

	def onFinishApp(appEntry):
		self.mainQ.put([self.name,Common.finishMsg,appEntry])


class ZipThreadManager:

	def __init__(self,mQ):
		self.mainQ = mQ

		#thread msg strings
		self.name = "Zipper"

		self.zipQ = Queue.Queue(0)
		#self.unZipQ = Queue.Queue(0)\

		t = threading.Thread(target=zipperThread)
		t.start()


	def addEntry(dirEntry):
		adir_local = dirEntry["dir"]
		azip_name = "dir%d.7z" % dirEntry["dirIndex"]
		azip_local = "%s\\%s" % dirEntry["appEntry"]["temp"] , azip_name

		dirEntry["adir_local"] = adir_local
		dirEntry["azip_name"] = azip_name
		dirEntry["azip_local"] = azip_local

		if(dirEntry["zipDirection"] == "up"): #dir -> 7zip
			zipCmd = "7za a -t7z %s %s -mx3" % azip_local, adir_local
			dirEntry["zipCmd"] = zipCmd
		else:
			zipCmd = "7za e %s -o%s" % azip_local, adir_local
			dirEntry["zipCmd"] = zipCmd

		self.zipQ.put(dirEntry)

	def zipperThread():
		while True:
			dirEntry = zipQ.get()
			subprocess.call(dirEntry["zipCmd"])
			onFinishEntry(dirEntry)

	def onFinishEntry(dirEntry):
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])








class HashThreadManager:

	def __init__(self,mQ):
		self.mainQ = mQ

		#Creating hasher
		self.hasher = pyhash.murmur3_32()

        #thread msg strings
		self.name = "Hasher"

		self.hashQ = Queue.Queue(0)

		t = threading.Thread(target=hashThread)
		t.start()

	def addEntry(self,dirEntry):
		self.hashQ.put(dirEntry)

	def hashThread(self):
		while True:
			dirEntry = hashQ.get()
			f = open(dirEntry["azip_local"],"r")
			dirEntry["digest"] = str(hasher(f.read()))
			f.close()
			onFinishEntry(dirEntry)

	def onFinishEntry(self,dirEntry):
		mQ.put([self.name,Common.finishMsg,dirEntry])









class FtpThreadManager:
	def __init__(self,mQ,mObj):
		self.mainQ = mQ
		self.mainObj = mObj

		#thread msg strings
		self.name = "Ftp"

		self.ftpQ = Queue.Queue(0)

		t = threading.Thread(target=zipperThread)
		t.start()

	def addEntry(dirEntry):
		self.ftpQ.put(dirEntry)

	def ftpThread():
		while True:
			dirEntry = zipQ.get()
			dirEntry["adir_remote"] = "%s/inProcess" % dirEntry["appEntry"]["app"]
			if (dirEntry["appEntry"]["direction"] == "up"):
				#upload dirEntry[""]
				self.mainObj.conn.uploadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])
			else:
				self.mainObj.conn.downloadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])
			onFinishEntry(dirEntry)

	def uploadZip(self,dirEntry):
		dirEntry["adir_remote"] = "%s/%s" % dirEntry["appEntry"]["app"],"inprocess"
		self.mainObj.conn.uploadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])

	def onFinishEntry(self,dirEntry):
		mQ.put([self.name,Common.finishMsg,dirEntry])
