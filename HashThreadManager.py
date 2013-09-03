import pyhash

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
