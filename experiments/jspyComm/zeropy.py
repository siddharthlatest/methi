import zerorpc
import zmq
import threading
import subprocess

class rpcExposed(object):
    def newApp(self, app,cmd):
		print "Calling app %s" % app
		t = threading.Thread(target=newAppThread, args=(app,cmd))
		t.start()
		return  "called :%s" % app 
		

def newAppThread(app,cmd):
	subprocess.call(cmd)
	appFinish(app)

def appFinish(app):
	print "Finished app:%s" % app

s = zerorpc.Server(rpcExposed())
port = 65000
while True:
	try:
		s.bind("tcp://0.0.0.0:%d" % port)
		break
	except zmq.error.ZMQError:
		port = port+1
		pass

print "rpc running on port:%d" % port
f = open('../data/pipe', 'w')
f.write(str(port))
f.close()

s.run()