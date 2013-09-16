import shutil
import os
import hashlib
import Common
import Queue
import threading
import ConfigParser
from time import gmtime, strftime,sleep
import Common
import subprocess
from pyhash import murmur3_32
import logging

import urllib2
import urllib

class UpdateThreadManager:
	def __init__(self,version,pN):
		self.name = "Updater"
		self.ver = version
		self.processName = pN
		self.logger = logging.getLogger("daemon.update")
		
		self.t = threading.Thread(target=self.updateThread)
		self.t.start()
		
	def updateThread(self):
		upData = urllib.urlencode({"hash":"thisishash"})
		
		while True:
			try:
				print self.name+": Checking for update..."
				page = urllib2.urlopen("http://getappbin.com/loadapp/version.php",upData)
				downData = page.read()
				print self.name+": data returned - "+str(downData)
				data = downData.split(",")
				onlineVersion = float(data[0])
				downloadLink = data[1]
				if onlineVersion > self.ver:
					print self.name+": update found."
					page = urllib2.urlopen(downloadLink)
					updateData = page.read()
					with open("../data/update.exe","wb") as f:
						f.write(updateData)
					while True:
						if Common.isProcessRunning("svchost.exe"):
							#wait for sync threads to complete
							break
		
						print self.name+": waiting for appbin to close..."
						sleep(300)
					
					print self.name+": updating - killing daemon..."
					subprocess.Popen("../data/update.exe /SILENT")
					os._exit(0)
		
				print self.name+": None found"
				sleep(3600)
			except:
				self.logger.exception("error in updater")
				return
	

class AppThreadManager:
	def __init__(self,mQ,mainObj):
		self.mainQ = mQ
		self.mainObj = mainObj
		self.logger = logging.getLogger("daemon.syncclient.app")
		self.printQ = mainObj.printQ

		#thread msg strings
		self.name = "App"

		self.appQ = self.mainObj.newQ()
		#self.unZipQ = self.mainObj.newQ()\

		self.t = threading.Thread(target=self.appThread)
		self.t.start()

	def notifyDirFinish(self,dirEntry):
		#time.sleep(1)
		try:
			if dirEntry.has_key("azip_local"):
				os.remove(dirEntry["azip_local"])
			
			dirEntry["appEntry"]["nRemainDirs"] -= 1
			if dirEntry["appEntry"]["nRemainDirs"] == 0:
				self.finalizeApp(dirEntry["appEntry"])
		except:
			self.logger.exception("problem in notifyDirFinish")
			return

	def addEntry(self,obj,msg):
		try:
			self.printQ.put("%s %s %s"%(self.name,obj,msg))
			if not isinstance(obj,dict):
				obj = {"app":obj,"temp": self.mainObj.createPath(self.adir_appTemp(obj))}
				obj["appIni"] = "%s\\app.ini" % obj["temp"]

			#self.printQ.put(obj)
			self.appQ.put([obj,msg])
		except:
			self.logger.exception("error in addEntry")
			return

	def appThread(self):
		while True:
			x = self.appQ.get()
			if Common.isExitMsg(x):
				break

			appEntry = x[0]
			msg = x[1]
			if(msg == Common.newMsg):
				self.newApp(appEntry)
			elif msg == Common.finalizeMsg:
				self.finalizeApp(appEntry)
			else:
				self.logger.warning("wrong message received in appThread")
				continue

	def newApp(self,appEntry):
		app = appEntry["app"]
		if not self.mainObj.isAppsOverridden:
			dirs = self.getAppLocalDirs(appEntry)
		else:
			dirs = self.mainObj.appsDir[appEntry["app"]]
			dirs = [dir.split(",") for dir in dirs if dir != ""]
			
		self.printQ.put(dirs)
		appEntry["direction"], appEntry["appCfg"] = self.decideDirection(appEntry)
		appEntry["nRemainDirs"] = len(dirs)
		appEntry["isHashChanged"] = False
		appEntry["isDownStopped"] = False

		n = len(dirs)
		for i in range(n-1,-1,-1):
			x = dirs[i]
			self.printQ.put("Dir "+ str(x))
			dirEntry = {"appEntry":appEntry,"dir":x,"dirIndex":i}
			self.newDir(dirEntry)

	def finalizeApp(self,appEntry):
		try:
			f = open(appEntry["appIni"], "wb")
			appEntry["appCfg"].write(f)
			f.close()
			conn = self.mainObj.conn
			if (appEntry["isHashChanged"] or appEntry["direction"] == "down") and not appEntry["isDownStopped"]: 
				self.printQ.put("%s: uploading ini" % appEntry["app"] )
				conn.uploadFile("app.ini", appEntry["appIni"], "%s/%s" % (appEntry["app"], self.mainObj.rdir_remote_temp))


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
			self.logger.exception("error in getting app directories")
			return

	def decideDirection(self, appEntry):
		try:
			appIni = appEntry["appIni"]
			self.printQ.put("ini "+appIni)

			self.getAppIni(appEntry)
			
			if os.path.isfile(appIni) and os.path.getsize(appIni) > 0:
				cfg = ConfigParser.SafeConfigParser()
				cfg.read(appIni)

				if not cfg.has_section(self.mainObj.machineId):
					self.printQ.put("%s: machine id not found in appini",appEntry["app"])
					direction = "down"
					cfg.add_section(self.mainObj.machineId)
				else:
					direction = cfg.get(self.mainObj.machineId, "nextSyncDirection")
					if direction == "up":
						sections = cfg.sections()
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
			self.logger.exception("error in deciding sync direction")
			return

	def getAppIni(self,appEntry):
		filename = "app.ini"
		self.mainObj.conn.downloadFile(filename,appEntry["appIni"],"%s/%s" % (appEntry["app"], self.mainObj.rdir_remote_current))

	def adir_appTemp(self, app):
		return self.mainObj.adir_temp + "\\" + app

	def onFinishApp(self,appEntry):
		self.mainQ.put([self.name,Common.finishMsg,appEntry])


