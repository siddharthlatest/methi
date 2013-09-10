from distutils.core import setup
import py2exe

py2exe_options = dict(
					compressed=1,
					optimize=2,
					excludes=['optparse','doctest','pickle','calendar','pdb','inspect','bz2'],
					dll_excludes=['API-MS-Win-Core-Interlocked-L1-1-0.dll','mswsock.dll','powrprof.dll','w9xpopen.exe','API-MS-Win-Core-DelayLoad-L1-1-0.dll','API-MS-Win-Core-ErrorHandling-L1-1-0.dll','API-MS-Win-Core-File-L1-1-0.dll','API-MS-Win-Core-Handle-L1-1-0.dll','API-MS-Win-Core-Heap-L1-1-0.dll','API-MS-Win-Core-IO-L1-1-0.dll','API-MS-Win-Core-LibraryLoader-L1-1-0.dll','API-MS-Win-Core-LocalRegistry-L1-1-0.dll','API-MS-Win-Core-Misc-L1-1-0.dll','API-MS-Win-Core-ProcessThreads-L1-1-0.dll','API-MS-Win-Core-Profile-L1-1-0.dll','API-MS-Win-Core-String-L1-1-0.dll','API-MS-Win-Core-Synch-L1-1-0.dll','API-MS-Win-Core-SysInfo-L1-1-0.dll','API-MS-Win-Core-ThreadPool-L1-1-0.dll','API-MS-Win-Security-Base-L1-1-0.dll']
					)

setup(windows=['Appbin.py'],
	options={'py2exe':py2exe_options},
	data_files=[("config",["config\\appDirs.ini","config\\config.ini"]),
				("bin",["bin\\7za.exe"]),
				],
	zipfile=None
	)