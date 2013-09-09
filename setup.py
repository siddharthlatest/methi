from distutils.core import setup
import py2exe

#py2exe_options = dict(
					#compressed=True,
					#optimize=2,
					#excludes=['optparse','doctest','pickle','calendar']
#					)

setup(console=['appbin.py'],#	options={'py2exe':py2exe_options},
	data_files=[("config",["config\\appDirs.ini","config\\config.ini"]),
				("bin",["bin\\7za.exe"]),
				]
	)