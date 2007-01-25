a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'pySimReader.py'],
             pathex=['C:\\Programming\\Python\\pySimReader2'])
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          name='pySimReader.exe',
          debug=False,
          strip=False,
          upx=False,
          console=False , icon='pySIM.ico')
