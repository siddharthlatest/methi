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
if not platform.system() == "Linux":
	import win32gui
	import win32process

import urllib2
import urllib

class AppRunnerThreadManager:
	def __init__(self,version,pN,msgToUthread, analytics):
		self.name = "AppRunner"
		self.ver = version
		self.processName = pN
		self.logger = logging.getLogger("daemon.apprunner")
		self.msgThread = msgToUthread
		
		self.t = threading.Thread(target=self.appRunnerThread, args=(analytics,))
		self.t.start()
		
		
	def appRunnerThread(self, analytics):
		class rpcExposed:
			def newApp(self, appArgsJson):
				appArgs = json.loads(json.dumps(appArgsJson))
				#print "Calling: ", appArgs
				appArgs["cmd"] = "./" + appArgs["cmd"]
				t = threading.Thread(target=newAppThread, args=(appArgs,))
				t.start()
				return  "called :%s" % appArgs["app"]
			def hello(self):
				return  "hello"

		def appFinish(app):
			Common.appsRunning.remove(app)
			Common.appsToSync.append(app)
			#Tracking Code
			analytics.track(event="app closed", properties={"appName":app})
			###
			print "Finished app:%s" % app
			
		def handleWindow(appprocess):
			sleep(4)
			foreground = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]

			for hwnd in Common.get_hwnds_for_pid (appprocess.pid):
				wanted = win32process.GetWindowThreadProcessId(hwnd)[0]
				print foreground,wanted
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
			print appArgs
			Common.appsRunning.append(appArgs["app"])
			#Tracking Code
			analytics.track(event="app opened", properties={"appName":appArgs["app"]})
			###
			if (appArgs["isOnline"]):
				appprocess = Popen([appArgs["cmd"],appArgs["appPath"],appArgs["url"],appArgs["title"],appArgs["dataPath"],"--no-toolbar"])
				if platform.system()=="Linux":
					pass
				else:
					handleWindow(appprocess)
				appprocess.wait()
				
			else:
				appprocess = Popen([appArgs["cmd"],appArgs["appPath"],appArgs["dataPath"],"--no-toolbar"])
				if platform.system()=="Linux":
					pass
				else:
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
				port = port+1
				
		f = open('../data/pipe', 'w')
		f.write(str(port))
		f.close()
		
		print "starting rpc server on:%d" % port
		s.serve_forever()
		

class UpdateThreadManager:
	def __init__(self,version,pN,msgToUthread):
		self.name = "Updater"
		self.ver = version
		self.processName = pN
		self.logger = logging.getLogger("daemon.update")
		self.msgThread = msgToUthread
		
		self.t = threading.Thread(target=self.updateThread)
		self.t.start()
		
	def updateThread(self):
		upData = urllib.urlencode({"hash":"thisishash", "os":platform.system(),"arch":platform.machine()})
		
		while True:
			try:
				if not self.msgThread.empty():
					return
				self.logger.info(self.name+": Checking for update...")
				page = urllib2.urlopen("http://getappbin.com/loadapp/version.php",upData)
				downData = page.read()
				self.logger.info(self.name+": data returned - "+str(downData))
				data = downData.split(",")
				onlineVersion = float(data[0])
				downloadLink = data[1]
				if onlineVersion > self.ver:
					print "update found"
					self.logger.info(self.name+": update found.")
					page = urllib2.urlopen(downloadLink)
					updateData = page.read()
					with open("../data/update.exe","wb") as f:
						f.write(updateData)
					while True:
						if not Common.isProcessRunning(self.processName):
							#wait for sync threads to complete
							break
		
						self.logger.info(self.name+": waiting for appbin to close...")
						sleep(30)
					
					print self.name+": updating - killing daemon..."
					if platform.system()=='Linux':
						subprocess.call(["pkill", "appbin_7za"])
						subprocess.call(["pkill", "appbin_nw"])
						subprocess.call(["chmod","777","../data/update.exe"])
						subprocess.Popen(["../data/update.exe", "&"])
					else:
						subprocess.call("cmd /c \"taskkill /F /T /IM appbin_7za.exe\"")
						subprocess.call("cmd /c \"taskkill /F /T /IM appbin_nw.exe\"")
						subprocess.Popen("../data/update.exe /SILENT")
					os._exit(0)
		
				self.logger.info(self.name+": None found")
				for i in range(0,720):
					if not self.msgThread.empty():
						return
					sleep(5)
			except:
				self.logger.exception("error in updater")
				return
	

