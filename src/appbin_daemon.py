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
	sleepTime = 10
	if Common.isWindows:
		selfProcName = "appbin_daemon.exe"
		processName = "appbin_nw.exe"
		zipProcName = "appbin_7za.exe"
		
	elif Common.isLinux:
		selfProcName = "appbin_daemon_lin"
		processName = "appbin_nw_lin"
		zipProcName = "appbin_7za"
		
	elif Common.isMac:
		selfProcName = "appbin_daemon_mac"
		processName = "appbin_nw_mac"
		zipProcName = "appbin_7za"
	
	uT = UpdateThreadManager(version,processName)
	aRT = AppRunnerThreadManager(analytics)	
	

	def changeIcon(icontoken):
		if not Common.isMac:  #disable wx in mac
			iconQ.put(icons[icontoken])

	def failNotify():
		changeIcon("-1")
	
	
	def exit():
		analytics.finish()
		Common.killProc(zipProcName)
		Common.killProc(selfProcName)
		os._exit(0)
	
	icons = { "1":"1.ico", "2":"2.ico", "3":"3.ico", "-1":"-1.ico", "0":"0.ico" }
	iconQ = Queue.Queue(0)
	if not Common.isMac:  #disable wx in mac
		t = threading.Thread(target=GUI.startGUI, args=(iconQ,exit))
		t.start()
		
	atexit.register(exit)
	
	def sigHandler(sig,frm):
		print "sig:" + str(sig)
		exit()

	signal.signal(signal.SIGTERM,sigHandler)
	
	if not Common.isWindows:
		signal.signal(signal.SIGINT,sigHandler)
		signal.signal(signal.SIGQUIT,sigHandler)
	
	def initSync():
		logger.info("calling syncClient")
		changeIcon("1")
		SyncClient(failNotify, changeIcon, analytics)
		logger.info("syncClient Done")
	
	Common.setSyncingMethod(initSync)
	
	while True:
		if Common.isProcessRunning(processName):
			Common.syncNow(False)
		
		if not Common.isProcessRunning(processName):
			logger.info("no appbin apps running. exiting.")
			exit()
		
		logger.info("Waiting for %d secs" % sleepTime)
		sleep(sleepTime)
			
main()
