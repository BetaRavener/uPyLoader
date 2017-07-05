# -*- mode: python -*-

block_cipher = None

import os
import ntpath
import PyQt5
import serial

a = Analysis(['main.py'],
             pathex=['C:\\Users\\celtofj\\My Documents\\github\\uPyLoader', os.path.join(ntpath.dirname(PyQt5.__file__), 'Qt', 'bin')],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='uPyLoader',
          debug=False,
          strip=False,
          upx=False,
          console=False )

