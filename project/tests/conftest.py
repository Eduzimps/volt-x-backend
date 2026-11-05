import shutil
import os
import sys
from pathlib import Path
import pytest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

@pytest.fixture
def application(tmp_path, monkeypatch):
    import utils
    from webui import create_app
    for name in ('cfg', 'playstyles'):
        shutil.copytree(PROJECT/name, tmp_path/name)
    shutil.copy2(PROJECT/'main.py', tmp_path/'main.py')
    for name in ('templates', 'static', 'images', 'api'):
        if os.name == 'nt':
            shutil.copytree(PROJECT/name, tmp_path/name)
        else:
            (tmp_path/name).symlink_to(PROJECT/name, target_is_directory=True)
    monkeypatch.setattr(utils, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(utils, 'brawlers_info_file_path', tmp_path/'cfg/brawlers_info.json')
    utils.cached_toml.clear()
    app = create_app(lambda *args, **kwargs: None, start_discord_bot=False)
    app.testing = True
    yield app
    utils.cached_toml.clear()

@pytest.fixture
def client(application):
    return application.test_client()

@pytest.fixture
def headers(application):
    return {'X-Pyla-UI-Token': application.config['UI_API_TOKEN']}
