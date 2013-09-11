from psutil import Process
from psutil import get_process_list
from time import sleep
import threading
import urllib2
import urllib

from SyncClient import SyncClient

def update(version):
	while True:
		upData = urllib.urlencode({"hash":"thisishash"})
		page = urllib2.urlopen("http://getappbin.com/loadapp/version.php",upData)
		downData = page.read()
		data = downData.split(",")
		onlineVersion = float(data[0])
		downloadLink = data[1]
		if onlineVersion > version:
			page = urllib2.urlopen(downloadLink)
			updateData = page.read()
			with open("../data/update.exe","wb") as f:
				f.write(updateData)
			while True:
				isRunning = False
				for p in plist:
					if processName in p.name:
						isRunning = True
						break

				if not isRunning:
					break

				sleep(300)

			subprocess.Popen("../data/update.exe /SILENT")
			sys.exit(0)

	sleep(3600)

version = 0.01
sleepTime = 60
processName = "appbin_nw"
ut = threading.Thread(target=update, args=(version))
ut.start()

while True:
	print "Daemon HAS STARTED"
	syncClient = SyncClient()
	plist = get_process_list()
	isRunning = False
	for p in plist:
		if processName in p.name:
			isRunning = True
			break

	print "calling syncClient"
	syncClient.sync(isRunning)
	print "syncClient Done"
	print "Waiting for %d secs" % sleepTime
	sleep(sleepTime)