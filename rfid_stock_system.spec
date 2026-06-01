# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# customtkinter ve darkdetect varlıklarını topla
ctk_datas = collect_data_files('customtkinter')
darkdetect_datas = collect_data_files('darkdetect')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # customtkinter tema ve asset dosyaları
        *ctk_datas,
        *darkdetect_datas,
        # screens paketi (tüm screen modülleri)
        ('screens', 'screens'),
        # App ikonu
        ('assets/icon.icns', 'assets'),
        ('assets/icon.png', 'assets'),
    ],
    hiddenimports=[
        'customtkinter',
        'darkdetect',
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        '_tkinter',
        'sqlite3',
        '_sqlite3',
        'hashlib',
        'datetime',
        'screens.login_screen',
        'screens.admin_dashboard',
        'screens.staff_inventory',
        'screens.rfid_scanner',
        'screens.medicine_form',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'test',
        'unittest',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RFID Stock System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # macOS'ta UPX sorun çıkarabilir
    console=False,      # Terminal penceresi açılmasın
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,   # Universal binary için 'universal2' yazılabilir
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
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
        'NSRequiresAquaSystemAppearance': False,   # Dark mode desteği
        'LSMinimumSystemVersion': '11.0',
        'CFBundleDocumentTypes': [],
        # Tkinter için gerekli
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        # Privacy — erişim izinleri gerekirse eklenebilir
        'NSHumanReadableCopyright': '© 2024 RFID Stock System',
    },
)
