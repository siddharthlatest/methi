from time import sleep
import threading
import sys
import Common
import os
import logging
import win32gui
from subprocess import Popen
import Queue

from SyncClient import SyncClient
from ThreadManagers import UpdateThreadManager
from GUI import *

def setupLogs():
	Common.createPath(os.path.abspath('../data'))
	f_print = file('../data/comm_path.txt', 'w',0)
	f_err = file('../data/error_log.txt', 'a',0)
	#sys.stderr = f_err
	#sys.stdout = f_print

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

	setupLogs()
	logger.info("Daemon HAS STARTED")
	version = 0.10
	sleepTime = 60
	processName = "appbin_nw.exe"
	uT = UpdateThreadManager(version,processName)

	gui = GUI()

	def changeIcon(icontoken):
		gui.changeIcon(icontoken)

	def failNotify():
		gui.changeIcon("-1")

	while True:
		logger.info("calling syncClient")
		print "sync start"
		SyncClient(Common.isProcessRunning(processName), failNotify, changeIcon)
		logger.info("syncClient Done")
		logger.info("Waiting for %d secs" % sleepTime)
		sleep(sleepTime)
	
main()