import os
import errno
import platform
import xmlrpclib
import socket
import logging

if platform.system()=='Linux':
	isLinux = True
	isWindows = False
	isMac = False
	self_proc_name = "appbin_daemon"
	
elif platform.system()=='Windows':
	isLinux = False
	isWindows = True
	isMac = False
	self_proc_name = "appbin_daemon.exe"

elif platform.system() == 'Darwin':
	isLinux = False
	isWindows = False
	isMac = True
	self_proc_name = "appbin_daemon_mac"

if isLinux or isMac:
	import subprocess
else:
	import win32con
	import win32gui
	import win32process
	import wmi
	import pythoncom

finishMsg = "Finish"
errorMsg = "Error"
newMsg = "New"
finalizeMsg = "Finalize"
startMsg = "Start"
checkMsg = "Check"
okMsg = "Ok"
lockedMsg = "Locked"
stopMsg = "Stop"
exitMsg = "Exit"

appsToSync = []
appsRunning = []

class nwRpc():

	rpcSrv = ''
	isServerUp = False
	
	@classmethod
	def setPort(cls,port):
		cls.rpcSrv = xmlrpclib.ServerProxy("http://localhost:"+str(port))
		cls.isServerUp = True
	
	@classmethod
	def methodWrapper(cls,str):
		if not cls.isServerUp:
			return
		try:
			logging.getLogger("daemon.nwRpcClient").info("calling "+ str)
			exec(str) in locals()
			
		except socket.error:
			cls.isServerUp = False
		except Exception as e:
			logging.getLogger("daemon.nwRpcClient").exception(type(e))
	
	@classmethod	
	def showInSync(cls,app):
		cls.methodWrapper("cls.rpcSrv.showInSync(\'%s\')" % (app))
	
	@classmethod
	def showSyncing(cls,app):
		cls.methodWrapper("cls.rpcSrv.showSyncing(\'%s\')" % (app))
	
def isDaemonAlreadyRunning():
	#check by process
	if( numOfProcessRunning(self_proc_name) > 2): # daemon itself has two processes
		return True
	
	#check by rpc
	try:
		f = open('../data/pipe', 'r')
	except:
		return False
	
	port = f.read()
	f.close()
		
	if (isinstance(port,int)):
		return False
	
	rpc = xmlrpclib.ServerProxy("http://localhost:"+str(port))
	try:
		rpc.hello()
		return True
	except:
		return False
	

def createPath(x):
	try:
		os.makedirs(x)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(x):
			pass
		else: raise

	return x

def isExitMsg(x):
	return (isinstance(x,str) and x == exitMsg)
   
def isProcessRunning(proc):
	if isMac or isLinux:
		number = int(subprocess.check_output("ps aux | grep "+proc+" | grep -v grep | wc -l", shell=True).strip())
		return True if number else False
	else:
		pythoncom.CoInitialize()
		bool = False;
		c = wmi.WMI (find_classes=False)
		if len(c.query("SELECT Handle FROM Win32_Process WHERE Name = '%s'" % proc)):
			bool = True
		return bool

def numOfProcessRunning(proc):
	if isLinux or isMac:
		return int(subprocess.check_output("ps aux | grep "+proc+" | grep -v grep | wc -l", shell=True).strip())
	else:
		pythoncom.CoInitialize()
		c = wmi.WMI (find_classes=False)
		return len(c.query("SELECT Handle FROM Win32_Process WHERE Name = '%s'" % proc))

def get_hwnds_for_pid (pid):
	def callback (hwnd, hwnds):
		if win32gui.IsWindowVisible (hwnd) and win32gui.IsWindowEnabled (hwnd):
			_, found_pid = win32process.GetWindowThreadProcessId (hwnd)
			if found_pid == pid:
				hwnds.append (hwnd)
		return True

	hwnds = []
	win32gui.EnumWindows (callback, hwnds)
	return hwnds
