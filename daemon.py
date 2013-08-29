import uuid
import os
import subprocess
import sys
import Queue
import thread
import threading
import time


from time import gmtime, strftime
from iniparse import INIConfig
from iniparse import config
from iniparse import ini

#consts
#-----------
userProfile = os.getenv('USERPROFILE')
cDrive = "C:"
programFiles86 = os.getenv('programfiles(x86)')
programFiles = os.getenv('ProgramW6432')
userAppDataDir = os.getenv('APPDATA')
#appBinConfigDir = userAppDataDir+'\AppBin'
appBinConfigDir = '.'

appBinConfigDir = os.path.abspath(appBinConfigDir)
cygHome = appBinConfigDir + "/cygHome"
appsIniFile = appBinConfigDir+'/apps.ini'
configIniFile = appBinConfigDir+'/config.ini'
remoteMachinesIniPath = "machines"
#binDir = "C:\\myBin\\Apps\\bin"
binDir = "./bin"
os.environ['PATH'] = os.getenv('PATH')+";"+os.path.abspath(binDir)
#os.environ['HOME'] = cygHome
os.environ['HOME'] = "C:\\myBin\\Files\\linuxHome"

#execution command queue
cmdQueue = Queue.Queue(0)
appQueue = Queue.Queue(0)
printQueue = Queue.Queue(0)
isCmdRunning = False
isAppQRunning = False
isPrintQRunning = False

#config loading
fl = open(configIniFile,'r')
cfg = INIConfig(fl)
fl.close()

server = cfg.main.syncServer
user = cfg.main.name
pwd = cfg.main.pwd
remoteUserHome = "/home/"+user+"/appbin"
apps = filter(None,cfg.main.apps.split(';'))
appN=0

if isinstance(cfg.main.machineId,config.Undefined):
    machineId = str(uuid.uuid1())
    cfg.main.machineId = machineId

    fl = open(configIniFile,'w+')
    print >> fl, cfg
    fl.close()
else:
    machineId = cfg.main.machineId


syncTool = "rsync"
def genSyncCmd(app,pathPair,direction):
    #rsync -begin
    if direction == "up":
        cmd = syncTool+ " --recursive --blocking-io -e 'cygnative plink -batch -ssh -pw "+pwd+"' --perms --chmod=Du=rwx,Fu=rw,go-rwx -rzsh --progress --delete --force " + "--rsync-path=\"umask u=rwx,go-rwx && mkdir --parents '"+remoteAbsPath(app,pathPair[1])+"' && rsync\" " + wrapWithQuotes(pathPair[0]+"/") +" "+ user +"@"+server+":"+wrapWithQuotes(createRemotePath(remoteAbsPath(app,pathPair[1])))
    else:
        cmd = syncTool+ " --recursive --blocking-io -e 'cygnative plink -batch -ssh -pw "+pwd+"' -rzsh --progress --delete --force " + user +"@"+server+":"+wrapWithQuotes(remoteAbsPath(app,pathPair[1])+"/")+" "+ wrapWithQuotes(pathPair[0])
    #rsync -end
    return cmd

def getAppLocalDirs(app):
    fl = open(appsIniFile,'r')
    cfg = INIConfig(fl)
    fl.close()

    paths = cfg[app]['paths'].split(';')
    paths = [path.split(",") for path in paths if path != ""]

    return paths

def localWinPath(x):
    return (eval(x[0])+"\\"+x[1]).lower()

def localPath(x):
    return "/cygdrive/"+(eval(x[0])+"\\"+x[1]).replace('\\', '/').replace(':', '').replace('//', '/').lower()

def remotePath(x):
    return (x[0]+"/"+x[1].replace('\\', '/')).replace('//', '/').lower()

def remoteAbsPath(app,x):
    return remoteUserHome+"/"+app+"/"+x

def winToLinPath(x):
    return "/cygdrive/"+x.replace('\\', '/').replace(':', '').replace('//', '/').lower()

def createRemotePath(x):
    cmd = "plink -ssh -pw " + pwd + " " + user + "@" + server + " mkdir -p '" + x +"'"
    #exe(cmd)
    return x

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

def wrapWithQuotes(x):
    return '"'+x+'"'

def syncApp(app):
    printQ(app+" : Init Sync...")
    global appN
    appN += 1
    direction,machinesIniPath = decideDirection(app)
    printQ( app+" : Direction - "+direction)

    #below part should be atomic
    #atomic -start
    dirs = getAppLocalDirs(app)
    n = len(dirs)
    for i in range(n):
        x = dirs[i]
        createPath(localWinPath(x))
        appSyncIndicator(app,1)

        cmd = genSyncCmd(app,[localPath(x),remotePath(x)],direction)
        endCmd= "\""+"syncAppMachinesIni('"+app+"','"+machinesIniPath+"','up')"+"\""
        exeQ(cmd,"appSyncIndicator('"+app+"',-1,"+endCmd+")")
        """
        if (i == n-1): #last one
            cmd1,cmd2,cmd3 = syncAppMachinesIni(app,machinesIniPath,"up",True)
            exeQ(cmd,cmd1,cmd2,cmd3)
        else:
            exeQ(cmd)
        """

    #atomic -end

