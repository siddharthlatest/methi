var xmlrpc = require("xmlrpc");
fs = require("fs")
app = "cut_the_rope"
cmd = "cmd /c echo " + app+" called" 

//if client not running, run it,
//wait until file exists

pipeFile = "../data/pipe"
//fs.openSync(pipeFile, "r")
rpcPort = fs.readFileSync(pipeFile)
console.log(rpcPort);

var client = xmlrpc.createClient({ host: 'localhost', port: rpcPort, path: '/'})

client.methodCall('newApp', [app,cmd], function (error, reply) {
    if(error){
        console.log("ERROR: ", error);
    } else {
		console.log("rpc reply:"+ reply);
	}
})