class AppThreadManager:
	def __init__(self,mQ,mainObj):
		self.mainQ = mQ
		self.mainObj = mainObj
		self.logger = logging.getLogger("daemon.syncclient.app")
		self.failNotify = mainObj.failNotify

		#thread msg strings
		self.name = "App"

		self.appQ = self.mainObj.newQ()
		#self.unZipQ = self.mainObj.newQ()
		
		for i in xrange(6):
			self.t = threading.Thread(target=self.appThread)
			self.t.start()

	def notifyDirFinish(self,dirEntry):
		try:
			if dirEntry.has_key("azip_local"):
				os.remove(dirEntry["azip_local"])
			
			dirEntry["appEntry"]["nRemainDirs"] -= 1
			if dirEntry["appEntry"]["nRemainDirs"] == 0:
				self.finalizeApp(dirEntry["appEntry"])
		except:
			dirEntry["appEntry"]["isSuccessful"] = False
			self.logger.exception("problem in notifyDirFinish")
			return

	def addEntry(self,obj,msg):
		print obj, msg
		try:
			if not isinstance(obj,dict):
				self.logger.info(obj + " started")
				obj = {"app":obj,"temp": Common.createPath(self.adir_appTemp(obj))}
				obj["appIni"] = "%s/app.ini" % obj["temp"]
				obj["isSuccessful"] = True
			
			self.logger.info("putting")
			self.appQ.put([obj,msg])
		except:
			self.logger.exception("error in addEntry")
			return

	def appThread(self):
		while True:
			x = self.appQ.get()
			if Common.isExitMsg(x):
				self.appQ.put(x) #for other running threads
				return

			appEntry = x[0]
			msg = x[1]
			if(msg == Common.newMsg):
				self.newApp(appEntry)
				print appEntry["app"]+"added"
			elif msg == Common.finalizeMsg:
				self.finalizeApp(appEntry)
			else:
				self.logger.warning("wrong message received in appThread")
				continue

	def newApp(self,appEntry):
		app = appEntry["app"]
		print app
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

		print appEntry["direction"]
		
		if appEntry["direction"] == "up":
			if (app not in Common.appsToSync):
				self.onFinishApp(appEntry)
				return
			else:
				del Common.appsToSync[Common.appsToSync.index(app)]
		
		
		appEntry["nRemainDirs"] = len(dirs)
		appEntry["isHashChanged"] = True
		appEntry["isDownStopped"] = False

		n = len(dirs)
		for i in range(n-1,-1,-1):
			x = dirs[i]
			dirEntry = {"appEntry":appEntry,"dir":x,"dirIndex":i}
			self.newDir(dirEntry)

	def finalizeApp(self,appEntry):
		try:
			f = open(appEntry["appIni"], "wb")
			appEntry["appCfg"].write(f)
			f.close()
			conn = self.mainObj.conn
			if (appEntry["isHashChanged"] or appEntry["direction"] == "down") and not appEntry["isDownStopped"]: 
				isNetOpSuccessful = conn.uploadFile("app.ini", appEntry["appIni"], "%s/%s" % (appEntry["app"], self.mainObj.rdir_remote_temp))
				if isNetOpSuccessful > 0:
					appEntry["isSuccessful"] = True
				else:
					appEntry["isSuccessful"] = False
				self.logger.info(appEntry["app"] + " ini uploaded")
			else:
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


			os.remove(appEntry["appIni"])
			self.onFinishApp(appEntry)
		except:
			appEntry["isSuccessful"] = False
			self.logger.exception("error in finalizeApp")
			return

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
			appEntry["isSuccessful"] = True
		else:
			appEntry["isSuccessful"] = False

	def adir_appTemp(self, app):
		return self.mainObj.adir_temp + "/" + app

	def onFinishApp(self,appEntry):
		print appEntry["app"] + " " + str(appEntry["isSuccessful"])
		self.logger.info(appEntry["app"] + " end")
		self.mainQ.put([self.name,Common.finishMsg,appEntry])


