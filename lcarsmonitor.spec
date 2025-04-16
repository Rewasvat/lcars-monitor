# -*- mode: python ; coding: utf-8 -*-
# flake8: noqa
from PyInstaller.utils.hooks import collect_all
# execute with: pyinstaller --clean -y lcarsmonitor.spec

hiddenimports = []
datas = []
binaries = []

imgui_datas, imgui_binaries, imgui_modules = collect_all("imgui_bundle")
binaries += imgui_binaries
hiddenimports += imgui_modules

lcars_datas, lcars_binaries, lcars_modules = collect_all("lcarsmonitor")
datas += lcars_datas
binaries += lcars_binaries
hiddenimports += lcars_modules

a = Analysis(  # type: ignore
    ['lcarsmonitor\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)  # type: ignore

exe = EXE(  # type: ignore
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='lcarsmonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    one_file=True,
    icon=['lcarsmonitor\\assets\\app_settings\\icon.png'],
)
