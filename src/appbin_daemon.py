from time import sleep
import threading
import sys
import Common
import os
import logging
import wx
import Queue
import subprocess

from SyncClient import SyncClient
from ThreadManagers import UpdateThreadManager,AppRunnerThreadManager
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
	sleepTime = 5
	processName = "appbin_nw.exe"
	msgToUthread = Queue.Queue(0)
	uT = UpdateThreadManager(version,processName,msgToUthread)
	aRT = AppRunnerThreadManager(version,processName,msgToUthread)

	stateQ = Queue.Queue(0)

	icons = { "1":"1.ico", "2":"2.ico", "3":"3.ico", "-1":"-1.ico", "0":"0.ico" }
	iconQ = Queue.Queue(0)
	t = threading.Thread(target=startGUI, args=(iconQ,stateQ))
	t.start()

	def changeIcon(icontoken):
		iconQ.put(icons[icontoken])

	def failNotify():
		changeIcon("-1")

	def exit(msgToUthread):
		subprocess.call("cmd /c \"taskkill /F /T /IM appbin_7za.exe\"")
		msgToUthread.put("exit")
		sleep(5)
		print "exit"
		os._exit(0)

	while True:
		if not stateQ.empty():
			exit(msgToUthread)
		logger.info("calling syncClient")
		print "sync start"
		changeIcon("1")
		SyncClient(Common.isProcessRunning(processName), failNotify, changeIcon)
		logger.info("syncClient Done")
		logger.info("Waiting for %d secs" % sleepTime)
		for i in range(0, 12):
			if not stateQ.empty():
				exit(msgToUthread)
			sleep(sleepTime)
	
main()
