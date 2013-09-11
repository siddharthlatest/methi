
from psutil import Process
from psutil import get_process_list
from time import sleep
import threading

from SyncClient import SyncClient
from ThreadManagers import UpdateThreadManager

def main():
	print "Daemon HAS STARTED"
	version = 0.01
	sleepTime = 60
	processName = "appbin_nw"
	uT = UpdateThreadManager(version,processName)
	
	while True:
		plist = get_process_list()
		isRunning = False
		for p in plist:
			if processName in p.name:
				isRunning = True
				break
	
		print "calling syncClient"
		SyncClient(isRunning)
		print "syncClient Done"
		print "Waiting for %d secs" % sleepTime
		sleep(sleepTime)
	
main()