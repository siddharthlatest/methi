import os
import wmi

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
	if x == "":
		return x
	y = x
	while y[-1] == "\\":
		y = y[:-1]
	if not os.access(y, os.F_OK):
		createPath(y[:y.rfind("\\")])
		os.mkdir(y)

	return x

def isExitMsg(x):
    return (isinstance(x,str) and x == exitMsg)
   
def isProcessRunning(proc):
	bool = False;
	c = wmi.WMI (find_classes=False)
	if len(c.query("SELECT Handle FROM Win32_Process WHERE Name = '%s'" % proc)):
		bool = True
	print proc,bool
	return bool