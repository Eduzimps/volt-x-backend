"""Package the complete source tree, excluding environments and generated caches."""
from pathlib import Path
import sys
import zipfile

root=Path(__file__).resolve().parents[1]
destination=Path(sys.argv[1]).resolve()
destination.parent.mkdir(parents=True,exist_ok=True)
excluded={'.git','.venv','.venv-win','venv','__pycache__','.pytest_cache','build','dist','test-results','profiles'}
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        relative=path.relative_to(root)
        if not path.is_file() or any(p in excluded for p in relative.parts):continue
        if path.resolve()==destination or path.suffix in {'.pyc','.env'} or path.name in {'latest_brawler_data.json','player-data.json'} or path.name.startswith('.pyla-profile'):continue
        if path.suffix=='.log' and 'audit-evidence' not in relative.parts:continue
        archive.write(path,str(relative))
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
    for required in ('main.py','utils.py','webui/app.py','models/mainInGameModel.onnx','LICENSE','README-AUDITORIA.md','pyla.spec'):
        assert required in archive.namelist(),required
print(f'Complete source ZIP validated: {destination} ({destination.stat().st_size} bytes)')