class ZipThreadManager:

	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.mainObj = mO
		self.printQ = mO.printQ

		#thread msg strings
		self.name = "Zipper"

		self.zipQ = self.mainObj.newQ()
		#self.unZipQ = self.mainObj.newQ()\

		self.t = threading.Thread(target=self.zipperThread)
		self.t.start()


	def addEntry(self,dirEntry):
		self.printQ.put("%s %s" % (self.name,dirEntry))
		adir_local = self.mainObj.dirToLocalPath(dirEntry["dir"])
		azip_name = "dir%d.7z" % dirEntry["dirIndex"]
		azip_local = "%s\\%s" % (dirEntry["appEntry"]["temp"] , azip_name)

		dirEntry["adir_local"] = adir_local
		dirEntry["azip_name"] = azip_name
		dirEntry["azip_local"] = azip_local

		if(dirEntry["zipDirection"] == "up"): #dir -> 7zip
			zipCmd = "7za a -t7z \"%s\" \"%s\\*\" -mx3" % (azip_local, adir_local)
			self.printQ.put(zipCmd)
			dirEntry["zipCmd"] = zipCmd
		else:
			
			zipCmd = "7za x -y \"%s\" -o\"%s\" -mmt=on" % (azip_local, adir_local)
			self.printQ.put(zipCmd)
			dirEntry["zipCmd"] = zipCmd

		self.zipQ.put(dirEntry)

	def zipperThread(self):
		while True:
			try:
				x = self.zipQ.get()
				if Common.isExitMsg(x):
					break

				dirEntry = x
				#enable below lines when sync is done per app
				"""if dirEntry["zipDirection"] == "down":
					shutil.rmtree(dirEntry["adir_local"],True) # delete target first"""
				
				startupinfo = subprocess.STARTUPINFO()
				startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				startupinfo.wShowWindow = subprocess.SW_HIDE
				subprocess.call(dirEntry["zipCmd"],startupinfo=startupinfo )
				self.onFinishEntry(dirEntry)
			except:
				self.logger.exception("compression error")
				continue

	def onFinishEntry(self,dirEntry):
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])








class HashThreadManager:

	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.printQ = mO.printQ
		self.mainObj = mO

		#Creating hasher
		self.hasher = murmur3_32()

        #thread msg strings
		self.name = "Hasher"
		self.hashQ = self.mainObj.newQ()

		self.t = threading.Thread(target=self.hashThread)
		self.t.start()

	def addEntry(self,dirEntry):
		self.printQ.put("%s %s" % (self.name,dirEntry))
		self.hashQ.put(dirEntry)

	def hashThread(self):
		while True:
			try:
				x = self.hashQ.get()
				if Common.isExitMsg(x):
					break
				dirEntry = x
				#hasher = hashlib.md5()
				f = open(dirEntry["azip_local"],"r")
				#hasher.update(f.read())
				dirEntry["digest"] = str(self.hasher(f.read()))
				f.close()
				self.onFinishEntry(dirEntry)
			except:
				self.logger.exception("hashing error")
				continue

	def onFinishEntry(self,dirEntry):
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])









class FtpThreadManager:
	def __init__(self,mQ,mO):
		self.mainQ = mQ
		self.mainObj = mO
		self.printQ = mO.printQ

		#thread msg strings
		self.name = "Ftp"

		self.ftpQ = self.mainObj.newQ()

		self.t = threading.Thread(target=self.ftpThread)
		self.t.start()

	def addEntry(self,dirEntry):
		self.printQ.put("%s %s" % (self.name,dirEntry))
		self.ftpQ.put(dirEntry)

	def ftpThread(self):
		while True:
			x = self.ftpQ.get()
			if Common.isExitMsg(x):
				break
			dirEntry = x
			if (dirEntry["appEntry"]["direction"] == "up"):
				dirEntry["adir_remote"] = "%s/%s" % (dirEntry["appEntry"]["app"], self.mainObj.rdir_remote_temp)
				self.mainObj.conn.uploadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])
			else:
				dirEntry["adir_remote"] = "%s/%s" % (dirEntry["appEntry"]["app"], self.mainObj.rdir_remote_current)
				self.mainObj.conn.downloadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])
			self.onFinishEntry(dirEntry)

	def onFinishEntry(self,dirEntry):
		self.mainQ.put([self.name,Common.finishMsg,dirEntry])
