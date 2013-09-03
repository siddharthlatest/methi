import Common

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
			subprocess.call(dirEntry["zipCmd"])
			onFinishEntry(dirEntry)

	def uploadZip(self,dirEntry):
		dirEntry["adir_remote"] = "%s/%s" % dirEntry["app"],"inprocess"
		self.mainObj.conn.uploadFile(dirEntry["azip_name"],dirEntry["azip_local"],dirEntry["adir_remote"])

	def onFinishEntry(self,dirEntry):
		mQ.put([self.name,Common.finishMsg,dirEntry])



"""def finalizeUpload(self, dirEntry):
		appCfg = dirEntry["appCfg"]
		original_digest = appCfg.get("data", str("dir") + str(dirEntry["dirIndex"]))
		original_digest = str(original_digest)
		if original_digest == str(dirEntry["digest"]):
			return
		else:
			self.uploadZip(dirEntry)

		if dirEntry["dirIndex"] == 0:
			syncAppFinish()

		@staticmethod

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

"""
