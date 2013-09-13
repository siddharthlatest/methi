from distutils.core import setup
import py2exe
import os
from glob import glob
import sys

sys.path.append("C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\redist\\x86\\Microsoft.VC90.CRT")
py2exe_options = dict(
                    ascii= 1,
                    bundle_files=1,
				    compressed=1,
					optimize=2,
                    #includes=['_scproxy', '_sysconfigdata'], 
					excludes=['optparse','doctest','pickle','calendar','pdb','inspect','bz2'],
					dll_excludes=['API-MS-Win-Core-Interlocked-L1-1-0.dll','mswsock.dll','powrprof.dll','w9xpopen.exe','API-MS-Win-Core-DelayLoad-L1-1-0.dll','API-MS-Win-Core-ErrorHandling-L1-1-0.dll','API-MS-Win-Core-File-L1-1-0.dll','API-MS-Win-Core-Handle-L1-1-0.dll','API-MS-Win-Core-Heap-L1-1-0.dll','API-MS-Win-Core-IO-L1-1-0.dll','API-MS-Win-Core-LibraryLoader-L1-1-0.dll','API-MS-Win-Core-LocalRegistry-L1-1-0.dll','API-MS-Win-Core-Misc-L1-1-0.dll','API-MS-Win-Core-ProcessThreads-L1-1-0.dll','API-MS-Win-Core-Profile-L1-1-0.dll','API-MS-Win-Core-String-L1-1-0.dll','API-MS-Win-Core-Synch-L1-1-0.dll','API-MS-Win-Core-SysInfo-L1-1-0.dll','api-ms-win-core-threadpool-legacy-l1-1-0.dll','API-MS-Win-Security-Base-L1-1-0.dll'],
                    dist_dir="../dist"
					)

setup(
      
    console = [{
                "version" : "0.01",
                "script": "appbin_daemon.py",    
                "icon_resources": [(0, "appbin.ico")],
                "description" : "Appbin sync daemon",
                "name" : "Appbin sync daemon",
                'comments': 'This daemon handles syncing and updating of apps.',
                'copyright': '(C) Appbin, 2013',
                'company_name': "Appbin Labs Pvt. Ltd.",
        }],
	options={'py2exe':py2exe_options},
    #data_files=[("config",["config\\appDirs.ini","config\\config.ini"]),("bin",["bin\\7za.exe"]),				],
	zipfile=None
	)
