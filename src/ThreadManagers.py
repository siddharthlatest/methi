import shutil
import os
import platform
import Common
import Queue
import threading
import ConfigParser
from time import gmtime, strftime,sleep
import Common
import subprocess
from subprocess import Popen
import logging
import socket
from SimpleXMLRPCServer import SimpleXMLRPCServer
import datetime
import json
if Common.isWindows :
	import win32gui
	import win32process

import urllib2
import urllib

class AppRunnerThreadManager:
	
	def __init__(self, analytics):
		self.name = "AppRunner"
		self.logger = logging.getLogger("daemon.apprunner")
		self.t = threading.Thread(target=self.appRunnerThread, args=(analytics,))
		self.t.start()
		
		
	def appRunnerThread(self, analytics):
		self.logger = logging.getLogger("daemon.apprunner")
		
		class rpcExposed:
			def newApp(self, appArgsJson):
				self.logger = logging.getLogger("daemon.apprunner")
				
				appArgs = json.loads(json.dumps(appArgsJson))
				#print "Calling: ", appArgs
				
				self.logger.info("App opened:" + appArgs["app"])
				appArgs["cmd"] = "./" + appArgs["cmd"]
				t = threading.Thread(target=newAppThread, args=(appArgs,))
				t.start()
				return  "called :%s" % appArgs["app"]
			def hello(self):
				return  "hello"
				
			def nwRpcPortRegister(self,port):
				Common.nwRpc.setPort(port)
				return "nw rpc port registered:" ,port
			
			def syncNow(self):
				Common.syncNow(True)
				return "synced or registered for sync"

		def appFinish(app):
			Common.appsRunning.remove(app)
			Common.appsToSync.append(app)
			self.logger.info("App closed. Appending to syncList: "+app)
			#Tracking Code
			analytics.track(event="App closed", properties={"appName":app})
			###
			self.logger.info("App closed:" + app)
			self.logger.info("calling sync")
			Common.syncNow(True)
			
		def handleWindow(appprocess):
			sleep(4)
			foreground = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]

			for hwnd in Common.get_hwnds_for_pid (appprocess.pid):
				wanted = win32process.GetWindowThreadProcessId(hwnd)[0]
				if not foreground == wanted:
					win32process.AttachThreadInput(foreground, wanted, True);
					win32gui.BringWindowToTop(hwnd)
					win32gui.ShowWindow(hwnd, 5)
					win32gui.SetActiveWindow(hwnd)
					win32process.AttachThreadInput(foreground, wanted, False);
				else:
					win32gui.BringWindowToTop(hwnd)
					win32gui.ShowWindow(hwnd, 5)
					win32gui.SetActiveWindow(hwnd)
			
				
		def newAppThread(appArgs):
			
			self.logger.info("App args:"+str(appArgs))
			
			Common.appsRunning.append(appArgs["app"])
			#Tracking Code
			analytics.track(event="App opened", properties={"appName":appArgs["app"]})
			###
			if (appArgs["isOnline"]):
				appprocess = Popen([appArgs["cmd"],appArgs["appPath"],appArgs["url"],appArgs["title"],appArgs["dataPath"],"--no-toolbar"])
				
			else:
				appprocess = Popen([appArgs["cmd"],appArgs["appPath"],appArgs["dataPath"],"--no-toolbar"])
				
			
			if Common.isWindows:
				handleWindow(appprocess)
				
			appprocess.wait()
			appFinish(appArgs["app"])
		
		port = 65000
		while True:	
			try:
				s = SimpleXMLRPCServer(("localhost", port))
				s.register_introspection_functions()
				s.register_instance(rpcExposed())
				break
			
			except socket.error:
				self.logger.info("RPC server:tryin port:" + str(port))
				port = port+1
				
		f = open('../data/pipe', 'w')
		f.write(str(port))
		f.close()
		
		
		self.logger.info("starting rpc server on:" +str(port))
		
		s.serve_forever()
		

