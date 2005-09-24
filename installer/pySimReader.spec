a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'pySimReader.py'],
             pathex=['C:\\Programming\\Python\\pySimReader'])
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          name='pySimReader.exe',
          debug=0,
          strip=0,
          upx=0,
          console=0,
          icon='pySIM.ico')
