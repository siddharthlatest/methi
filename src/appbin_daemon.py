from time import sleep
import threading
import sys
import Common
import os
import logging

from SyncClient import SyncClient
from ThreadManagers import UpdateThreadManager

def setupLogs():
	Common.createPath(os.path.abspath('../data'))
	f_print = file('../data/print_log.txt', 'a',0)
	f_err = file('../data/error_log.txt', 'a',0)
	sys.stderr = f_err
	sys.stdout = f_print

def main():
	#creating log file and assigning stdout to logfile
	logger = logging.getLogger("daemon")
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler("../data/daemon_logs.log", delay=True)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	
	if Common.numOfProcessRunning("appbin_daemon.exe") > 1:
		sys.exit() #exit if another daemon already running"""
	#sys.stderr = sys.stdout
	setupLogs()
	logger.info("Daemon HAS STARTED")
	version = 0.02
	sleepTime = 60
	processName = "appbin_nw.exe"
	uT = UpdateThreadManager(version,processName)
	
	while True:
		logger.info("calling syncClient")
		SyncClient(Common.isProcessRunning(processName))
		logger.info("syncClient Done")
		logger.info("Waiting for %d secs" % sleepTime)
		sleep(sleepTime)
	
main()