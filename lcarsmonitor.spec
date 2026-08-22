# -*- mode: python ; coding: utf-8 -*-
# flake8: noqa
import glob
from PyInstaller.utils.hooks import collect_all
# execute with: pyinstaller --clean -y lcarsmonitor.spec

hiddenimports = []
datas = []
binaries = []

imgui_datas, imgui_binaries, imgui_modules = collect_all("imgui_bundle")
binaries += imgui_binaries
hiddenimports += imgui_modules

dependencies = ["keyring", "wmi", "libasvat", "lcarsmonitor"]
for pkg_name in dependencies:
    pkg_datas, pkg_binaries, pkg_modules = collect_all(pkg_name)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_modules

# Add all .py files from lcarsmonitor (including subfolders) to hiddenimports, since
# collect_all() apparently doesn't get everything.
for folder in ['lcarsmonitor/']:
    for pyfile in glob.glob(folder + '/**/*.py', recursive=True):
        mod = pyfile.replace('/', '.').replace('\\', '.').replace('.py', '')
        if mod.endswith('__init__'):
            mod = mod[:-9]  # remove .__init__
        hiddenimports.append(mod)

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
