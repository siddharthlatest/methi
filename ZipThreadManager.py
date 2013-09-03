import Common

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
		azip_local = "%s\\%s" % dirEntry["temp"] , azip_name

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
		mQ.put([self.name,Common.finishMsg,dirEntry])