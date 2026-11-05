import asyncio
from io import BytesIO
import json
import threading
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest

@pytest.mark.parametrize('path', ['/', '/api/bootstrap', '/api/queue', '/api/playstyles', '/api/history', '/api/runtime/status', '/api/runtime/logs'] + ['/api/settings/'+s for s in ('general','bot','debug','timers','webhook')])
def test_local_read_routes(client, headers, path):
    response = client.get(path, headers=headers)
    assert response.status_code == 200
    assert response.headers['X-Frame-Options'] == 'DENY'

def test_session_and_origin_protection(client, headers):
    assert client.get('/api/bootstrap').status_code == 403
    assert client.get('/api/bootstrap', headers={**headers,'Origin':'https://example.com'}).status_code == 403
    assert client.get('/', base_url='http://example.com').status_code == 403
    assert client.get('/api/bootstrap', headers={**headers,'Origin':'http://localhost'}).status_code == 200

def test_free_public_state_unchanged(client, headers):
    assert client.get('/api/bootstrap', headers=headers).json['auth'] == {'required':False,'authenticated':True,'premium':False}

def test_queue_crud_and_persistence(client, headers, application):
    for name in ('shelly','colt'):
        assert client.post('/api/queue',json={'brawler':name,'push_until':1000},headers=headers).status_code == 200
    assert len(client.get('/api/queue',headers=headers).json['items']) == 2
    assert client.put('/api/queue/shelly',json={'push_until':1100},headers=headers).status_code == 200
    assert client.post('/api/queue/reorder',json={'order':['colt','shelly']},headers=headers).json['items'][0]['brawler']=='colt'
    import utils
    assert len(json.loads(utils.resolve_project_path('latest_brawler_data.json').read_text()))==2
    assert client.delete('/api/queue/colt',headers=headers).status_code==200
    assert len(client.delete('/api/queue',headers=headers).json['items'])==0

def test_duplicate_order_rejected(client, headers):
    client.post('/api/queue',json={'brawler':'shelly'},headers=headers)
    response=client.post('/api/queue/reorder',json={'order':['shelly','shelly']},headers=headers)
    assert response.status_code==400
    assert len(client.get('/api/queue',headers=headers).json['items'])==1

@pytest.mark.parametrize('payload',[['wrong'], 'wrong', 5])
def test_invalid_json_shape_is_client_error(client,headers,payload):
    assert client.post('/api/queue',json=payload,headers=headers).status_code==400

def test_malformed_json_is_client_error(client,headers):
    assert client.post('/api/queue',data='{bad',content_type='application/json',headers=headers).status_code==400

def test_storage_failure_does_not_report_success(application,monkeypatch):
    import webui.services as services
    data=application.config['data_service']
    def fail(*a,**k):raise OSError('simulated disk failure')
    monkeypatch.setattr(services,'save_brawler_data',fail)
    with pytest.raises(OSError):data.save_queue_data([{'brawler':'shelly'}])
    assert data.get_queue_data()==[]

def test_failed_serialization_preserves_file(application):
    import utils
    utils.save_brawler_data([{'brawler':'shelly'}])
    before=utils.resolve_project_path('latest_brawler_data.json').read_bytes()
    with pytest.raises(TypeError):utils.save_brawler_data([{'invalid':object()}])
    assert utils.resolve_project_path('latest_brawler_data.json').read_bytes()==before

@pytest.mark.parametrize('section,updates',[('general',{'max_fps':0}),('general',{'used_threads':-2}),('general',{'emulator_port':70000}),('bot',{'wall_detection_confidence':2}),('timers',{'state_check':-1}),('debug',{'debug_view_fps':0}),('bot',{'minimum_movement_delay':float('nan')})])
def test_invalid_settings_are_rejected(client,headers,section,updates):
    assert client.put('/api/settings/'+section,json=updates,headers=headers).status_code==400

@pytest.mark.parametrize('section',['general','bot','timers','debug','webhook'])
def test_settings_roundtrip_reset(client,headers,section):
    original=client.get('/api/settings/'+section,headers=headers).json
    if section=='general':
        assert client.put('/api/settings/general',json={'run_for_minutes':12},headers=headers).json['run_for_minutes']==12
    assert client.post('/api/settings/'+section+'/reset',json={},headers=headers).status_code==200

