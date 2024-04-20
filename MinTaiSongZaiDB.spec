# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

SETUP_DIR = 'C:\\MyProject\\MinTaiSongZai\\'

a = Analysis(['MinTaiSongZaiDB.py',
              'CreateDB.py',
              'PDFWidget.py',
              'SongListWidget.py',
              'AdminAddItemWidget.py',
              'SongListAdminWidget.py',
              'C:\\MyProject\\MinTaiSongZai\\RES\\imq_rc.py',
              'C:\\MyProject\\MinTaiSongZai\\UI\\UI_ReadPDF.py',
              'C:\\MyProject\\MinTaiSongZai\\UI\\UI_SongListWidget.py',
              'C:\\MyProject\\MinTaiSongZai\\UI\\UI_SongZaiMainWin.py',
              'C:\\MyProject\\MinTaiSongZai\\UI\\Ui_AdminAddItemWidget.py',
              'C:\\MyProject\\MinTaiSongZai\\UI\\UI_SongListAdminWidget.py',
              ],
             pathex=['C:\\MyProject\\MinTaiSongZai'],
             binaries=[],
             datas=[(SETUP_DIR+'DB\\','DB\\')],
             hiddenimports=['PyQt5','sys','sys','tempfile','threading','queue','fitz','os','win32api','win32print','sqlite3','hashlib'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='两岸稀有古本歌仔册数据库',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='两岸稀有古本歌仔册数据库')
