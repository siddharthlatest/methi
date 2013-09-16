
from time import sleep
import threading
import sys
import Common
import os

from SyncClient import SyncClient
from ThreadManagers import UpdateThreadManager

def setupLogs():
	Common.createPath(os.path.abspath('../data'))
	f_print = file('../data/print_log.txt', 'a',0)
	f_err = file('../data/error_log.txt', 'a',0)
	sys.stderr = f_err
	sys.stdout = f_print

def main():
	
	"""if Common.isProcessRunning("appbin_daemon.exe"):
		sys.exit() #exit if another daemon already running"""
	#sys.stderr = sys.stdout
	setupLogs()
	print "Daemon HAS STARTED"
	version = 0.02
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