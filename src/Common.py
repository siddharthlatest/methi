import os
import errno
import platform
if platform.system()=='Linux':
	import subprocess
else:
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