var fs = require('fs');
var iniReader = require('inireader');
var parser = new iniReader.IniReader();

module.exports = function(cfgF){
	var cfgFile = cfgF
	var dataPath = ''
	var email = ''
	
	var syncToFile = function(){
		fs.exists(cfgFile,function(exists){
			
			if(!exists){
				parser.load(cfgFile);
			}
			
			writeToFile();
		});
	}
	
	var writeToFile = function (){
		parser.param('main.email',email);
		parser.param('main.path',dataPath);
		parser.write(cfgFile);
	}
	
	return {
		var setConfigFile = function(cfgF){
			cfgFile = cfgF
			syncToFile()
		}
		
		var setDataPath= function(dpath){
			dataPath = dpath
			syncToFile()
		}
		
		var setEmail = function(mail){
			email = mail
			syncToFile()
		}
		
		var addApp = function(app){
		
		}
		
	}
}