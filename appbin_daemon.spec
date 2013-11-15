# -*- mode: python -*-
a = Analysis(['src/appbin_daemon.py'],
             pathex=['D:\\DOCs\\PersonalProjects\\AppBin\\SyncingExp\\gitRepo'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='appbin_daemon.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='appbin.ico')
