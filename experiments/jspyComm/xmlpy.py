import socket
import threading
import subprocess
from SimpleXMLRPCServer import SimpleXMLRPCServer

class rpcExposed:
    def newApp(self, app,cmd):
		print "Calling app %s" % app
		t = threading.Thread(target=newAppThread, args=(app,cmd))
		t.start()
		return  "called :%s" % app 
		
def newAppThread(app,cmd):
	runningApps.append(app)
	subprocess.call(cmd)
	appFinish(app)

def appFinish(app):
	runningApps.remove(app)
	print "Finished app:%s" % app

runningApps = []
port = 65000
while True:	
	try:
		s = SimpleXMLRPCServer(("localhost", port))
		s.register_introspection_functions()
		s.register_instance(rpcExposed())
		break
	
	except socket.error:
		port = port+1
		pass
		
f = open('../data/pipe', 'w')
f.write(str(port))
f.close()

print "starting rpc server on:%d" % port
s.serve_forever()