class UpdateThreadManager:
	def __init__(self,version,pN):
		self.name = "Updater"
		self.ver = version
		self.processName = pN
		self.logger = logging.getLogger("daemon.update")
		
		self.t = threading.Thread(target=self.updateThread)
		self.t.start()
		
	def updateThread(self):
		upData = urllib.urlencode({"hash":"thisishash", "os":platform.system(),"arch":platform.machine()})
		sleepTime = 5*60
		while True:
			try:
				self.logger.info("Checking for update...")
				page = urllib2.urlopen("http://getappbin.com/loadapp/version.php",upData)
				downData = page.read()
				self.logger.info("data returned - "+str(downData))
				data = downData.split(",")
				onlineVersion = float(data[0])
				downloadLink = data[1]
				if onlineVersion > self.ver:
					self.logger.info(self.name+": update found.")
					page = urllib2.urlopen(downloadLink)
					updateData = page.read()
					with open("../data/update.exe","wb") as f:
						f.write(updateData)
					while True:
						if not Common.isProcessRunning(self.processName):
							#wait appbin_nw to exit
							break
		
						self.logger.info("waiting for appbin to close...")
						sleep(30)
					
					self.logger.info("updating - killing daemon...")
					if Common.isLinux :
						subprocess.call(["pkill", "appbin_7za"])
						subprocess.call(["pkill", "appbin_nw"])
						subprocess.call(["chmod","777","../data/update.exe"])
						subprocess.Popen(["../data/update.exe", "&"])
					elif Common.isMac:
						subprocess.call(["killall","-9", "appbin_7za"])
						subprocess.call(["killall","-9", "appbin_nw"])
						subprocess.call(["chmod","777","../data/update.exe"])
						subprocess.Popen(["../data/update.exe", "&"])
					elif Common.isWindows:
						subprocess.call("cmd /c \"taskkill /F /T /IM appbin_7za.exe\"")
						subprocess.call("cmd /c \"taskkill /F /T /IM appbin_nw.exe\"")
						subprocess.Popen("../data/update.exe /SILENT")
					os._exit(0)
		
				self.logger.info(self.name+": None found")
				sleep(sleepTime)
			except:
				self.logger.exception("error in updater")
				return
	

