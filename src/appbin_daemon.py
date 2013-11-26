import Common
import sys
import signal

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
import atexit

if not Common.isMac:
	import GUI #disable wx in mac

def setupLogs():
	Common.createPath(os.path.abspath('../data'))
	f_out = file('../data/stdout.txt', 'a',0)
	f_err = file('../data/stderr.txt', 'a',0)
	sys.stderr = f_err
	sys.stdout = f_out

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
	
	
	logger.info("Daemon Init")
	version = 1.0
	sleepTime = 20
	if Common.isWindows:
		processName = "appbin_nw.exe"
	elif Common.isLinux:
		processName = "appbin_nw_lin"
	elif Common.isMac:
		processName = "appbin_nw_mac"
	
	uT = UpdateThreadManager(version,processName)
	aRT = AppRunnerThreadManager(analytics)	
	
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
	
	
	def exit():
		analytics.finish()
		if Common.isLinux :
			subprocess.call(["pkill", "appbin_7za"])
		elif Common.isMac :
			subprocess.call(["killall","-9" ,"appbin_7za"])
		elif Common.isWindows:
			subprocess.call("cmd /c \"taskkill /F /T /IM appbin_7za.exe\"")
		print "exit"
		os._exit(0)
		
	atexit.register(exit)
	
	def sigHandler(sig,frm):
		print "sig:" + str(sig)
		exit()

	signal.signal(signal.SIGTERM,sigHandler)
	
	if Common.isWindows:
		signal.signal(signal.CTRL_C_EVENT,sigHandler)
		signal.signal(signal.CTRL_BREAK_EVENT,sigHandler)
	else:
		signal.signal(signal.SIGINT,sigHandler)
		signal.signal(signal.SIGQUIT,sigHandler)
		
	while True:
		if not stateQ.empty():
			exit()
		logger.info("calling syncClient")
		changeIcon("1")
		SyncClient(failNotify, changeIcon, analytics)
		logger.info("syncClient Done")
		logger.info("Waiting for %d secs" % sleepTime)
		divide = 4
		for i in range(0, divide):
			if not stateQ.empty():
				exit()
			sleep(sleepTime/divide)
			
main()
