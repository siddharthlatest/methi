var zerorpc = require("zerorpc");
fs = require("fs")
app = "cut_the_rope"
cmd = "cmd /c echo " + app+" called" 

//if client not running, run it,
//wait until file exists

pipeFile = "../data/pipe"
//fs.openSync(pipeFile, "r")
rpcPort = fs.readFileSync(pipeFile)
console.log(rpcPort);

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:"+rpcPort);
client.invoke("newApp", app,cmd, function(error, reply, streaming) {
    if(error){
        console.log("ERROR: ", error);
    } else {
		console.log("rpc reply:"+ reply);
	}
});