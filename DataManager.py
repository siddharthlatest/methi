import pyhash
import threading
import ConfigParser
import pyhash

import FTPconnection

class DataManager:

	def __init__(self, conn):
		self.conn = conn

		self.compressQ = Queue.Queue(0)
		self.decompressQ = Queue.Queue(0)
		self.hashQ = Queue.Queue(0)
		self.transferQ = Queue.Queue(0)

		isCompressQRunning = False
		isDecompressQRunning = False
		isHashQRunning = False
		isTransferQRunning = False

		#Creating hasher
		hasher = pyhash.murmur3_32()

	def uploadZip(self,dirEntry):
		dirEntry["adir_remote"] = "%s/%s" % dirEntry["app"],"inprocess"
		conn.uploadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])

	def finalizeUpload(self, dirEntry):
		appCfg = dirEntry["appCfg"]
		original_digest = appCfg.get("data", str("dir") + str(dirEntry["dirIndex"]))
		original_digest = str(original_digest)
		if original_digest == str(dirEntry["digest"]):
			return
		else:
			self.uploadZip(dirEntry)

		if dirEntry["index"] == 0:
			syncAppFinish()

	def hashThread(self, dirEntry):
		while not self.hashQ.empty():
			dirEntry = hashQ.get()
			f = open(dirEntry["azip_local"], "r")
			digest = self.hasher(f.read())
			f.close()
			dirEntry["digest"] = digest
			self.finalizeUpload(dirEntry)

		self.isHashQRunning = False

	def addToHashQueue(self, dirEntry):
		self.hashQ.put(dirEntry)

		if not self.isHashQRunning:
			self.isHashQRunning = True
			t = threading.Thread(target=hashThread)
			t.start()

	def compresssThread(self):
		while not self.compressQ.empty():
			dirEntry = compressQ.get()
			subprocess.call(dirEntry["zipCmd"])
			self.addToHashQueue(dirEntry)

		self.isCompressQRunning = False

	def addToCompressQ(self, dirEntry):
		self.compressQ.put(dirEntry)

		if not self.isCompressQRunning:
			self.isCompressQRunning = True
			t = threading.Thread(target=compressThread)
			t.start()

	"""def decompressThread(self):
		while not self.decompressQ.empty():
			dirEntry = decompressQ.get()
			subprocess.call(dirEntry["zipCmd"])

		self.isDecompressQRunning = False

	def addToDecompressQ(self, dirEntry):
		self.decompressQ.put(dirEntry)

		if not self.isDecompressQRunning:
			self.isDecompressQRunning = True
			t = threading.Thread(target=decompressThread)
			t.start()"""

	def syncDirWithZip(self, dirEntry):
		adir_local = dirEntry["dir"]
		azip_name = "dir%d.7z" % dirEntry["dirIndex"])
		azip_local = "%s\\%s" % dirEntry["temp"] , azip_name

		dirEntry["adir_local"] = adir_local
		dirEntry["azip_name"] = azip_name
		dirEntry["azip_local"] = azip_local

		if(dirEntry["zipDirection"] == "up"): #dir -> 7zip
			zipCmd = "7za a -t7z %s %s -mx3" % azip_local, adir_local
			dirEntry["zipCmd"] = zipCmd
			self.addToCompressQ(dirEntry)
		else:
			zipCmd = "7za e %s -o%s" % azip_local, adir_local
			dirEntry["zipCmd"] = zipCmd
			self.getToDecompress(dirEntry)