def syncAppMachinesIni(app,machinesIniPath,direction,returnOnly=False):
    cmd = genSyncCmd(app,[winToLinPath(machinesIniPath),remoteMachinesIniPath],direction)
    if(direction == "up"):
        #delete machineInIPath
        machinesIniFile = machinesIniPath+"\\machines.ini"
        delCmd = "cmd /c del /F /Q " + wrapWithQuotes(machinesIniFile)
        printCmd = "cmd /c echo 'Complete: "+app+"'"
        if not returnOnly:
            exeQ(cmd,delCmd)
    else:
        if not returnOnly:
            exeNow(cmd)
            #return cmd

    #return cmd,delCmd,printCmd

def syncAllApps():
    for app in apps:
        if isAppQRunning:
            appQueue.put(app)
        else:
            appQueue.put(app)
            startAppQ()

def decideDirection(app):
    machinesIniPath = createPath(appBinConfigDir+"\\"+remoteMachinesIniPath+"\\"+app)
    machinesIniFile = machinesIniPath+"\\machines.ini"

    syncAppMachinesIni(app,machinesIniPath,"down")

    if os.path.isfile(machinesIniFile):
        fl = open(machinesIniFile,'r')
        cfg = INIConfig(fl)
        fl.close()

        if isinstance(cfg[machineId],config.Undefined):
            direction = "down"
        else:
            direction = cfg[machineId]["nextSyncDirection"]
            if direction == "up":
                for k,v in cfg._sections.iteritems():
                    v["nextSyncDirection"] = "down"

    else:
        cfg = INIConfig()
        direction = "up"

    #final writing
    cfg[machineId]["lastSyncStartTime"] = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " GMT"
    cfg[machineId]["lastSyncDirection"] = direction
    cfg[machineId]["nextSyncDirection"] = "up"

    fl = open(machinesIniFile,'w+')
    print >> fl, cfg
    fl.close()

    return direction,machinesIniPath

def exeQ(*cmds):
    cmds = [cmd for cmd in cmds if cmd != ""]
    cmdQueue.put(cmds)

    if not (isCmdRunning):
        startExeQ()

def exeNow(cmd):
    #printQ(cmd)
    arg0 = cmd.split(' ',1)[0]
    if arg0 == syncTool or arg0 == "cmd":
        subprocess.call(cmd)
    else:
        exec cmd

def startExeQ():
    isCmdRunning = True
    for i in range(4):
        #thread.start_new_thread(newProcess,(i,))
        t = threading.Thread(target=newProcess)
        t.setDaemon(True)
        t.start()

def newProcess():
    while not (cmdQueue.empty()):
        cmds = cmdQueue.get()
        for cmd in cmds:
                #printQ(cmd)
                arg0 = cmd.split(' ',1)[0]
                if arg0 == syncTool or arg0 == "cmd":
                    subprocess.call(cmd)
                else:
                    exec cmd

    isCmdRunning = False

def startAppQ():
    isAppQRunning = True
    for i in range(2):
        #thread.start_new_thread(newAppProcess,(i,))
        t = threading.Thread(target=newAppProcess)
        t.daemon=True
        t.start()

def newAppProcess():
    while not (appQueue.empty()):
        app = appQueue.get()
        syncApp(app)

    isAppQRunning = False


appInidicatorDir = {}
asiLock = threading.Lock()
def appSyncIndicator(app,i,endCmd = ""):
    global appN
    asiLock.acquire()

    if int(i)>0:
        if appInidicatorDir.has_key(app):
            appInidicatorDir[app] = appInidicatorDir[app] + i
        else:
            appInidicatorDir[app] = 1
            printQ(app+" : Syncing...")
    else:
        appInidicatorDir[app] = appInidicatorDir[app] + i
        if appInidicatorDir[app] == 0:
            appN -= 1
            exeNow(endCmd)
            printQ(app+" : Sync complete. "+str(appN)+" app(s) remaining.")

    asiLock.release()


printLock =  threading.Lock()
def printQ(strn):
    printQueue.put(strn)

    if not (isPrintQRunning):
        startPrintQ()

def startPrintQ():
    isPrintQRunning = True
    #thread.start_new_thread(printThread,())
    t = threading.Thread(target=printThread)
    t.setDaemon(True)
    t.start()

def printThread():
    while not (printQueue.empty()):
        strn = printQueue.get()
        printLock.acquire()
        #print
        print strn
        printLock.release()

    isPrintQRunning = False

syncAllApps()

while (threading.activeCount() >1 ):
    time.sleep(0.5)
    #list[0].join()

print "Done."
raw_input()