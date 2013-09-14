
from time import sleep
import threading
import sys
import Common

from SyncClient import SyncClient
from ThreadManagers import UpdateThreadManager

def setupLogs():
	f_print = file('../data/print_log.txt', 'a',0)
	f_err = file('../data/error_log.txt', 'a',0)
	sys.stderr = f_err
	sys.stdout = f_print

def main():
	#sys.stderr = sys.stdout
	#setupLogs()
	print "Daemon HAS STARTED"
	version = 0.01
	sleepTime = 60
	processName = "appbin_nw.exe"
	uT = UpdateThreadManager(version,processName)
	
	while True:
		print "calling syncClient"
		SyncClient(Common.isProcessRunning(processName))
		print "syncClient Done"
		print "Waiting for %d secs" % sleepTime
		sleep(sleepTime)
	
main()