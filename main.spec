# -*- mode: python -*-

block_cipher = None

import os
import sys
import datetime
import ntpath
import PyQt5
import serial

# Add working dir to path so we can use uPyLoader modules here
sys.path += [os.getcwd()]
from src.utility.build_info import BuildInfo

BuildInfo().save("build_info.json")

a = Analysis(['main.py'],
             pathex=[os.path.join(ntpath.dirname(PyQt5.__file__), 'Qt', 'bin')],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
# From, To, What
a.datas += [('icons//main.png','icons//main.png','DATA'),
            ('icons//main-512.png','icons//main-512.png','DATA'),
            ('icons//floppy.png','icons//floppy.png','DATA'),
            ('icons//refresh.png','icons//refresh.png','DATA'),
            ('icons//run.png','icons//run.png','DATA'),
            ('mcu//download.py','mcu//download.py','DATA'),
            ('mcu//upload.py','mcu//upload.py','DATA'),
            (BuildInfo.pyinstaller_path,'build_info.json','DATA')]
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
          console=False,
          icon='icons//main.ico' )

app = BUNDLE(exe,
             name='uPyLoader.app',
             icon='icons//main-512.icns',
             bundle_identifier=None)