class ZipThreadManager:

	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.mainObj = mO
		self.logger = logging.getLogger("daemon.syncclient.zip")
		self.failNotify = mO.failNotify

		#thread msg strings
		self.name = "Zipper"

		self.zipQ = self.mainObj.newQ()
		#self.unZipQ = self.mainObj.newQ()

		self.t = threading.Thread(target=self.zipperThread)
		self.t.start()


	def addEntry(self,dirEntry):
		adir_local = self.mainObj.dirToLocalPath(dirEntry["dir"])
		azip_name = "dir%d.7z" % dirEntry["dirIndex"]
		azip_local = "%s/%s" % (dirEntry["appEntry"]["temp"] , azip_name)
		
		
		
		dirEntry["adir_local"] = adir_local
		dirEntry["azip_name"] = azip_name
		dirEntry["azip_local"] = azip_local

		if platform.system() == 'Linux':
			zip_exe = "bin/appbin_7za"
		else:
			zip_exe = "appbin_7za"

		if(dirEntry["zipDirection"] == "up"): #dir -> 7zip
			if platform.system() == 'Linux':
				zipCmd = "%s a -t7z %s %s/* -mx3" % (zip_exe, azip_local, adir_local)
			else:
				zipCmd = "%s a -t7z \"%s\" \"%s\\*\" -mx3" % (zip_exe, azip_local.replace("/","\\"), adir_local.replace("/","\\"))
			dirEntry["zipCmd"] = zipCmd
		else:
			
			if platform.system() == 'Linux':
				zipCmd = "%s x -y %s -o%s -mmt=on" % (zip_exe, azip_local, adir_local)
			else:
				zipCmd = "%s x -y \"%s\" -o\"%s\" -mmt=on" % (zip_exe, azip_local.replace("/","\\"), adir_local.replace("/","\\"))
			dirEntry["zipCmd"] = zipCmd

		self.zipQ.put(dirEntry)

	def zipperThread(self):
		while True:
			try:
				x = self.zipQ.get()
				if Common.isExitMsg(x):
					return

				dirEntry = x
				
				if(not( (not self.mainObj.digestCheck) and dirEntry["zipDirection"] == "up" and dirEntry["appEntry"]["direction"] == "down") ):
					#enable below lines when sync is done per app
					if dirEntry["zipDirection"] == "down":
						shutil.rmtree(dirEntry["adir_local"],True) # delete target first
					
					if platform.system() == 'Linux':
						exe = dirEntry["zipCmd"].split(" ")
						print exe
						subprocess.call(exe)
					else:
						startupinfo = subprocess.STARTUPINFO()
						startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
						startupinfo.wShowWindow = subprocess.SW_HIDE
						subprocess.call(dirEntry["zipCmd"],startupinfo=startupinfo )
					self.logger.info(dirEntry["zipCmd"] + " excuted")
					
				
				self.onFinishEntry(dirEntry)
			except:
				self.logger.exception("compression or decompression error")
				continue

	def onFinishEntry(self,dirEntry):
		self.logger.info("%s %d %s zip finish" % (dirEntry["appEntry"]["app"], dirEntry["dirIndex"], dirEntry["dir"]) )
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])








class HashThreadManager:

	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.mainObj = mO
		self.logger = logging.getLogger("daemon.syncclient.hash")
		self.failNotify = mO.failNotify

		#Creating hasher
		#self.hasher = murmur3_32()

        #thread msg strings
		self.name = "Hasher"
		self.hashQ = self.mainObj.newQ()

		self.t = threading.Thread(target=self.hashThread)
		self.t.start()

	def addEntry(self,dirEntry):
		self.hashQ.put(dirEntry)

	def hashThread(self):
		while True:
			try:
				x = self.hashQ.get()
				if Common.isExitMsg(x):
					return
				dirEntry = x
				#hasher = hashlib.md5()
				print dirEntry["azip_local"]
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

		#thread msg strings
		self.name = "Ftp"

		self.ftpQ = self.mainObj.newQ()

		self.t = threading.Thread(target=self.ftpThread)
		self.t.start()

	def addEntry(self,dirEntry):
		self.ftpQ.put(dirEntry)

	def ftpThread(self):
		while True:
			x = self.ftpQ.get()
			if Common.isExitMsg(x):
				return
			dirEntry = x
			if (dirEntry["appEntry"]["direction"] == "up"):
				dirEntry["adir_remote"] = "%s/%s" % (dirEntry["appEntry"]["app"], self.mainObj.rdir_remote_temp)
				isNetOpSuccessful = self.mainObj.conn.uploadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])
			else:
				dirEntry["adir_remote"] = "%s/%s" % (dirEntry["appEntry"]["app"], self.mainObj.rdir_remote_current)
				isNetOpSuccessful = self.mainObj.conn.downloadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])
			if isNetOpSuccessful > 0:
				dirEntry["appEntry"]["isSuccessful"] = True
			else:
				dirEntry["appEntry"]["isSuccessful"] = False
			self.onFinishEntry(dirEntry)

	def onFinishEntry(self,dirEntry):
		self.logger.info("%s %d %s network operation finish" % (dirEntry["appEntry"]["app"], dirEntry["dirIndex"], dirEntry["dir"]) )
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])
