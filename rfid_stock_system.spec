# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# customtkinter varlıklarını (temalar, görseller) topla
ctk_datas = collect_data_files('customtkinter')
darkdetect_datas = collect_data_files('darkdetect')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # customtkinter tema ve asset dosyaları
        *ctk_datas,
        *darkdetect_datas,
        # screens paketi
        ('screens', 'screens'),
    ],
    hiddenimports=[
        'customtkinter',
        'darkdetect',
        'packaging',
        'PIL',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        '_tkinter',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RFID Stock System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # Terminal penceresi açılmasın
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RFID Stock System',
)

app = BUNDLE(
    coll,
    name='RFID Stock System.app',
    icon='assets/icon.icns',
    bundle_identifier='com.erenekx.rfid-stock-system',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'RFID Stock System',
        'CFBundleDisplayName': 'RFID Stock System',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleIdentifier': 'com.erenekx.rfid-stock-system',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Dark mode desteği
        'LSMinimumSystemVersion': '10.14',
        'CFBundleDocumentTypes': [],
    },
)