def test_secret_mask_preserve_and_clear(client,headers):
    result=client.put('/api/settings/webhook',json={'discord_bot_token':'audit-dummy-not-a-real-token'},headers=headers)
    assert b'audit-dummy-not-a-real-token' not in result.data
    client.put('/api/settings/webhook',json={'discord_bot_token':''},headers=headers)
    import utils
    assert utils.load_toml_as_dict('cfg/webhook_config.toml')['discord_bot_token']=='audit-dummy-not-a-real-token'
    client.put('/api/settings/webhook',json={'_clear_secrets':['discord_bot_token']},headers=headers)
    assert utils.load_toml_as_dict('cfg/webhook_config.toml')['discord_bot_token']==''

def test_playstyle_import_activate_delete(client,headers):
    content=b'{"name":"Audit","author":"Local test"}\n\ndef play(self):\n    return None\n'
    response=client.post('/api/playstyles/import',data={'file':(BytesIO(content),'audit.pyla')},headers=headers)
    assert response.status_code==200
    assert client.put('/api/playstyles/active',json={'filename':'audit.pyla'},headers=headers).status_code==200
    assert client.delete('/api/playstyles/audit.pyla',headers=headers).status_code==400
    assert client.put('/api/playstyles/active',json={'filename':'default_up.pyla'},headers=headers).status_code==200
    assert client.delete('/api/playstyles/audit.pyla',headers=headers).status_code==200
    assert client.put('/api/playstyles/active',json={'filename':'../utils.py'},headers=headers).status_code==400

@pytest.mark.parametrize('metadata',[[],['invalid'],'invalid',{'name':3},{'brawlers':None}])
def test_invalid_playstyle_cannot_break_bootstrap(client,headers,metadata):
    content=(json.dumps(metadata)+'\n\ndef play(self):\n    return None\n').encode()
    response=client.post('/api/playstyles/import',data={'file':(BytesIO(content),'invalid.pyla')},headers=headers)
    assert response.status_code==400
    assert client.get('/api/bootstrap',headers=headers).status_code==200

def test_empty_playstyle_rejected(client,headers):
    content=b'{"name":"Empty"}\n'
    assert client.post('/api/playstyles/import',data={'file':(BytesIO(content),'empty.pyla')},headers=headers).status_code==400

@pytest.mark.parametrize('query',['?start_date=wrong','?start_date=2026-11-05&end_date=2026-11-04'])
def test_invalid_history_dates(client,headers,query):
    assert client.get('/api/history'+query,headers=headers).status_code==400

def test_empty_queue_start_and_stop(client,headers):
    assert client.post('/api/runtime/start',headers=headers).json['code']=='EMPTY_QUEUE'
    assert client.post('/api/runtime/pause',headers=headers).status_code==409
    assert client.post('/api/runtime/stop',headers=headers).json['ok'] is True

def test_discord_requires_explicit_authorized_user(application,monkeypatch):
    bot=application.config['discord_bot']
    monkeypatch.setattr(bot,'get_authorized_user_id',lambda:None)
    interaction=SimpleNamespace(user=SimpleNamespace(id=123),response=SimpleNamespace(send_message=AsyncMock()))
    assert asyncio.run(bot.require_authorized_user(interaction)) is False
    interaction.response.send_message.assert_awaited_once()

def test_runtime_lifecycle_with_simulated_worker():
    from webui.runtime import RuntimeManager
    started=threading.Event()
    def worker(discord_bot,queue_data,runtime_control):
        started.set()
        while not runtime_control.should_stop():time.sleep(.01)
    manager=RuntimeManager(worker)
    manager.configure_start_gate(lambda:[{'brawler':'shelly'}],lambda:{'required':False})
    assert manager.start_current_queue(None)['ok']
    assert started.wait(2)
    assert manager.get_status()['is_running']
    assert manager.pause()['ok']
    assert manager.stop()['ok']
    end=time.monotonic()+2
    while manager.get_status()['is_running'] and time.monotonic()<end:time.sleep(.01)
    assert manager.get_status()['state']=='idle'