class AppThreadManager:
	def __init__(self,mQ,mainObj):
		self.mainQ = mQ
		self.mainObj = mainObj
		self.logger = logging.getLogger("daemon.syncclient.app")
		self.failNotify = mainObj.failNotify
		self.noOfThreads = 20

		#thread msg strings
		self.name = "App"

		self.appQ = self.mainObj.newQ()
		#self.unZipQ = self.mainObj.newQ()
		
		for i in xrange(self.noOfThreads):
			self.t = threading.Thread(target=self.appThread,args=(i,))
			self.t.start()

	def notifyDirFinish(self,dirEntry):
		try:
			if dirEntry.has_key("azip_local"):
				try:
					os.remove(dirEntry["azip_local"])
				except:
					pass
			
			dirEntry["appEntry"]["nRemainDirs"] -= 1
			if dirEntry["appEntry"]["nRemainDirs"] == 0:
				self.logger.info(dirEntry["appEntry"]["app"]+": Dirs Finished:")
				self.addEntry(dirEntry["appEntry"],Common.finalizeMsg)
			
			
		except:
			dirEntry["appEntry"]["isSuccessful"] = False
			self.logger.exception("problem in notifyDirFinish")
			return

	def addEntry(self,obj,msg):
		try:
			if not isinstance(obj,dict):
				obj = {"app":obj,"temp": Common.createPath(self.adir_appTemp(obj))}
				obj["appIni"] = "%s/app.ini" % obj["temp"]
				obj["isSuccessful"] = True
				obj["isActuallySynced"] = True
			self.appQ.put([obj,msg])
		except:
			self.logger.exception("error in addEntry:"+str((obj, msg)))
			return

	def appThread(self,tN):
		while True:
			x = self.appQ.get()
			if Common.isExitMsg(x):
				self.appQ.put(x) #for other running threads
				return
			appEntry = x[0]
			msg = x[1]
			self.logger.info("tN:"+str(tN)+" Q popped:"+appEntry["app"]+" "+msg+"; lenQ:"+str(self.appQ.qsize()))
			if(msg == Common.newMsg):
				self.newApp(appEntry)
			elif msg == Common.finalizeMsg:
				self.finalizeApp(appEntry)
			else:
				self.logger.warning("wrong message received in appThread")
				continue

	def newApp(self,appEntry):
		app = appEntry["app"]
		
		if app in Common.appsRunning:
			self.onFinishApp(appEntry)
			return
		
		if self.mainObj.isAppsOverridden:
			dirs = self.mainObj.appsDir[appEntry["app"]]
			dirs = [dir.split(",") for dir in dirs if dir != ""]
			
		elif self.mainObj.isOnlyWebApps:
			dirs = [["userAppDataRoot",appEntry["app"]]]
		
		else:
			dirs = self.getAppLocalDirs(appEntry)
			
			
		appEntry["direction"], appEntry["appCfg"] = self.decideDirection(appEntry)
		#TODO: if sync direction == null
		
		self.logger.info(appEntry["app"]+" direction:"+appEntry["direction"])
		
		if appEntry["direction"] == "up":
			if (app not in Common.appsToSync):
				appEntry["isActuallySynced"] = False
				self.onFinishApp(appEntry)
				return
			else:
				Common.appsToSync = [i for i in Common.appsToSync if i != app]
				self.logger.info("Filtered: "+ appEntry["app"] +". syncList: "+str(Common.appsToSync))
				
		
		Common.nwRpc.showSyncing(app)
		
		appEntry["nRemainDirs"] = len(dirs)
		appEntry["isHashChanged"] = True
		appEntry["isDownStopped"] = False

		n = len(dirs)
		for i in range(n-1,-1,-1):
			x = dirs[i]
			dirEntry = {"appEntry":appEntry,"dir":x,"dirIndex":i}
			self.newDir(dirEntry)

	def finalizeApp(self,appEntry):
		self.logger.info(appEntry["app"]+": Finalizing..")
		try:
			f = open(appEntry["appIni"], "wb")
			appEntry["appCfg"].write(f)
			f.close()
			conn = self.mainObj.conn
			if (appEntry["isHashChanged"] or appEntry["direction"] == "down") and (not appEntry["isDownStopped"]) and appEntry["isSuccessful"]:
				self.logger.info(appEntry["app"]+": Uploading Ini..")
				isNetOpSuccessful = conn.uploadFile("app.ini", appEntry["appIni"], "%s/%s" % (appEntry["app"], self.mainObj.rdir_remote_temp),checkDir=False)
				if isNetOpSuccessful > 0:
					pass
				else:
					appEntry["isActuallySynced"] = False
					appEntry["isSuccessful"] = False
				self.logger.info(appEntry["app"] + " ini uploaded")
			else:
				appEntry["isActuallySynced"] = False
				self.logger.info(appEntry["app"] + " ini not uploaded")


			"""
			ftp = conn.login()
			conn.delete_dir_nologin(ftp,self.mainObj.rdir_remote_old, appEntry["app"])
			conn.rename_nologin(ftp,self.mainObj.rdir_remote_current,self.mainObj.rdir_remote_old, appEntry["app"])
			conn.rename_nologin(ftp,self.mainObj.rdir_remote_temp, self.mainObj.rdir_remote_current, appEntry["app"])
			conn.delete_dir_nologin(ftp,self.mainObj.rdir_remote_old, appEntry["app"])
			conn.logout(ftp)
			"""

			"""
			conn.delete_dir(self.mainObj.rdir_remote_old, appEntry["app"])
			conn.rename(self.mainObj.rdir_remote_current,self.mainObj.rdir_remote_old, appEntry["app"])
			conn.rename(self.mainObj.rdir_remote_temp, self.mainObj.rdir_remote_current, appEntry["app"])
			conn.delete_dir(self.mainObj.rdir_remote_old, appEntry["app"])
			"""
			
		except:
			appEntry["isSuccessful"] = False
			self.logger.exception("error in finalizeApp")
			return
			
		try:
			os.remove(appEntry["appIni"])
		except:
			pass
		
		self.onFinishApp(appEntry)

	def newDir(self,dirEntry):
		self.mainQ.put([self.name,Common.newMsg,dirEntry])

	def getAppLocalDirs(self, appEntry):
		try:
			cfg = ConfigParser.SafeConfigParser()
			cfg.read(self.mainObj.afile_dirsIni)

			lockTimeOut = int(cfg.get(appEntry["app"], "lockTimeOut"))
			appEntry["lockTimeOut"] = lockTimeOut
			paths = cfg.get(appEntry["app"], "paths").split(";")
			paths = [path.split(",") for path in paths if path != ""]

			return paths
		except:
			dirEntry["appEntry"]["isSuccessful"] = False
			self.logger.exception("error in getting app directories")
			return

	def decideDirection(self, appEntry):
		try:
			appIni = appEntry["appIni"]

			self.getAppIni(appEntry)
			
			if os.path.isfile(appIni) and os.path.getsize(appIni) > 0:
				cfg = ConfigParser.SafeConfigParser()
				cfg.read(appIni)

				if not cfg.has_section(self.mainObj.machineId):
					direction = "down"
					cfg.add_section(self.mainObj.machineId)
				else:
					direction = cfg.get(self.mainObj.machineId, "nextSyncDirection")
					if direction == "up":
						sections = cfg.sections()
						if(self.mainObj.digestCheck):
							sections.remove("Digest")
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
		except:
			appEntry["isSuccessful"] = False
			self.logger.exception("error in deciding sync direction")
			return

	def getAppIni(self,appEntry):
		filename = "app.ini"
		isNetOpSuccessful = self.mainObj.conn.downloadFile(filename,appEntry["appIni"],"%s/%s" % (appEntry["app"], self.mainObj.rdir_remote_current),False)
		if isNetOpSuccessful > 0:
			pass
		else:
			pass

	def adir_appTemp(self, app):
		return self.mainObj.adir_temp + "/" + app

	def onFinishApp(self,appEntry):
		self.logger.info(appEntry["app"] + " end. Success:"+str(appEntry["isSuccessful"]))
		
		if (not appEntry["isSuccessful"]) :
			if appEntry["direction"] == "up":
				Common.appsToSync.append(appEntry["app"])
				self.logger.info("Appending to syncList: "+appEntry["app"])
		elif  appEntry["app"] not in Common.appsRunning :
			Common.nwRpc.showInSync(appEntry["app"])
		
		self.mainQ.put([self.name,Common.finishMsg,appEntry])


