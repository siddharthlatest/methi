
cmd = process.env.windir+"/system32/cscript.exe";
console.log("cmd is "+ cmd);
arg0 = "shortcut.vbs"
arg1 = "angrybirds";
arg2 = "AngryBirds";
arg3 = "yo";


var spawn = require('child_process').spawn,
ls = spawn(cmd, [arg0,arg1,arg2,arg3],{ detached: true} );

ls.on('close', function (code) {
  console.log('Icon Created' + code);
});									