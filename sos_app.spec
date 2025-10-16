# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

def get_datas():
    base = os.path.abspath(".")
    return [
        ("_validation", "_validation"),
        ("src", "src"),
        ("assets", "assets"),
    ]

a = Analysis(
    ['sos_boot.py'],
    pathex=['.'],
    binaries=[],
    datas=get_datas(),
    hiddenimports=['src.orchestrator.app', 'src.asr.app', 'src.tts.app'],
    hookspath=[],
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
    name='SOS_Button_App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='assets/sos_icon.ico',
)*** End Patch
