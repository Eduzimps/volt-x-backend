"""Preserve the original distribution, replacing only its verified executable."""
import hashlib
from pathlib import Path
import sys
import zipfile

original, executable, destination = map(Path, sys.argv[1:])
exe = executable.read_bytes()
expected = '17c4d88095794f162578969d698dab674facae553331dea64b3ed6507f1be4ee'
if hashlib.sha256(exe).hexdigest() != expected:
    raise SystemExit('Executable checksum mismatch')
with zipfile.ZipFile(original) as source:
    if source.testzip() is not None:
        raise SystemExit('Original ZIP integrity check failed')
    if source.namelist().count('internal/pyla_main.exe') != 1:
        raise SystemExit('Unexpected distribution structure')
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as output:
        for entry in source.infolist():
            data = exe if entry.filename == 'internal/pyla_main.exe' else source.read(entry)
            output.writestr(entry, data)
        output.writestr('LEIA-ME-RECONSTRUCAO.txt',
            'Extraia o ZIP inteiro no Windows e execute start.bat. '
            'Mantenha todas as pastas. O executavel foi reconstruido de fontes verificadas; '
            'a execucao no Windows ainda nao foi testada. '
            'Nao foram adicionados recursos nem removidas verificacoes de acesso. '
            'Codigo original: https://github.com/PylaAI/PylaAI (CC BY-NC 4.0).\n')
with zipfile.ZipFile(destination) as output, zipfile.ZipFile(original) as source:
    assert output.testzip() is None
    assert len(output.infolist()) == len(source.infolist()) + 1
    for entry in source.infolist():
        assert output.read(entry.filename) == (exe if entry.filename == 'internal/pyla_main.exe' else source.read(entry.filename))
print(f'Complete ZIP validated: {destination} ({destination.stat().st_size} bytes)')
