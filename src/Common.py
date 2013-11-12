import os
import errno
import platform
import xmlrpclib
if platform.system()=='Linux':
	isLinux = True
	isWindows = False
	isMac = False
elif platform.system()=='Windows':
	isLinux = False
	isWindows = True
	isMac = False
else:	
	isLinux = False
	isWindows = False
	isMac = True

if platform.system()=='Linux':
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

def isDaemonAlreadyRunning():
	try:
		f = open('../data/pipe', 'r')
	except:
		return False
	
	port = f.read()
	f.close()
	print "trying" + port
	
	if (isinstance(port,int)):
		return False
	
	rpc = xmlrpclib.ServerProxy("http://localhost:"+port)
	try:
		print rpc.hello()
		return True
	except:
		return False
	

def createPath(x):
	print x
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
	if platform.system()=='Linux':
		try:
			output = subprocess.check_output(["ps", "-C", proc])
			return True
		except subprocess.CalledProcessError:
			return False
	else:
		pythoncom.CoInitialize()
		bool = False;
		c = wmi.WMI (find_classes=False)
		if len(c.query("SELECT Handle FROM Win32_Process WHERE Name = '%s'" % proc)):
			bool = True
		return bool

def numOfProcessRunning(proc):
	if platform.system()=='Linux':
		try:
			output = subprocess.check_output(["ps", "-C", proc])
			procs = output.split("\n")
			return len(procs)-1
		except subprocess.CalledProcessError:
			return 0
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