class ZipThreadManager:

	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.mainObj = mO
		self.logger = logging.getLogger("daemon.syncclient.zip")
		self.failNotify = mO.failNotify
		self.noOfThreads = 6

		#thread msg strings
		self.name = "Zipper"

		self.zipQ = self.mainObj.newQ()
		#self.unZipQ = self.mainObj.newQ()

		for i in xrange(self.noOfThreads):
			self.t = threading.Thread(target=self.zipperThread)
			self.t.start()


	def addEntry(self,dirEntry):
		adir_local = self.mainObj.dirToLocalPath(dirEntry["dir"])
		azip_name = "dir%d.7z" % dirEntry["dirIndex"]
		azip_local = "%s/%s" % (dirEntry["appEntry"]["temp"] , azip_name)
		
		
		
		dirEntry["adir_local"] = adir_local
		dirEntry["azip_name"] = azip_name
		dirEntry["azip_local"] = azip_local

		if Common.isMac or Common.isLinux:
			zip_exe = "bin/appbin_7za"
		elif Common.isWindows:
			zip_exe = "appbin_7za"

		if(dirEntry["zipDirection"] == "up"): #dir -> 7zip
			if Common.isLinux or Common.isMac:
				zipCmd = "%s a -t7z %s %s/* -mx3" % (zip_exe, azip_local, adir_local)
			elif Common.isWindows:
				zipCmd = "%s a -t7z \"%s\" \"%s\\*\" -mx3" % (zip_exe, azip_local.replace("/","\\"), adir_local.replace("/","\\"))
			dirEntry["zipCmd"] = zipCmd
		else:
			
			if Common.isLinux or Common.isMac:
				zipCmd = "%s x -y %s -o%s -mmt=on" % (zip_exe, azip_local, adir_local)
			elif Common.isWindows:
				zipCmd = "%s x -y \"%s\" -o\"%s\" -mmt=on" % (zip_exe, azip_local.replace("/","\\"), adir_local.replace("/","\\"))
			dirEntry["zipCmd"] = zipCmd

		self.zipQ.put(dirEntry)

	def zipperThread(self):
		while True:
			try:
				x = self.zipQ.get()
				if Common.isExitMsg(x):
					self.zipQ.put(x) #for other running threads
					return

				dirEntry = x
				
				if(not( (not self.mainObj.digestCheck) and dirEntry["zipDirection"] == "up" and dirEntry["appEntry"]["direction"] == "down") ):
					#enable below lines when sync is done per app
					if dirEntry["zipDirection"] == "down":
						shutil.rmtree(dirEntry["adir_local"],True) # delete target first
					
					if Common.isLinux or Common.isMac:
						exe = dirEntry["zipCmd"].split(" ")
						subprocess.call(exe)
					elif Common.isWindows:
						startupinfo = subprocess.STARTUPINFO()
						startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
						startupinfo.wShowWindow = subprocess.SW_HIDE
						subprocess.call(dirEntry["zipCmd"],startupinfo=startupinfo )
					self.logger.info(dirEntry["zipCmd"] + " excuted")
					
				
				
			except:
				self.logger.exception("compression or decompression error")
				continue
			
			self.onFinishEntry(dirEntry)
			

	def onFinishEntry(self,dirEntry):
		self.logger.info("%s %d %s zip finish" % (dirEntry["appEntry"]["app"], dirEntry["dirIndex"], dirEntry["dir"]) )
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])








