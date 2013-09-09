from psutil import Process
from psutil import get_process_list
from time import sleep

from SyncClient import SyncClient

sleepTime = 60
processName = "appbin"

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