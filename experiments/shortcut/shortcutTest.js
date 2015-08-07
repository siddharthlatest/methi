

var createShortcuts = function (app,shortcutName,description){
	cmd = process.env.windir+"/system32/cscript.exe";// don not change
	newShortcut = "NewShortcut.vbs" //vbs file for new shortcut (full path needed)
	pinItem = "PinItem.vbs" //vbs file to pin items(full path needed)
	var spawn = require('child_process').spawn;
	
	temp = process.env.TMP + "\\" + shortcutName + ".lnk"
	startMenu= process.env.USERPROFILE + "\\Start Menu\\Programs" +"\\" + shortcutName + ".lnk"
	console.log(startMenu)
	
	spawn(cmd, [newShortcut,app,temp,description],{ detached: true} );
	spawn(cmd, [newShortcut,app,startMenu,description],{ detached: true} );
	spawn(cmd, [pinItem,"/item:"+temp,"/taskbar"],{ detached: true} );
	
	
	
}

createShortcuts("cut_the_rope","Cut the ROpe","it rocks")