class HashThreadManager:

	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.mainObj = mO
		self.logger = logging.getLogger("daemon.syncclient.hash")
		self.failNotify = mO.failNotify
		self.noOfThreads = 4

		#Creating hasher
		#self.hasher = murmur3_32()

		#thread msg strings
		self.name = "Hasher"
		self.hashQ = self.mainObj.newQ()
		
		for i in xrange(self.noOfThreads):
			self.t = threading.Thread(target=self.hashThread)
			self.t.start()

	def addEntry(self,dirEntry):
		self.hashQ.put(dirEntry)

	def hashThread(self):
		while True:
			try:
				x = self.hashQ.get()
				if Common.isExitMsg(x):
					self.hashQ.put(x) #for other running threads
					return
				dirEntry = x
				#hasher = hashlib.md5()
				f = open(dirEntry["azip_local"],"r")
				#hasher.update(f.read())
				#dirEntry["digest"] = str(self.hasher(f.read()))
				dirEntry["digest"] = ''
				f.close()
				self.onFinishEntry(dirEntry)
			except:
				dirEntry["appEntry"]["isSuccessful"] = False
				self.logger.exception("hashing error")
				continue

	def onFinishEntry(self,dirEntry):
		self.logger.info("%s %d %s hash finish" % (dirEntry["appEntry"]["app"], dirEntry["dirIndex"], dirEntry["dir"]) )
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])









class FtpThreadManager:
	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.mainObj = mO
		self.logger = logging.getLogger("daemon.syncclient.ftp")
		self.failNotify = mO.failNotify
		self.noOfThreads = 8

		#thread msg strings
		self.name = "Ftp"

		self.ftpQ = self.mainObj.newQ()

		for i in xrange(self.noOfThreads):
			self.t = threading.Thread(target=self.ftpThread)
			self.t.start()

	def addEntry(self,dirEntry):
		self.ftpQ.put(dirEntry)

	def ftpThread(self):
		while True:
			x = self.ftpQ.get()
			if Common.isExitMsg(x):
				self.ftpQ.put(x) #for other running threads
				return
			dirEntry = x
			if (dirEntry["appEntry"]["direction"] == "up"):
				dirEntry["adir_remote"] = "%s/%s" % (dirEntry["appEntry"]["app"], self.mainObj.rdir_remote_temp)
				isNetOpSuccessful = self.mainObj.conn.uploadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])
			else:
				dirEntry["adir_remote"] = "%s/%s" % (dirEntry["appEntry"]["app"], self.mainObj.rdir_remote_current)
				isNetOpSuccessful = self.mainObj.conn.downloadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])
			if isNetOpSuccessful > 0:
				pass
			else:
				dirEntry["appEntry"]["isSuccessful"] = False
			self.onFinishEntry(dirEntry)

	def onFinishEntry(self,dirEntry):
		self.logger.info("%s %d %s network operation finish" % (dirEntry["appEntry"]["app"], dirEntry["dirIndex"], dirEntry["dir"]) )
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])
