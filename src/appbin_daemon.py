import Common
import sys

if(Common.isDaemonAlreadyRunning()):
	sys.exit()

from time import sleep
import threading

import os
import logging
import Queue
import subprocess
from analytics import Analytics

from SyncClient import SyncClient
from ThreadManagers import UpdateThreadManager,AppRunnerThreadManager

if not Common.isMac:
	import GUI #disable wx in mac

def setupLogs():
	Common.createPath(os.path.abspath('../data'))
	f_print = file('../data/stdout.txt', 'a',0)
	f_err = file('../data/stderr.txt', 'a',0)
	sys.stderr = f_err
	sys.stdout = f_print

def main():
	setupLogs()
	
	#creating log file and assigning stdout to logfile
	logger = logging.getLogger("daemon")
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler("../data/daemon_logs.log", delay=True)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	
	#Initializing Analytics
	analytics = Analytics()
	###
	
	
	logger.info("Daemon HAS STARTED")
	version = 1.0
	sleepTime = 20
	if Common.isWindows:
		processName = "appbin_nw.exe"
	elif Common.isLinux:
		processName = "appbin_nw_lin"
	elif Common.isMac:
		processName = "appbin_nw_mac"
		
	msgToUthread = Queue.Queue(0)
	uT = UpdateThreadManager(version,processNamemsg)
	aRT = AppRunnerThreadManager(version,processName,analytics)	
	
	stateQ = Queue.Queue(0)

	icons = { "1":"1.ico", "2":"2.ico", "3":"3.ico", "-1":"-1.ico", "0":"0.ico" }
	iconQ = Queue.Queue(0)
	if not Common.isMac:  #disable wx in mac
		t = threading.Thread(target=GUI.startGUI, args=(iconQ,stateQ))
		t.start()

	def changeIcon(icontoken):
		if not Common.isMac:  #disable wx in mac
			iconQ.put(icons[icontoken])

	def failNotify():
		changeIcon("-1")

	def exit(msgToUthread):
		analytics.finish()
		if Common.isLinux or Common.isMac :
			subprocess.call(["pkill", "appbin_7za"])
		else:
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
		SyncClient(failNotify, changeIcon, analytics)
		logger.info("syncClient Done")
		logger.info("Waiting for %d secs" % sleepTime)
		divide = 4
		for i in range(0, divide):
			if not stateQ.empty():
				exit(msgToUthread)
			sleep(sleepTime/divide)
			
main()
