# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_data_files
import os

# Configurar las rutas de Tcl/Tk (actualiza con tus rutas reales)
tcl_dir = '/usr/lib/tcl8.6'
tk_dir = '/usr/lib/tk8.6'

a = Analysis(
    ['tu_archivo.py'],
    binaries=[],
    datas=[
        (os.path.join(tcl_dir, '*.tcl'), 'tcl'),
        (os.path.join(tk_dir, '*.tcl'), 'tk'),
        (os.path.join(tk_dir, '*.xbm'), 'tk')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EcualizadorTurbo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icono.ico'  # Opcional si tienes un icono
)