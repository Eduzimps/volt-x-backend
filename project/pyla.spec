# Native Windows PyInstaller build. Resources remain beside internal/.
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

root = Path(SPECPATH)
datas = [(str(root/'scrcpy/scrcpy-server.jar'), 'scrcpy')]
binaries = []
hidden = ['webview', 'webview.platforms.edgechromium', 'webui.app', 'webui.runtime', 'webui.services']
for package in ('onnxruntime', 'adbutils', 'av'):
    package_datas, package_binaries, package_hidden = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hidden += package_hidden
a = Analysis([str(root/'main.py')], pathex=[str(root)], binaries=binaries,
             datas=datas, hiddenimports=hidden, hookspath=[], hooksconfig={},
             runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='pyla_main',
          debug=False, strip=False, upx=False, console=True,
          icon=str(root/'images/logo.ico'))
collection = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='pyla-internal')
